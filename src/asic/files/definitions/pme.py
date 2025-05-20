import logging
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath

# Third party imports
import pandas as pd

from asic import ASIC_FILE_CONFIG
# Local application imports
from asic.files.file import AsicFile, FileKind, VisibilityEnum

logger = logging.getLogger(__name__)

FORMAT = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {"CONCEPTO": str, "DESCRIPCION": str, "VALOR": float},
}


class PME(AsicFile):
    kind = FileKind.PME
    visibility = VisibilityEnum.PUBLIC
    name_pattern = ASIC_FILE_CONFIG[kind].name_pattern
    location_pattern = ASIC_FILE_CONFIG[kind].location_pattern
    location = ASIC_FILE_CONFIG[kind].location_template
    description = ASIC_FILE_CONFIG[kind].description

    _format = FORMAT

    @property
    def path(self) -> PureWindowsPath:
        return self._path

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int | None:
        return self._day

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def version(self) -> str | None:
        return self._version

    @property
    def agent(self) -> str | None:
        return self._agent

    def preprocess(self, target: Path | BytesIO | StringIO) -> pd.DataFrame:
        """
        PME: se publica un archivo mensual.
        versiones: TXA
        AGENTE:
          SISTEMA: el precio de escacez de activación
        """
        total = self.read(target)
        total["MES"] = f"{self.year:04d}-{self.month:02d}"

        return_cols = ["MES", "CONCEPTO", "DESCRIPCION", "VALOR"]
        return total[return_cols]
