import datetime as dt
import logging
import os
import pathlib
from typing import Optional

import pydantic
import rich
import rich.logging
import rich.progress
import typer

from asic import ASIC_FILE_CONFIG, ASIC_FILE_EXTENSION_MAP
from asic.config import ASICFileVisibility
from asic.files.definitions import SUPPORTED_FILE_CLASSES
from asic.ftp import (
    get_ftps,
    grab_file,  # list_supported_files_in_location,
    list_supported_files,
)
from asic.publication import list_latest_published_versions

logger = logging.getLogger("asic")
logger.addHandler(rich.logging.RichHandler())

YEAR_MONTH_FORMATS = ["%Y-%m", "%Y%m"]
YEAR_MONTH_MATCH_ERROR_MESSAGE = f"Must match one of: {YEAR_MONTH_FORMATS}"
SUPPORTED_FILE_KINDS = sorted([k.lower() for k in SUPPORTED_FILE_CLASSES])
SUPPORTED_FILE_KINDS_ERROR_MESSAGE = f"Must match one of: {SUPPORTED_FILE_KINDS}"
SUPPORTED_EXTENSIONS = [e.lower() for e in ASIC_FILE_EXTENSION_MAP.keys()]
SUPPORTED_EXTENSIONS_ERROR_MESSAGE = f"""Must match one of: ['{"', '".join(SUPPORTED_EXTENSIONS[:6])}', ..., '{"', '".join(SUPPORTED_EXTENSIONS[-2:])}']"""

cli = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@cli.callback()
def main(
    ctx: typer.Context,
    verbosity: int = typer.Option(0, "--verbosity", "-v", count=True),
    ftps_host: str = typer.Option(default="xmftps.xm.com.co", envvar="ASIC_FTPS_HOST"),
    ftps_port: int = typer.Option(default=210, envvar="ASIC_FTPS_PORT"),
    ftps_user: str = typer.Option(..., envvar="ASIC_FTPS_USER", prompt=True),
    ftps_password: str = typer.Option(..., envvar="ASIC_FTPS_PASSWORD", prompt=True),
    agent: str = typer.Option(default=None, envvar="ASIC_AGENT", help="Agent's asic code, required for private files"),
):
    """
    FTP authentication info should be provided as environment variables (ASIC_FTP_*)
    """
    logger.info(f"Verbosity level {verbosity}")
    match verbosity:
        case 0:
            logger.setLevel(logging.ERROR)
        case 1:
            logger.setLevel(logging.WARNING)
        case 2:
            logger.setLevel(logging.INFO)
        case 3:
            logger.setLevel(logging.DEBUG)
        case _:
            logger.setLevel(logging.DEBUG)

    ctx.meta["ASIC_FTPS_HOST"] = ftps_host
    ctx.meta["ASIC_FTPS_PORT"] = ftps_port
    ctx.meta["ASIC_FTPS_USER"] = ftps_user
    ctx.meta["ASIC_FTPS_PASSWORD"] = pydantic.SecretStr(ftps_password)
    ctx.meta["VERBOSITY"] = verbosity
    ctx.meta["ASIC_AGENT"] = agent


def validate_month(month: str) -> str:
    for f in YEAR_MONTH_FORMATS:
        try:
            dt.datetime.strptime(month, f).date()
            break
        except ValueError:
            continue
    else:
        raise typer.BadParameter(YEAR_MONTH_MATCH_ERROR_MESSAGE)

    return month


def parse_month(month: str) -> dt.date:
    for f in YEAR_MONTH_FORMATS:
        try:
            value = dt.datetime.strptime(month, f).date()
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"Failed to parse {month} as date")

    return value


def validate_file_kind(file_kind: str) -> str:
    if file_kind.lower() not in SUPPORTED_FILE_KINDS:
        raise typer.BadParameter(SUPPORTED_FILE_KINDS_ERROR_MESSAGE)
    return file_kind


def validate_version(version: str) -> str:
    if version.lower() not in SUPPORTED_EXTENSIONS:
        raise typer.BadParameter(SUPPORTED_EXTENSIONS_ERROR_MESSAGE)
    return version


def months_callback(values: list[str]) -> list[str]:
    months = sorted({validate_month(v) for v in values}, reverse=True)
    return months


def file_kinds_callback(values: list[str]) -> list[str]:
    if values is None:
        raise typer.BadParameter(SUPPORTED_FILE_KINDS_ERROR_MESSAGE)

    files = sorted(
        {validate_file_kind(v) for v in values},
        reverse=True,
    )

    return files


