import json as json
import re
from enum import Enum
from typing import Annotated

import pkg_resources
from pydantic import BaseModel, StringConstraints

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
    asic_extension: Annotated[str, StringConstraints(pattern=r"^\.[a-zA-Z0-9]*$")]
    normalized_version: Annotated[str, StringConstraints(pattern=r"^[0-9]{3}$")]
    order: int


class ASICFileVisibility(str, Enum):
    PUBLIC = "public"
    AGENT = "agent"


class ASICFileConfigDefinition(BaseModel):
    code: str
    visibility: ASICFileVisibility
    name_template: str
    location_template: str
    description: str | None


class ASICFileConfig(ASICFileConfigDefinition):
    name_pattern: str
    location_pattern: str


PATTERN_REGEX = re.compile(
    pattern=r"""
    \(                              # Start of group definition
    \?P                             # Start of group naming definition
    \<                              # Start of name
    (?P<capture_name>.*?)           # name
    \>                              # End of group naming definition
    (?P<regex>.*?)?                 # regex of name
    \)                              # End of group definition
    """,
    flags=re.VERBOSE,
)

PATTERN_REGEX_EXACT_QUANTIFIER = re.compile(
    pattern=r"""
    .*?                             # Non quantifier definition
    \{                              # Start of quantifier definition
    (?P<exact_quantifier>[0-9]+)    # Quantifier
    \}                              # End of quantifier definition
    """,
    flags=re.VERBOSE,
)

TEMPLATE_PATTERN_MAPPING: dict[str, tuple[str, str]] = {
    "code": ("{code}", "(?P<code>[a-zA-Z0-9-_]*)"),
    "name_year": ("{name_year:04}", "(?P<name_year>[0-9]{4})"),
    "name_month": ("{name_month:02}", "(?P<name_month>[0-9]{2})"),
    "name_day": ("{name_day:02}", "(?P<name_day>[0-9]{2})"),
    "ext_versioned": (
        "{ext_versioned}",
        "(?P<ext_versioned>[tT]{1}[xX]{1}[a-zA-Z0-9]+)",
    ),
    "ext_excel": ("{ext_excel}", "(?P<ext_excel>xlsx)"),
    "name_agent": ("{agent}", "(?P<name_agent>[a-zA-Z]{4})"),
    "location_agent": ("{agent}", "(?P<location_agent>[a-zA-Z]{4})"),
    "location_month": ("{location_month:02}", "(?P<location_month>[0-9]{2})"),
    "location_day": ("{location_day:02}", "(?P<location_day>[0-9]{2})"),
    "location_year": ("{location_year:04}", "(?P<location_year>[0-9]{4})"),
}


def pattern_to_template_replacement(match_object: str) -> str:
    template_key = match_object["capture_name"]
    regex = match_object["regex"]
    match template_key:
        case "location_month" | "name_month" | "location_day" | "name_day" | "location_year" | "name_year":
            quant_match = PATTERN_REGEX_EXACT_QUANTIFIER.match(regex)
            if quant_match is not None:
                quantifier_template = f":{quant_match['exact_quantifier']}"
        case _:
            quantifier_template = ""
    return "{" + template_key + quantifier_template + "}"


def pattern_to_template(patt: str) -> str:
    matches = PATTERN_REGEX.findall(patt)
    template = PATTERN_REGEX.sub(pattern_to_template_replacement, patt)
    return template


def load_asic_file_extension_map() -> dict[str, ASICExtesionMap]:
    """Return a list of ASIC extension maps"""
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream("asic", "data/ASIC_FILE_EXTENSION_MAP.jsonl")
    lines = []
    for line in stream:
        lines.append(json.loads(line))

    asic_file_extension_mapper = {
        line["asic_extension"]: ASICExtesionMap.model_validate(line) for line in lines
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

    asic_file_config = {
        line["code"]: ASICFileConfigDefinition.model_validate(line) for line in lines
    }
    mappping = {c: t[1] for c, t in TEMPLATE_PATTERN_MAPPING.items()}
    code_template = "{code}"
    for c, fcd in asic_file_config.items():
        name_pattern = fcd.name_template
        location_pattern = fcd.location_template
        if code_template in name_pattern or code_template in location_pattern:
            code_mapping_fix = {"code": "(?P<code>{code})".format(code=fcd.code)}

        name_pattern = name_pattern.format(**(mappping | code_mapping_fix))
        location_pattern = location_pattern.format(**(mappping | code_mapping_fix))
        asic_file_config[c] = ASICFileConfig.model_validate(
            fcd.model_dump()
            | {"name_pattern": name_pattern, "location_pattern": location_pattern}
        )
    return asic_file_config
