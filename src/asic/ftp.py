import contextlib
import datetime as dt
import ftplib
import functools
import io
import itertools
import logging
import pathlib
import ssl
from typing import Iterable, Type

import pydantic

from asic import ASIC_FILE_EXTENSION_MAP
from asic.files.definitions import SUPPORTED_FILE_CLASSES
from asic.files.file import AsicFile, FileKind

logger = logging.getLogger(__name__)


SSL_CONTEXT = ssl.create_default_context()

SUPPORTED_ASIC_EXTENSIONS = frozenset(ASIC_FILE_EXTENSION_MAP.keys())


class DownloadSpec(pydantic.BaseModel):
    remote: pathlib.PureWindowsPath
    local: pathlib.Path

    class Config:
        arbitrary_types_allowed = True


def get_ftps(
    ftps_host: str,
    ftps_user: str,
    ftps_password: pydantic.SecretStr,
    ftps_port: int,
    verbosity: int = 0,
):
    ftps = ftplib.FTP_TLS(
        encoding="Latin-1",
    )

    ftps.set_debuglevel(verbosity - 1)
    with contextlib.redirect_stdout(io.StringIO()) as f:
        ftps.connect(
            host=ftps_host,
            port=ftps_port,
        )
    for line in f.getvalue().splitlines():
        logger.debug(f"FTP: {line}")
    logger.info(f"Login to FTP '{ftps_host}' as '{ftps_user}'")

    with contextlib.redirect_stdout(io.StringIO()) as f:
        ftps.login(user=ftps_user, passwd=ftps_password.get_secret_value())
    for line in f.getvalue().splitlines():
        logger.debug(f"FTP: {line}")

    with contextlib.redirect_stdout(io.StringIO()) as f:
        # Explicitly secure the connection
        ftps.prot_p()

    for line in f.getvalue().splitlines():
        logger.debug(f"FTP: {line}")
    ftps.set_debuglevel(0)
    return ftps


def grab_file(ftp: ftplib.FTP, remote: pathlib.PurePath, local: pathlib.Path):
    with open(local, "wb") as dst:
        try:
            ftp.retrbinary("RETR " + str(remote), dst.write)
        except ftplib.error_reply:
            logger.exception(f"Failed to download file '{str(remote)}'")


def grab_files(ftp: ftplib.FTP, files: Iterable[DownloadSpec]) -> None:
    for i in files:
        grab_file(ftp, i.remote, i.local)


def get_path_version(path: pathlib.PurePath) -> str:
    version = ASIC_FILE_EXTENSION_MAP[path.suffix.lower()].normalized_version
    return version


@functools.cache
def list_paths_in_location(
    ftp: ftplib.FTP,
    location: str,
) -> list[pathlib.PureWindowsPath]:
    ftp.cwd(location)
    location_path = pathlib.PureWindowsPath(location)
    logger.debug(f"Listing files in location {location}")
    files_in_location = ftp.nlst()
    logger.debug(f"Total files found in location {len(files_in_location)}")
    paths_in_location = [location_path / f for f in files_in_location]
    logger.debug(f"Total paths found in location {len(paths_in_location)}")
    return paths_in_location


def fiter_files_by_date_range(
    file_list: list[AsicFile],
    since: dt.date,
    until: dt.date,
) -> list[AsicFile]:
    filtered: list[AsicFile] = []
    for f in file_list:
        f_day = f.day if f.day is not None else 1
        f_date = dt.date(f.year, f.month, f_day)
        if since <= f_date <= until:
            filtered.append(f)

    return filtered


def fiter_files_by_extension(
    file_list: list[AsicFile],
    extension: str,
) -> list[AsicFile]:
    filtered: list[AsicFile] = [
        f for f in file_list if f.extension == extension or f.extension is None
    ]
    return filtered


