import json as json
import re

import pkg_resources
from pydantic import BaseModel, constr

LOCATION_TEMPLATE = "{remote_parent}/{normalized_version}/{remote_name}"

LOCATION_REGEX = re.compile(
    r"""
    /                                       # Inner directory start
    (?P<location_year>[0-9]{4})             # Year of the location directory
    -                                       # Separator between year and month
    (?P<location_month>[0-9]{2})            # Month of the location directory
    /                                       # Directory sepparator
    (?P<location_normalized_version>[0-9]{3})  # Version of the location directory
    /                                       # Inner directory end
    """,
    re.VERBOSE,
)


class ASICExtesionMap(BaseModel):
    asic_extension: constr(regex=r"^\.[a-zA-Z0-9]*$")  # type: ignore # noqa: F722
    normalized_version: constr(regex=r"^[0-9]{3}$")  # type: ignore # noqa: F722
    order: int


class ASICFileConfig(BaseModel):
    code: str
    name_pattern: str
    location_pattern: str
    description: str | None


def load_asic_file_extension_map() -> dict[str, ASICExtesionMap]:
    """Return a list of ASIC extension maps"""
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream("asic", "data/ASIC_FILE_EXTENSION_MAP.jsonl")
    lines = []
    for line in stream:
        lines.append(json.loads(line))

    asic_file_extension_mapper = {
        line["asic_extension"]: ASICExtesionMap.parse_obj(line) for line in lines
    }
    return asic_file_extension_mapper


def load_asic_file_config() -> dict[str, ASICFileConfig]:
    """Return a list of ASIC file configurations"""
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream("asic", "data/ASIC_FILE_CONFIG.jsonl")
    lines = []
    for line in stream:
        lines.append(json.loads(line))

    asic_file_config = {line["code"]: ASICFileConfig.parse_obj(line) for line in lines}
    return asic_file_config
