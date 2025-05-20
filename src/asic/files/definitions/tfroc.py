
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
        "CODIGO FRONTERA": str,
        "NIVEL DE TENSION": str,
        "FACTOR DE PERDIDAS": float,
        "FACTOR DE PULSOS": float,
        "FACTOR DE DISPLAY": float,
        "AGENTE COMERCIAL QUE EXPORTA": str,
        "AGENTE COMERCIAL QUE IMPORTA": str,
        "MERCADO COMERCIALIZACIÓN QUE EXPORTA": str,
        "MERCADO COMERCIALIZACIÓN QUE IMPORTA": str
    }
}

class TFROC(AsicFile):
    kind = FileKind.TFROC
    visibility = VisibilityEnum.AGENT
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
        TFROC: es un archivo diario
        versiones: TX2, TXR, TXF
        VALOR: energia calculada por ASIC para frontera en cada periodo
        """
        total = self.read(target)

        return total
