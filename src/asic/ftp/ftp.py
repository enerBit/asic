import datetime as dt
import ftplib
import functools
import itertools
import logging
import pathlib
import re
from typing import Iterable

import pydantic
from asic import ASIC_FILE_CONFIG, ASIC_FILE_EXTENSION_MAP

logger = logging.getLogger(__name__)

SUPPORTED_ASIC_EXTENSIONS = frozenset(ASIC_FILE_EXTENSION_MAP.keys())


class DownloadSpec(pydantic.BaseModel):
    remote: pathlib.PurePosixPath
    local: pathlib.Path

    class Config:
        arbitrary_types_allowed = True


def grab_file(ftp: ftplib.FTP, remote: pathlib.PurePath, local: pathlib.Path):
    with open(local, "wb") as dst:
        ftp.retrbinary("RETR " + str(remote), dst.write)


def grab_files(ftp: ftplib.FTP, files: Iterable[DownloadSpec]) -> None:
    for i in files:
        grab_file(ftp, i.remote, i.local)


def get_path_version(path: pathlib.PurePath) -> str:
    version = ASIC_FILE_EXTENSION_MAP[path.suffix.lower()].normalized_version
    return version


@functools.cache
def list_files_in_location(
    ftp: ftplib.FTP,
    location: str,
) -> list[pathlib.PurePath]:
    ftp.cwd(location)
    location_path = pathlib.PurePath(location)
    logger.debug(f"Listing files in location {location}")
    files_in_location = ftp.nlst()
    logger.debug(f"Total files found in location {len(files_in_location)}")
    paths_in_location = [location_path / f for f in files_in_location]
    logger.debug(f"Total paths found in location {len(paths_in_location)}")
    return paths_in_location


def fiter_files_by_pattern(
    file_list: list[pathlib.PurePath], name_pattern: str
) -> list[pathlib.PurePath]:
    filtered = [f for f in file_list if re.search(name_pattern, str(f.name))]
    return filtered


def list_supported_files(
    ftp: ftplib.FTP,
    *,
    agent: str | None = None,
    months: list[dt.date],
    extensions: list[str],
    files: list[str],
    locations: list[str],
) -> list[pathlib.PurePath]:
    file_list = []
    for month, l_template, ext in itertools.product(
        months,
        locations,
        extensions,
    ):
        try:
            remote_location = l_template.format(
                year=month.year, month=month.month, agent=agent
            )
        except Exception:
            logger.debug(
                f"Failed to build remote location with {l_template}, {month, agent}"
            )
            continue
        logger.debug(f"Listing remote location: {remote_location}")
        file_list.extend(
            list_supported_files_in_location(ftp, remote_location, files, ext)
        )

    return file_list


def list_supported_files_in_location(
    ftp: ftplib.FTP,
    location: str,
    file_codes: list[str],
    extension: str,
) -> list[pathlib.PurePath]:
    files = list_files_in_location(ftp, location)
    logger.debug(f"Total files in location {location}")

    patterns = [c.name_pattern for f, c in ASIC_FILE_CONFIG.items() if f in file_codes]

    if extension is not None:
        patterns = [combine_patterns_and_extension(p, extension) for p in patterns]

    logger.debug(f"Patterns to filter by: {patterns}")

    supported_files_in_location = []
    for p in patterns:
        logger.debug(f"Filtering {len(files)} by pattern {p}")
        new_files = fiter_files_by_pattern(files, p)
        logger.debug(f"Kept {len(new_files)} files")
        supported_files_in_location.extend(new_files)
    logger.info(f"Total files kept {len(supported_files_in_location)}")
    return supported_files_in_location


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

    location = pathlib.PurePosixPath("/UsuariosK/ENBC/Sic/COMERCIA/2022-07/")
    with ftplib.FTP(
        host=os.environ["ASIC_FTP_HOST"],
        user=os.environ["ASIC_FTP_USER"],
        passwd=os.environ["ASIC_FTP_PASSWORD"],
    ) as ftp_aux:
        files = list_files_in_location(ftp_aux, str(location))
        for f in files:
            print(f)
