import json as json
from typing import Annotated

import pkg_resources
from pydantic import BaseModel, StringConstraints


class ASICExtesionMap(BaseModel):
    asic_extension: Annotated[str, StringConstraints(pattern=r"^\.[a-zA-Z0-9]*$")]
    normalized_version: Annotated[str, StringConstraints(pattern=r"^[0-9]{3}$")]
    order: int


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


# def load_asic_file_config() -> dict[str, ASICFileConfig]:
#     """Return a list of ASIC file configurations"""

#     asic_file_config: dict[str, ASICFileConfig] = dict()
#     for c in asic.files.definitions.SUPPORTED_FILE_CLASSES:
#         kind = c.kind
#         name_template = pattern_to_template(c.name_pattern)
#         location_template = pattern_to_template(c.location_pattern)

#         asic_file_config[kind] = ASICFileConfig.model_validate(
#             fcd.model_dump()
#             | {"name_template": name_template, "location_template": location_template}
#         )
#     return asic_file_config
