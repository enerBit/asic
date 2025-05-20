import logging
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath

import numpy as np

# Third party imports
import pandas as pd

from asic import ASIC_FILE_CONFIG
from asic.files.file import AsicFile, FileKind, VisibilityEnum

# Local application imports

logger = logging.getLogger(__name__)

FORMAT = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "FECHA": str,
        "PERIODO": int,
        "PBNAL": float,
        "DdaCom": float,
        "HORA 01": float,
        "DEM": float,
        "PTB": float,
        "OHEFx": float,
        "OHEFy": float,
        "OHEFz": float,
        "GIx": float,
        "GIy": float,
        "GIz": float,
        "GIv": float,
        "GINAL_NDC": float,
    },
}


class PTB(AsicFile):
    kind = FileKind.PTB
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
        PTB: es un archivo diario
        versiones: TX2, TXR, TXF
        """
        total = self.read(target)

        total["FECHA"] = pd.to_datetime(
            total["FECHA"],
            format="%Y-%m-%d",
        )

        total = (
            total.set_index(["FECHA", "PERIODO"])
            .stack()
            .reset_index()
        )
        total = total.rename(columns={"PERIODO":"NOMBRE HORA","level_2": "CODIGO", 0: "VALOR"})
        total["HORA"] = total["NOMBRE HORA"]
        total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
        total["FECHA_HORA"] = total["FECHA"] + total["HORA"]

        return_cols = ["FECHA_HORA", "CODIGO", "VALOR"]
        return total[return_cols]

