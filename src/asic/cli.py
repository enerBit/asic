import datetime as dt
import ftplib
import logging
import os
import pathlib
from ssl import SSLZeroReturnError
from typing import Optional

import typer
from rich.progress import track

from asic import ASIC_FILE_EXTENSION_MAP
from asic.files import SupportedFiles
from asic.ftp.ftp import grab_file  # list_supported_files_in_location,
from asic.ftp.ftp import list_supported_files
from asic.publication import list_latest_published_versions

logger = logging.getLogger("eds")
logger.addHandler(logging.StreamHandler())

YEAR_MONTH_FORMATS = ["%Y-%m", "%Y%m"]
YEAR_MONTH_MATCH_ERROR_MESSAGE = f"Must match one of: {YEAR_MONTH_FORMATS}"
SUPPORTED_FILES = sorted([f.value.lower() for f in SupportedFiles])
SUPPORTED_FILES_ERROR_MESSAGE = f"Must match one of: {SUPPORTED_FILES}"
SUPPORTED_EXTENSIONS = [e.lower() for e in ASIC_FILE_EXTENSION_MAP.keys()]
SUPPORTED_EXTENSIONS_ERROR_MESSAGE = f"Must match one of: {SUPPORTED_EXTENSIONS}"
PUBLIC_SEARCHEABLE_LOCATIONS = [
    r"/INFORMACION_XM/PUBLICOK/SIC/COMERCIA/{year:04d}-{month:02d}/",
]
PRIVATE_SEARCHEABLE_LOCATIONS = [
    r"/UsuariosK/{agent}/Sic/COMERCIA/{year:04d}-{month:02d}/",
]


cli = typer.Typer(no_args_is_help=True)


@cli.callback()
def main(verbosity: int = typer.Option(0, "--verbosity", "-v", count=True)):
    logger.info(f"Verbosity level {verbosity}")
    match verbosity:
        case 0:
            logger.setLevel(logging.FATAL)
        case 1:
            logger.setLevel(logging.ERROR)
        case 2:
            logger.setLevel(logging.WARNING)
        case 3:
            logger.setLevel(logging.INFO)
        case 4:
            logger.setLevel(logging.DEBUG)
        case _:
            logger.setLevel(logging.DEBUG)


def get_ftps(
    ftps_host: str,
    ftps_user: str,
    ftps_password: str,
    ftps_port: int,
):
    ftps = ftplib.FTP_TLS(
        host=ftps_host,
        encoding="Latin-1",
        # timeout=10,
    )

    ftps.connect(
        port=ftps_port,
    )

    ftps.login(user=ftps_user, passwd=ftps_password)

    ftps.prot_p()

    return ftps


def parse_month(month: str) -> dt.date:
    for f in YEAR_MONTH_FORMATS:
        try:
            value = dt.datetime.strptime(month, f).date()
            break
        except ValueError:
            continue
    else:
        raise typer.BadParameter(YEAR_MONTH_MATCH_ERROR_MESSAGE)

    return value


def validate_file(file_code: str) -> str:
    if not file_code.lower() in SUPPORTED_FILES:
        raise typer.BadParameter(SUPPORTED_FILES_ERROR_MESSAGE)
    return file_code


def validate_version(version: str) -> str:
    if not version.lower() in SUPPORTED_EXTENSIONS:
        raise typer.BadParameter(SUPPORTED_EXTENSIONS_ERROR_MESSAGE)
    return version


def months_callback(values: list[str]) -> list[dt.date]:
    months = sorted(list(set([parse_month(v) for v in values])), reverse=True)
    return months


def files_callback(values: list[str]) -> list[str]:
    files = sorted(
        list(set([validate_file(v) for v in values])),
        reverse=True,
    )

    return files


def extensions_callback(values: list[str]) -> list[str]:
    extensions = list(set([validate_version(v) for v in values]))

    return extensions


@cli.command()
def pubs(
    days_old: int = typer.Option(None),
    after: dt.datetime = typer.Option(None),
    include_daily: bool = typer.Option(False),
):
    """
    Check latest published settlements in asic's website.
    """
    message = "Listing latest published settlements by ASIC"
    if days_old is not None:
        message = message + f" in the last {days_old} days"
        published_after = dt.datetime.combine(
            dt.date.today(), dt.datetime.min.time()
        ) + dt.timedelta(days=-days_old)
    elif after is not None:
        message = message + f" afte {after}"
        published_after = after
    else:
        published_after = None
    logger.info(message)
    latest_publications = list_latest_published_versions(published_after, include_daily)
    for pub in latest_publications:
        typer.echo(
            f"{pub.month:%Y-%m}:{pub.version.upper()} -- published: {pub.published_at:%Y-%m-%d}"
        )


