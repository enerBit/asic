import importlib.resources
import json as json
import pathlib
import re
from enum import Enum
from typing import Annotated
import os

from pydantic import BaseModel, StringConstraints

LOCAL_LOCATION_TEMPLATE = "{remote_parent}/{normalized_version}/{remote_name}"

LOCAL_LOCATION_REGEX = re.compile(
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
    normalized_version: Annotated[str, StringConstraints(pattern=r"^[-]?[0-9]{3}$")]
    order: int


class ASICFileVisibility(str, Enum):
    PUBLIC = "public"
    AGENT = "agent"


class ASICFileConfigDefinition(BaseModel):
    code: str
    visibility: ASICFileVisibility
    name_pattern: str
    location_pattern: str
    description: str | None


class ASICFileConfig(ASICFileConfigDefinition):
    name_template: str
    location_template: str


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


def pattern_to_template_replacement(match_object: re.Match) -> str:
    template_key = match_object["capture_name"]
    regex = match_object["regex"]
    match template_key:
        case (
            "location_month"
            | "name_month"
            | "location_day"
            | "name_day"
            | "location_year"
            | "name_year"
        ):
            quant_match = PATTERN_REGEX_EXACT_QUANTIFIER.match(regex)
            if quant_match is not None:
                quantifier_template = f":0{quant_match['exact_quantifier']}"
            return "{" + template_key + quantifier_template + "}"
        case "ext_excel" | "ext_versioned":
            return "{extension}"
        case "code":
            return regex
        case _:
            return "{" + template_key + "}"


def pattern_to_template(patt: str) -> str:
    PATTERN_REGEX.findall(patt)
    template = PATTERN_REGEX.sub(pattern_to_template_replacement, patt)
    return template


def load_asic_file_extension_map() -> dict[str, ASICExtesionMap]:
    """Return a list of ASIC extension maps"""
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    resource = importlib.resources.files("asic").joinpath(
        "data/ASIC_FILE_EXTENSION_MAP.jsonl"
    )
    lines = []
    with resource.open("r") as src:
        for line in src:
            lines.append(json.loads(line))

    asic_file_extension_mapper = {
        line["asic_extension"]: ASICExtesionMap.model_validate(line) for line in lines
    }
    return asic_file_extension_mapper


def load_asic_file_config() -> dict[str, ASICFileConfig]:
    """Return a list of ASIC file configurations"""
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    path_env = os.getenv("ASIC_FILE_CONFIG_PATH")
    if path_env is None:
        raise ValueError("\nASIC_FILE_CONFIG_PATH environment variable not set, you can create the file with the following structure:\n"
                         """{"code":"adem", "visibility": "public","name_pattern":"(?P<kind>adem)(?P<name_month>[0-9]{2})(?P<name_day>[0-9]{2}).(?P<ext_versioned>[a-zA-Z0-9]+)", "location_pattern":"/RUTA/PUBLICA/DEL/FTP/(?P<location_year>[0-9]{4})-(?P<location_month>[0-9]{2})/","description":"Los archivos de demanda comercial"}\n"""
                         "then save your file as .jsonl and set the file path in the environment variable")

    resource = pathlib.Path(path_env)
    lines = []
    with resource.open("r") as src:
        for line in src:
            lines.append(json.loads(line))

    asic_file_config_definition = {
        line["code"]: ASICFileConfigDefinition.model_validate(line) for line in lines
    }
    # mappping = {c: t[1] for c, t in TEMPLATE_PATTERN_MAPPING.items()}
    # code_template = "{code}"
    asic_file_config: dict[str, ASICFileConfig] = {}
    for c, fcd in asic_file_config_definition.items():
        name_template = pattern_to_template(fcd.name_pattern)
        location_template = pattern_to_template(fcd.location_pattern)

        asic_file_config[c] = ASICFileConfig.model_validate(
            fcd.model_dump()
            | {"name_template": name_template, "location_template": location_template}
        )
    return asic_file_config
