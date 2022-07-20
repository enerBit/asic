import logging
import pathlib
import re

import pydantic

from asic import ASIC_FILE_CONFIG, ASIC_FILE_EXTENSION_MAP

from .config import LOCATION_REGEX

logger = logging.getLogger(__name__)


class FileItemInfo(pydantic.BaseModel):
    path: pathlib.PurePath
    year: int
    month: int
    day: int | None
    extension: str
    code: str
    version: str
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
    assert match.group("location_month") == match.group("month")

    year = (match.group("location_year"),)
    month = (match.group("month"),)
    extension = (match.group("ext"),)
    code = (match.group("code"),)
    version = (ASIC_FILE_EXTENSION_MAP[match.group("ext").lower()].normalized_version,)
    try:
        day = int(match.group("day"))
    except Exception:
        day = None
    return FileItemInfo(
        path=file_path,
        year=year,
        month=month,
        day=day,
        extension=extension,
        code=code,
        version=version,
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
    match = re.match(path_pattern, str(file_path))
    if match is None:
        raise ValueError(
            f"failed to extract metadata from file path {file_path} using pattern {path_pattern}"
        )
    assert match.group("location_month") == match.group("month")

    year = (match.group("location_year"),)
    month = (match.group("month"),)
    extension = (match.group("ext"),)
    code = (match.group("code"),)
    version = (ASIC_FILE_EXTENSION_MAP[match.group("ext").lower()].normalized_version,)
    try:
        day = int(match.group("day"))
    except Exception:
        day = None
    return FileItemInfo(
        path=file_path,
        year=year,
        month=month,
        day=day,
        extension=extension,
        code=code,
        version=version,
    )


if __name__ == "__main__":
    remote_path = pathlib.PurePosixPath(
        "/UsuariosK/ENBC/Sic/COMERCIA/2022-07/aenc0703.tx2"
    )
    file_info = extract_metadata_from_remote_path(remote_path, "AENC")