def list_supported_files(
    ftp: ftplib.FTP,
    *,
    agent: str | None = None,
    months: list[dt.date],
    extensions: list[str],
    kinds: list[str],
    locations: list[str],
) -> list[AsicFile]:
    logger.info("Listing files")
    file_list = []
    for month, l_template, ext in itertools.product(
        months,
        locations,
        extensions,
    ):
        try:
            remote_location = l_template.format(
                location_year=month.year,
                location_month=month.month,
                location_agent=agent,
            )
        except Exception:
            logger.warning(
                f"Failed to build remote location with {l_template}, {month, agent}"
            )
            continue
        logger.debug(f"Listing remote location: {remote_location}")
        files_in_location = list_supported_files_in_location(
            ftp, remote_location, month, kinds, ext
        )
        file_list.extend(files_in_location)

    return file_list


def path_to_asic_file(
    path: pathlib.PureWindowsPath, asic_file_class: Type[AsicFile]
) -> AsicFile:
    file = asic_file_class.from_remote_path(path)
    return file


def cast_into_kinds(
    paths: list[pathlib.PureWindowsPath], kinds: dict[FileKind, Type[AsicFile]]
) -> list[AsicFile]:
    file_list: list[AsicFile] = []
    for p in paths:
        for k, c in kinds.items():
            logger.debug(f"Trying kind '{k}' for {p}")
            try:
                file = path_to_asic_file(p, c)
                logger.debug(f"Found kind '{k}' for {p}")
                file_list.append(file)
                break
            except ValueError:
                logger.debug(f"Failed kind '{k}' for {p}")
                continue
        else:
            logger.debug(f"Failed to match a kind to {p} in {kinds.keys()}")
    return file_list


def list_supported_files_in_location(
    ftp: ftplib.FTP,
    location: str,
    month: dt.date,
    kinds: list[str],
    extension: str,
) -> list[AsicFile]:
    remote_paths = list_paths_in_location(ftp, location)
    logger.debug(f"Total files in location {len(remote_paths)}")
    asic_file_kinds_requested = {
        k: c for k, c in SUPPORTED_FILE_CLASSES.items() if k in kinds
    }
    logger.debug(f"Checking for {len(asic_file_kinds_requested)} kinds")
    remote_files = cast_into_kinds(remote_paths, asic_file_kinds_requested)
    logger.debug(f"Kept {len(remote_files)} AsicFiles by kind")

    since = month
    until = (month.replace(day=1) + dt.timedelta(days=31)).replace(
        day=1
    ) - dt.timedelta(days=1)

    remote_files = fiter_files_by_date_range(remote_files, since, until)
    logger.debug(f"Kept {len(remote_files)} AsicFiles by date filter")

    if extension is not None:
        logger.debug(f"Filtering by ex {len(remote_files)} files")
        remote_files = fiter_files_by_extension(remote_files, extension)
        logger.debug(f"Kept {len(remote_files)} AsicFiles by date filter")

    logger.debug(f"Total files kept {len(remote_files)}")
    return remote_files


def combine_patterns_and_extension(pattern: str, extension: str) -> str:
    logger.info(f"Preparing search pattern with file extension '{extension}'")
    aux_p = pattern.split(".")
    pattern_ext = "".join(
        ["[" + a.lower() + a.upper() + "]{1}" for a in extension if a != "."]
    )
    logger.debug(f"Search pattern without extension: {pattern}")
    pattern = aux_p[0] + f".(?P<ext>{pattern_ext})"
    logger.debug(f"Search pattern with extension: {pattern}")

    return pattern


if __name__ == "__main__":
    # Mes del que se va a descargar
    # dt_format = r"%Y-%m-%d"
    # beg_month = dt.dt.datetime.strptime("2019-03-01", dt_format)  # input beg_month date
    # end_month = dt.dt.datetime.strptime("2019-07-01", dt_format)  # input end_month date
    # file_code = "adem"

    import os

    location = pathlib.PureWindowsPath("/UsuariosK/ENBC/Sic/COMERCIA/2022-07/")
    with ftplib.FTP(
        host=os.environ["ASIC_FTP_HOST"],
        user=os.environ["ASIC_FTP_USER"],
        passwd=os.environ["ASIC_FTP_PASSWORD"],
    ) as ftp_aux:
        files = list_paths_in_location(ftp_aux, str(location))
        for f in files:
            print(f)
