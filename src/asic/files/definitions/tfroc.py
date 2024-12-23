
import logging
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath

import pandas as pd

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
    name_pattern = "(?P<kind>tfroc)(?P<name_month>[0-9]{2})(?P<name_day>[0-9]{2}).(?P<ext_versioned>[a-zA-Z0-9]+)"
    location_pattern = "/informacion_xm/USUARIOSK/(?P<location_agent>[a-zA-Z]{4})/SIC/COMERCIA/(?P<location_year>[0-9]{4})-(?P<location_month>[0-9]{2})/"
    location = "/informacion_xm/usuariosk/{location_agent}/sic/comercia/{location_year:04}-{location_month:02}/"
    description = "Los archivos de factores de perdidas aplicables a los consumos"
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
    def agent(self) -> str:
        return self._agent

    @property
    def version(self) -> str:
        return self._version

    def preprocess(self, target: Path | BytesIO | StringIO) -> pd.DataFrame:
        """
        TFROC: es un archivo diario
        versiones: TX2, TXR, TXF
        VALOR: energia calculada por ASIC para frontera en cada periodo
        """
        total = self.read(target)

        return total
