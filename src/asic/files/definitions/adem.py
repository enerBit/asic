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
        "CODIGO": str,
        "AGENTE": str,
        "CONTENIDO": str,
        "HORA 01": float,
        "HORA 02": float,
        "HORA 03": float,
        "HORA 04": float,
        "HORA 05": float,
        "HORA 06": float,
        "HORA 07": float,
        "HORA 08": float,
        "HORA 09": float,
        "HORA 10": float,
        "HORA 11": float,
        "HORA 12": float,
        "HORA 13": float,
        "HORA 14": float,
        "HORA 15": float,
        "HORA 16": float,
        "HORA 17": float,
        "HORA 18": float,
        "HORA 19": float,
        "HORA 20": float,
        "HORA 21": float,
        "HORA 22": float,
        "HORA 23": float,
        "HORA 24": float,
    },
}


class ADEM(AsicFile):
    kind = FileKind.ADEM
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
        ADEM: es un archivo diario
        versiones: TX2, TXR, TXF
        AGENTE
        EPSC: Código SIC del agente comercializador
        CODIGO:
        DMRE: demanda regulada
        DMNR: demanda no regulada
        PRRE: perdidas reguladas
        PRNR: perdidas no reguladas
        """
        total = self.read(target)
        total["FECHA"] = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

        filter = np.full(total.index.shape, True)
        filter = filter & (total["CODIGO"].isin(["DMRE", "PRRE","DMNR","PRNR"]))

        total = total[filter]
        total["FECHA"] = pd.to_datetime(
            total["FECHA"],
            format="%Y-%m-%d",
        )
        total = (
            total.set_index(["FECHA", "CODIGO", "AGENTE", "CONTENIDO"])
            .stack()
            .reset_index()
        )
        total = total.rename(columns={"level_4": "NOMBRE HORA", 0: "VALOR"})
        total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
        total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
        total["FECHA_HORA"] = total["FECHA"] + total["HORA"]

        total = (
            total[
                [
                    "FECHA",
                    "NOMBRE HORA",
                    "HORA",
                    "FECHA_HORA",
                    "AGENTE",
                    "CODIGO",
                    "VALOR",
                ]
            ]
            .set_index(
                ["FECHA", "NOMBRE HORA", "HORA", "FECHA_HORA", "AGENTE", "CODIGO"]
            )
            .unstack()
            .reset_index()
        )
        cols = [
            f"{l1}_{l0}" if l1 else str(l0)
            for (l0, l1) in zip(
                total.columns.get_level_values(0), total.columns.get_level_values(1), strict=False
            )
        ]
        total.columns = cols  # type: ignore
        return_cols = ["FECHA_HORA", "AGENTE", "DMRE_VALOR", "PRRE_VALOR","DMNR_VALOR","PRNR_VALOR"]
        return total[return_cols]

