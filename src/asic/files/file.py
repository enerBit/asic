import enum
import logging
import re
from abc import ABC, abstractmethod
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath

import pandas as pd
import pydantic
from typing_extensions import Self

from asic import ASIC_FILE_EXTENSION_MAP, ASIC_FILE_CONFIG
from asic.reader import FileReader

logger = logging.getLogger(__name__)

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
    AENC = "aenc"
    BALCTTOS = "balcttos"
    PEP = "pep"
    PME = "PME"
    TRSD = "trsd"
    TFROC = "tfroc"
    TGRL = "tgrl"
    TSERV = "tserv"
    TRSM = "trsm"
    SNTIE = "sntie"
    AFAC = "afac"
    DSPCTTOS = "dspcttos"
    PTB = "PTB"
    CURT = "curt"
    FRONTERAS = "fronteras"

    # LDCBMR = "ldcbmr"
    # PUBFC = "pubfc"
    # PUBFC_FALLA_HURTO = "pubfc_falla-hurto"
    # CLIQ = "cliq"
    # DESBM = "desbm"
    # DESBMEX = "desbmex"
    # OEFAGNCH = "oefagnch"


class AsicFileMetadataInput(pydantic.BaseModel):
    year: int
    month: int
    day: int | None = None
    extension: str
    version: str | None = pydantic.Field(None, pattern=r"^[-]?[0-9]{3}$")
    agent: str | None = pydantic.Field(None, pattern=r"^[a-z]{4}$")


class AsicFileMetadata(AsicFileMetadataInput):
    remote_path: PureWindowsPath
    kind: FileKind


class VisibilityEnum(str, enum.Enum):
    PUBLIC = "public"
    AGENT = "agent"


class AsicFile(ABC):
    kind: FileKind
    visibility: VisibilityEnum
    name_pattern: str
    location_pattern: str
    location: str
    description: str | None

    @property
    @abstractmethod
    def path(self) -> PureWindowsPath:
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

    @abstractmethod
    def preprocess(self, target: Path | BytesIO | StringIO) -> pd.DataFrame:
        pass

    def _read_raw_header(self, raw_bytes: bytes) -> set[str]:
        fmt = self._format
        if fmt.get("type") in ("xls", "xlsx"):
            header = pd.read_excel(BytesIO(raw_bytes), sheet_name=fmt["sheet_name"], nrows=0)
            return {str(c).strip() for c in header.columns}
        sep: str = fmt.get("sep", ",")
        encoding: str = fmt.get("encoding", "utf-8")
        first_line = raw_bytes.decode(encoding).split("\n")[0].rstrip("\r")
        return {c.strip() for c in first_line.split(sep)}

    def validate_raw(self, raw_bytes: bytes) -> bool:
        fmt = self._format
        dtype: dict[str, type] = fmt.get("dtype", {})
        if not dtype:
            return True
        try:
            actual_columns = self._read_raw_header(raw_bytes)
        except Exception:
            return False

        required_columns = fmt.get("required_columns")
        if required_columns is None:
            expected_columns = {k.strip() for k in dtype.keys()}
            return actual_columns.issubset(expected_columns)

        # Esquema dinámico: solo se exigen las columnas estructurales; las
        # columnas desconocidas se aceptan y se reportan en el log.
        missing_columns = {c.strip() for c in required_columns} - actual_columns
        if missing_columns:
            logger.error(f"{self.kind.value}: missing required columns {sorted(missing_columns)}")
            return False
        known_columns = fmt.get("known_columns")
        if known_columns is not None:
            new_columns = actual_columns - {c.strip() for c in known_columns}
            if new_columns:
                logger.warning(f"{self.kind.value}: unknown columns {sorted(new_columns)}")
        return True

    @property
    @abstractmethod
    def _format(self) -> dict:
        pass

    def __init__(
        self,
        path: PureWindowsPath,
        year: int,
        month: int,
        extension: str,
        day: int | None = None,
        version: str | None = None,
        agent: str | None = None,
    ) -> None:
        self._path: PureWindowsPath = path
        self._year: int = year
        self._month: int = month
        self._day: int | None = day
        self._extension: str = extension
        self._version: str | None = version
        self._agent: str | None = agent
        self.reader = FileReader(self._format)
        self.name_template = pattern_to_template(self.name_pattern)
        self.location_template = pattern_to_template(self.location_pattern)

    def read(self, target: str | Path | StringIO | BytesIO) -> pd.DataFrame:
        return self.reader.read(target)

    @property
    def metadata(self) -> AsicFileMetadata:
        return AsicFileMetadata(
            remote_path=self.path,
            kind=self.kind,
            year=self.year,
            month=self.month,
            day=self.day,
            extension=self.extension,
            version=self.version,
            agent=self.agent,
        )

    @classmethod
    def from_remote_path(cls, remote_path: PureWindowsPath) -> Self:
        path_metadata = cls.extract_metadata_from_remote_path(remote_path)
        file = cls(path=remote_path, **path_metadata.model_dump())
        return file

    @classmethod
    def extract_metadata_from_remote_path(
        cls, file_path: PureWindowsPath
    ) -> AsicFileMetadataInput:
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

        if cls.visibility == VisibilityEnum.AGENT:
            agent = match_groups.get("location_agent", None)
            if agent is None:
                agent = match_groups["name_agent"]
            agent = agent.lower()
        else:
            agent = None
        return AsicFileMetadataInput(
            year=int(year),
            month=int(month),
            day=day,
            extension=extension,
            # kind=kind,
            version=version,
            agent=agent,
        )