def extensions_callback(values: list[str]) -> list[str]:
    if values is None:
        raise typer.BadParameter(SUPPORTED_EXTENSIONS_ERROR_MESSAGE)

    extensions = list({validate_version(v) for v in values})

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
    ctx: typer.Context,
    months: list[str] = typer.Option(
        ...,
        "--month",
        callback=months_callback,
        help=YEAR_MONTH_MATCH_ERROR_MESSAGE,
    ),
    agent: Optional[str] = typer.Option(default=None,
                                        envvar="ASIC_AGENT",
                                        prompt=True,
                                        help="Agent's asic code, required for private files"),
    kinds: Optional[list[str]] = typer.Option(
        None,
        "--kind",
        callback=file_kinds_callback,
        help=SUPPORTED_FILE_KINDS_ERROR_MESSAGE,
    ),
    extensions: Optional[list[str]] = typer.Option(
        None,
        "--version",
        callback=extensions_callback,
        help=SUPPORTED_EXTENSIONS_ERROR_MESSAGE,
    ),
    # asic_raw_container_name: str = typer.Argument(
    #     "asic-raw", envvar="ASIC_RAW_CONTAINER_NAME"
    # ),
    # asic_processed_container_name: str = typer.Argument(
    #     "asic", envvar="ASIC_PROCESSED_CONTAINER_NAME"
    # ),
):
    """
    List files from asic's ftp server.

    FTP authentication info should be provided as environment variables (ASIC_FTP_*)
    """
    logger.info(
        "Listing files for"
        f" agent: {agent}"
        f" months: {months}"
        f" extensions: {extensions}"
        f" kinds: {kinds}"
    )
    ftps_host = ctx.meta["ASIC_FTPS_HOST"]
    ftps_port = ctx.meta["ASIC_FTPS_PORT"]
    ftps_user = ctx.meta["ASIC_FTPS_USER"]
    ftps_password = ctx.meta["ASIC_FTPS_PASSWORD"]
    verbosity = ctx.meta["VERBOSITY"]

    if not extensions:
        extensions = [None]  # type: ignore
    if not kinds:
        kinds = SUPPORTED_FILE_KINDS

    locations: set = set()
    for v in SUPPORTED_FILE_CLASSES.values():
        if v.kind in kinds:
            locations.add(v.location)

    ftps = get_ftps(
        ftps_host=ftps_host,
        ftps_user=ftps_user,
        ftps_password=ftps_password,
        ftps_port=ftps_port,
        verbosity=verbosity,
    )
    month_dates = [parse_month(m) for m in months]
    file_list = list_supported_files(
        ftps,
        agent=agent,
        months=month_dates,
        extensions=extensions,
        kinds=kinds,
        locations=list(locations),
    )

    ftps.quit()

    for f in file_list:
        rich.print(f.path)


@cli.command()
def download(
    ctx: typer.Context,
    is_preprocessing_required: bool = typer.Option(
        False, "--prepro", help="Preprocess each file after donwload"
    ),
    prepocessed_dir: bool = typer.Option(
    False, "--prepro-dirs", help="Create directories for preprocessed files if not present"
    ),
    months: list[str] = typer.Option(
        ...,
        "--month",
        callback=months_callback,
        help=YEAR_MONTH_MATCH_ERROR_MESSAGE,
    ),
    agent: Optional[str] = typer.Option(default=None,
                                        envvar="ASIC_AGENT",
                                        prompt=True,
                                        help="Agent's asic code, required for private files"),
    kinds: Optional[list[str]] = typer.Option(
        None,
        "--kind",
        callback=file_kinds_callback,
        help=SUPPORTED_FILE_KINDS_ERROR_MESSAGE,
    ),
    extensions: Optional[list[str]] = typer.Option(
        None,
        "--version",
        callback=extensions_callback,
        help=SUPPORTED_EXTENSIONS_ERROR_MESSAGE,
    ),
    destination: pathlib.Path = typer.Argument(...),
):
    """
    Download files from asic's ftp server to local DESTINATION folder.

    FTP authentication info should be provided as environment variables (ASIC_FTP_*)
    """
    if not extensions:
        extensions = [None]  # type: ignore
    if not kinds:
        kinds = SUPPORTED_FILE_KINDS

    ftps_host = ctx.meta["ASIC_FTPS_HOST"]
    ftps_port = ctx.meta["ASIC_FTPS_PORT"]
    ftps_user = ctx.meta["ASIC_FTPS_USER"]
    ftps_password = ctx.meta["ASIC_FTPS_PASSWORD"]
    verbosity = ctx.meta["VERBOSITY"]

    locations: set = set()
    for v in SUPPORTED_FILE_CLASSES.values():
        if v.kind in kinds:
            locations.add(v.location)

    ftps = get_ftps(
        ftps_host=ftps_host,
        ftps_user=ftps_user,
        ftps_password=ftps_password,
        ftps_port=ftps_port,
        verbosity=verbosity,
    )
    month_dates = [parse_month(m) for m in months]
    file_list = list_supported_files(
        ftps,
        agent=agent,
        months=month_dates,
        extensions=extensions,
        kinds=kinds,
        locations=list(locations),
    )

    logger.info(f"Total files to download: {len(file_list)}")

    for f in rich.progress.track(file_list, description="Downloading files..."):
        logger.info(f"File: {f.path}")
        remote = f
        local = destination / str(f.path)[1:]  # hack to remove root anchor
        os.makedirs(local.parent, exist_ok=True)
        logger.debug(f"Downloading {remote} to {local}")

        try:
            grab_file(ftps, remote.path, local)

        # except (ssl.SSLZeroReturnError, ssl.SSLEOFError):
        except Exception:
            logger.warning("Download failed, retrying connection")
            ftps = get_ftps(
                ftps_host=ftps_host,
                ftps_user=ftps_user,
                ftps_password=ftps_password,
                ftps_port=ftps_port,
                verbosity=verbosity,
            )

            grab_file(ftps, remote.path, local)

        if is_preprocessing_required:
            normalized_version = (
                f.metadata.version
                if f.metadata.version is not None
                else f.metadata.extension
            )
            subpath_str = str(f.path)[1:].replace(
                f"{f.year:04d}-{f.month:02d}",
                f"{f.year:04d}-{f.month:02d}\\{normalized_version}",
            )

            preprocessed_path = destination.joinpath(subpath_str)

            preprocessed = f.preprocess(local)
            write_to = preprocessed_path.with_suffix(".csv")
            try:
                if prepocessed_dir:
                    os.makedirs(preprocessed_path.parent, exist_ok=True)
                preprocessed.to_csv(
                    write_to,
                    index=False,
                    encoding="utf-8-sig",
                )
            except Exception as e:
                if "Cannot save file into a non-existent directory: " in str(e):
                    raise FileNotFoundError(f"{e}. Use the '--prepro-dirs' flag to create the folder")

                raise e


    ftps.quit()
