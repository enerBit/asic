import logging
import pathlib
import re

import pydantic

from asic import ASIC_FILE_CONFIG, ASIC_FILE_EXTENSION_MAP

from .config import LOCATION_REGEX, ASICFileVisibility

logger = logging.getLogger(__name__)


class FileItemInfo(pydantic.BaseModel):
    path: pathlib.PurePath
    year: int
    month: int
    day: int | None
    extension: str
    code: str
    version: str | None
    agent: str | None

    class Config:
        arbitrary_types_allowed = True


def extract_metadata_from_remote_path(
    file_path: pathlib.PurePath, as_: str | None = None
) -> FileItemInfo:
    if as_ is None:
        logger.debug(
            "Trying file patterns to discover file code,"
            " consider passing the actual 'as_' argument"
        )
        for c, config in ASIC_FILE_CONFIG.items():
            name_pattern = config.name_pattern
            logger.debug(f"Trying file pattern {name_pattern:r} of code {c}")
            if re.match(name_pattern, str(file_path)):
                as_ = c
                break
        else:
            raise ValueError(
                f"Failed to find a file code in supported files for {file_path}"
            )
    try:
        file_config = ASIC_FILE_CONFIG[as_]
    except KeyError:
        raise ValueError(f"Unsupported file code '{as_}'")

    path_pattern = LOCATION_REGEX.pattern + file_config.name_pattern
    match = re.match(path_pattern, str(file_path))
    if match is None:
        raise ValueError(
            f"failed to extract metadata from file path {file_path} using pattern {path_pattern}"
        )
    match_groups = match.groupdict()

    year = int(match_groups.get("location_year", match_groups["name_year"]))
    month = int(match_groups.get("location_month", match_groups["name_month"]))
    day = int(match_groups.get("location_day", match_groups.get("name_day", None)))
    extension = match_groups["ext"]
    code = match_groups["code"]
    if extension in ASIC_FILE_EXTENSION_MAP:
        version = ASIC_FILE_EXTENSION_MAP[extension].normalized_version
    else:
        version = None
    if file_config.visibility == ASICFileVisibility.AGENT:
        agent = match_groups["agent"]
    else:
        agent = None
    return FileItemInfo(
        path=file_path,
        year=year,
        month=month,
        day=day,
        extension=extension,
        code=code,
        version=version,
        agent=agent,
    )


def extract_metadata_from_local_path(
    file_path: pathlib.PurePath, as_: str | None = None
) -> FileItemInfo:
    if as_ is None:
        logger.debug(
            "Trying file patterns to discover file code,"
            " consider passing the actual 'as_' argument"
        )
        for c, config in ASIC_FILE_CONFIG.items():
            name_pattern = config.name_pattern
            logger.debug(f"Trying file pattern {name_pattern:r} of code {c}")
            if re.match(name_pattern, str(file_path)):
                as_ = c
                break
        else:
            raise ValueError(
                f"Failed to find a file code in supported files for {file_path}"
            )
    try:
        file_config = ASIC_FILE_CONFIG[as_]
    except KeyError:
        raise ValueError(f"Unsupported file code '{as_}'")

    path_pattern = LOCATION_REGEX.pattern + file_config.name_pattern
    name_pattern = file_config.name_pattern
    match = re.match(path_pattern, str(file_path))
    if match is None:
        match = re.match(name_pattern, str(file_path))
        if match is None:
            raise ValueError(
                f"failed to extract metadata from file path {file_path} using pattern {path_pattern}"
            )
    match_groups = match.groupdict()

    year = int(match_groups.get("location_year", match_groups["name_year"]))
    month = int(match_groups.get("location_month", match_groups["name_month"]))
    day = int(match_groups.get("location_day", match_groups.get("name_day", None)))
    extension = match_groups["ext"]
    code = match_groups["code"]
    if extension in ASIC_FILE_EXTENSION_MAP:
        version = ASIC_FILE_EXTENSION_MAP[extension].normalized_version
    else:
        version = None
    if file_config.visibility == ASICFileVisibility.AGENT:
        agent = match_groups["agent"]
    else:
        agent = None

    return FileItemInfo(
        path=file_path,
        year=year,
        month=month,
        day=day,
        extension=extension,
        code=code,
        version=version,
        agent=agent,
    )


if __name__ == "__main__":
    remote_path = pathlib.PurePosixPath(
        "/UsuariosK/ENBC/Sic/COMERCIA/2022-07/aenc0703.tx2"
    )
    file_info = extract_metadata_from_remote_path(remote_path, "AENC")
