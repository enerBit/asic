
import logging
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath

import pandas as pd

from asic import ASIC_FILE_CONFIG
from asic.files.file import AsicFile, FileKind, VisibilityEnum

logger = logging.getLogger(__name__)

FORMAT = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "FECHA": str,
        "AGENTE": str,
        "BENEFICIARIO": str,
        "CONCEPTO": str,
        "TIPOPAGO": str,
        "VALOR": int,
        "MAGNITUD": int,
    }
}

class TSERV(AsicFile):
    kind = FileKind.TSERV
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
    def agent(self) -> str | None:
        return self._agent

    @property
    def version(self) -> str | None:
        return self._version

    def preprocess(self, target: Path | BytesIO | StringIO) -> pd.DataFrame:
        """
        TSERV: es un archivo mensual
        versiones: TXR, TXF, TXn
        VALOR: Contiene el soporte a la liquidación de servicios CND, SIC y FAZNI.
        """
        total = self.read(target)

        return total
