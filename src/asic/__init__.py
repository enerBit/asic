from .config import (
    LOCATION_REGEX,
    LOCATION_TEMPLATE,
    load_asic_file_config,
    load_asic_file_extension_map,
)

ASIC_FILE_CONFIG = load_asic_file_config()
ASIC_FILE_EXTENSION_MAP = load_asic_file_extension_map()

__all__ = [
    "ASIC_FILE_CONFIG",
    "ASIC_FILE_EXTENSION_MAP",
    "LOCATION_REGEX",
    "LOCATION_TEMPLATE",
]