@cli.command("list")
def list_files(
    months: list[str] = typer.Option(
        ...,
        "--month",
        callback=months_callback,
        help=YEAR_MONTH_MATCH_ERROR_MESSAGE,
    ),
    agent: Optional[str] = typer.Option(
        None, help="Agent's asic code, required for private files"
    ),
    files: Optional[list[str]] = typer.Option(
        None, "--file", callback=files_callback, help=SUPPORTED_FILES_ERROR_MESSAGE
    ),
    extensions: Optional[list[str]] = typer.Option(
        None,
        "--version",
        callback=extensions_callback,
        help=SUPPORTED_EXTENSIONS_ERROR_MESSAGE,
    ),
    ftps_host: str = typer.Argument(
        default="xmftps.xm.com.co", envvar="ASIC_FTPS_HOST"
    ),
    ftps_user: str = typer.Argument(..., envvar="ASIC_FTPS_USER"),
    ftps_password: str = typer.Argument(..., envvar="ASIC_FTPS_PASSWORD"),
    ftps_port: int = typer.Argument(default=210, envvar="ASIC_FTPS_PORT"),
    # asic_raw_container_name: str = typer.Argument(
    #     "asic-raw", envvar="ASIC_RAW_CONTAINER_NAME"
    # ),
    # asic_processed_container_name: str = typer.Argument(
    #     "asic", envvar="ASIC_PROCESSED_CONTAINER_NAME"
    # ),
):
    """
    List files from asic's ftp server.

    FTP authentication info should be  provided as environment variables (ASIC_FTP_*)
    """
    logger.info(
        "Listing files for"
        f" agent: {agent}"
        f" months: {months}"
        f" extensions: {extensions}"
        f" files: {files}"
    )
    if not extensions:
        extensions = [None]
    if not files:
        files = SUPPORTED_FILES

    locations = PUBLIC_SEARCHEABLE_LOCATIONS
    if agent is not None:
        locations.extend(PRIVATE_SEARCHEABLE_LOCATIONS)

    ftps = get_ftps(
        ftps_host=ftps_host,
        ftps_user=ftps_user,
        ftps_password=ftps_password,
        ftps_port=ftps_port,
    )

    file_list = list_supported_files(
        ftps,
        agent=agent,
        months=months,
        extensions=extensions,
        files=files,
        locations=locations,
    )

    ftps.quit()

    for f in file_list:
        typer.echo(f)


@cli.command()
def download(
    months: list[str] = typer.Option(
        ...,
        "--month",
        callback=months_callback,
        help=YEAR_MONTH_MATCH_ERROR_MESSAGE,
    ),
    agent: Optional[str] = typer.Option(
        None, help="Agent's asic code, required for private files"
    ),
    files: Optional[list[str]] = typer.Option(
        None, "--file", callback=files_callback, help=SUPPORTED_FILES_ERROR_MESSAGE
    ),
    extensions: Optional[list[str]] = typer.Option(
        None,
        "--version",
        callback=extensions_callback,
        help=SUPPORTED_EXTENSIONS_ERROR_MESSAGE,
    ),
    destination: pathlib.Path = typer.Argument(...),
    ftps_host: str = typer.Argument(
        default="xmftps.xm.com.co", envvar="ASIC_FTPS_HOST"
    ),
    ftps_user: str = typer.Argument(..., envvar="ASIC_FTPS_USER"),
    ftps_password: str = typer.Argument(..., envvar="ASIC_FTPS_PASSWORD"),
    ftps_port: int = typer.Argument(default=210, envvar="ASIC_FTPS_PORT"),
    # asic_raw_container_name: str = typer.Argument(
    #     "asic-raw", envvar="ASIC_RAW_CONTAINER_NAME"
    # ),
    # asic_processed_container_name: str = typer.Argument(
    #     "asic", envvar="ASIC_PROCESSED_CONTAINER_NAME"
    # ),
):
    """
    Download files from asic's ftp server to local DESTINATION folder.

    FTP authentication info should be  provided as environment variables (ASIC_FTP_*)
    """
    if not extensions:
        extensions = [None]
    if not files:
        files = SUPPORTED_FILES

    locations = PUBLIC_SEARCHEABLE_LOCATIONS
    if agent is not None:
        locations.extend(PRIVATE_SEARCHEABLE_LOCATIONS)

    ftps = get_ftps(
        ftps_host=ftps_host,
        ftps_user=ftps_user,
        ftps_password=ftps_password,
        ftps_port=ftps_port,
    )

    file_list = list_supported_files(
        ftps,
        agent=agent,
        months=months,
        extensions=extensions,
        files=files,
        locations=locations,
    )

    logger.info(f"Total files to download: {len(file_list)}")

    for f in track(file_list, description="Dowloading files..."):
        remote = f
        local = destination / str(f)[1:]  # hack to remove root anchor
        os.makedirs(local.parent, exist_ok=True)
        logger.info(f"Downloading {remote} to {local}")

        try:
            grab_file(ftps, remote, local)

        except SSLZeroReturnError:
            ftps = get_ftps(
                ftps_host=ftps_host,
                ftps_user=ftps_user,
                ftps_password=ftps_password,
                ftps_port=ftps_port,
            )

            grab_file(ftps, remote, local)

    ftps.quit()
