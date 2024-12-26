
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
    name_pattern = "(?P<kind>tserv)(?P<name_month>[0-9]{2}).(?P<ext_versioned>[a-zA-Z0-9]+)"
    location_pattern = "/informacion_xm/publicok/sic/comercia/(?P<location_year>[0-9]{4})-(?P<location_month>[0-9]{2})/"
    location = "/informacion_xm/publicok/sic/comercia/{location_year:04}-{location_month:02}/"
    description = "Contiene el soporte a la liquidación de servicios CND, SIC y FAZNI."
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
