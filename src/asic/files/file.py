import enum
import pathlib
import re
from abc import ABC, abstractmethod

import pandas as pd
import pydantic
from typing_extensions import Self

from asic import ASIC_FILE_EXTENSION_MAP

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
        case "location_month" | "name_month" | "location_day" | "name_day" | "location_year" | "name_year":
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
    template = PATTERN_REGEX.sub(pattern_to_template_replacement, patt)
    return template


class FileKind(str, enum.Enum):
    ADEM = "adem"
    # TGRL = "tgrl"
    # AENC = "aenc"
    # TRSM = "trsm"
    # LDCBMR = "ldcbmr"
    # PEP = "pep"
    # TRSD = "trsd"
    # SNTIE = "sntie"
    # AFAC = "afac"
    # DSPCTTOS = "dspcttos"
    # PUBFC = "pubfc"
    # PUBFC_FALLA_HURTO = "pubfc_falla-hurto"
    # TFROC = "tfroc"
    # CLIQ = "cliq"
    # BALCTTOS = "balcttos"
    # DESBM = "desbm"
    # DESBMEX = "desbmex"
    # OEFAGNCH = "oefagnch"
    # FRONTERAS = "fronterascomerciales"


class AsicFileMetadata(pydantic.BaseModel):
    # kind: FileKind
    year: int
    month: int
    day: int | None = None
    extension: str
    version: str | None = pydantic.Field(None, pattern=r"^[0-9]{3}$")
    agent: str | None = pydantic.Field(None, pattern=r"^[a-z]{3}$")


class VisibilityEnum(str, enum.Enum):
    PUBLIC = "public"
    AGENT = "agent"


class AsicFile(ABC):
    @property
    @abstractmethod
    def path(self) -> pathlib.PurePath:
        pass

    @property
    @abstractmethod
    def kind(self) -> FileKind:
        pass

    @property
    @abstractmethod
    def year(self) -> int:
        pass

    @property
    @abstractmethod
    def month(self) -> int:
        pass

    @property
    @abstractmethod
    def day(self) -> int | None:
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str | None:
        pass

    @property
    @abstractmethod
    def agent(self) -> str | None:
        pass

    @property
    @abstractmethod
    def visibility(self) -> VisibilityEnum:
        pass

    @property
    @abstractmethod
    def name_pattern(self) -> str:
        pass

    @property
    @abstractmethod
    def location_pattern(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def preprocess(self, arg1) -> pd.DataFrame:
        pass

    @property
    @abstractmethod
    def _format(self) -> dict:
        pass

    def __init__(self) -> None:
        self.name_template = pattern_to_template(self.name_pattern)
        self.location_template = pattern_to_template(self.location_pattern)

    @classmethod
    def from_remote_path(cls, remote_path: pathlib.PurePosixPath) -> Self:
        path_metadata = cls.extract_metadata_from_remote_path(remote_path)
        file = cls(path=remote_path, **path_metadata.model_dump())
        return file

    @classmethod
    def extract_metadata_from_remote_path(
        cls, file_path: pathlib.PurePosixPath
    ) -> AsicFileMetadata:
        file_path_as_posix = file_path.as_posix()
        path_pattern = cls.location_pattern + cls.name_pattern
        match = re.match(path_pattern, file_path_as_posix, flags=re.IGNORECASE)
        if match is None:
            raise ValueError(
                f"failed to extract metadata from file path {file_path_as_posix} using pattern {path_pattern}"
            )
        match_groups = match.groupdict()

        year = match_groups.get("location_year", None)
        if year is None:
            year = match_groups["name_year"]
        month = match_groups.get("location_month", None)
        if month is None:
            month = match_groups["name_month"]
        day = match_groups.get("location_day", None)
        if day is None:
            day = match_groups.get("name_day", None)
        day = int(day) if day is not None else None
        if "ext_versioned" in match_groups:
            extension = f".{match_groups['ext_versioned'].lower()}"
            if extension in ASIC_FILE_EXTENSION_MAP:
                version = ASIC_FILE_EXTENSION_MAP[extension].normalized_version
            else:
                raise ValueError(f"Unsupported extension '{extension}'")
        elif "ext_excel" in match_groups:
            extension = f".{match_groups['ext_excel'].lower()}"
            version = None
        else:
            raise ValueError(
                f"One of ['ext_versioned', 'ext_excel'] must be in {file_path_as_posix}"
            )

        kind = match_groups["kind"].lower()
        if cls.visibility == VisibilityEnum.AGENT:
            agent = match_groups.get("location_agent", None)
            if agent is None:
                agent = match_groups["name_agent"]
        else:
            agent = None
        return AsicFileMetadata(
            year=int(year),
            month=int(month),
            day=day,
            extension=extension,
            # kind=kind,
            version=version,
            agent=agent,
        )
