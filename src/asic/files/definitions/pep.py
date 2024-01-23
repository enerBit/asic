import logging
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath

# Third party imports
import pandas as pd

# Local application imports
from asic.files.file import AsicFile, FileKind, VisibilityEnum

logger = logging.getLogger(__name__)

FORMAT = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {"AGENTE": str, "VALOR PE": float},
}


class PEP(AsicFile):
    kind = FileKind.PEP
    visibility = VisibilityEnum.PUBLIC
    name_pattern = "(?P<kind>pep)(?P<name_month>[0-9]{2})(?P<name_day>[0-9]{2}).(?P<ext_versioned>[a-zA-Z0-9]+)"
    location_pattern = "/informacion_xm/publicok/sic/comercia/(?P<location_year>[0-9]{4})-(?P<location_month>[0-9]{2})/"
    description = ""  # TODO

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
        pep: se publica un archivo por día.
        versiones: TX1, TX2, TXR y TXF
        AGENTE:
          SISTEMA: el precio de escasez ponderado del sistema
        """
        total = self.read(target)
        total["FECHA"] = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

        total["FECHA"] = pd.to_datetime(
            total["FECHA"],
            format="%Y-%m-%d",
        )
        return_cols = ["FECHA", "AGENTE", "VALOR PE"]
        return total[return_cols]
