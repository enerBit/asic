
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
        "CONTRATO": str,
        "VENDEDOR": str,
        "COMPRADOR": str,
        "TIPO": str,
        "TIPOMERC": str,
        "TIPO ASIGNA": str,
        "DESP_HORA 01": float,
        "DESP_HORA 02": float,
        "DESP_HORA 03": float,
        "DESP_HORA 04": float,
        "DESP_HORA 05": float,
        "DESP_HORA 06": float,
        "DESP_HORA 07": float,
        "DESP_HORA 08": float,
        "DESP_HORA 09": float,
        "DESP_HORA 10": float,
        "DESP_HORA 11": float,
        "DESP_HORA 12": float,
        "DESP_HORA 13": float,
        "DESP_HORA 14": float,
        "DESP_HORA 15": float,
        "DESP_HORA 16": float,
        "DESP_HORA 17": float,
        "DESP_HORA 18": float,
        "DESP_HORA 19": float,
        "DESP_HORA 20": float,
        "DESP_HORA 21": float,
        "DESP_HORA 22": float,
        "DESP_HORA 23": float,
        "DESP_HORA 24": float,
        "TRF_HORA 01": float,
        "TRF_HORA 02": float,
        "TRF_HORA 03": float,
        "TRF_HORA 04": float,
        "TRF_HORA 05": float,
        "TRF_HORA 06": float,
        "TRF_HORA 07": float,
        "TRF_HORA 08": float,
        "TRF_HORA 09": float,
        "TRF_HORA 10": float,
        "TRF_HORA 11": float,
        "TRF_HORA 12": float,
        "TRF_HORA 13": float,
        "TRF_HORA 14": float,
        "TRF_HORA 15": float,
        "TRF_HORA 16": float,
        "TRF_HORA 17": float,
        "TRF_HORA 18": float,
        "TRF_HORA 19": float,
        "TRF_HORA 20": float,
        "TRF_HORA 21": float,
        "TRF_HORA 22": float,
        "TRF_HORA 23": float,
        "TRF_HORA 24": float,
    },
}


class DSPCTTOS(AsicFile):
    kind = FileKind.DSPCTTOS
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
        DSPCTTOS: es un archivo mensual
        versiones: TXR, TXF, TXn
        VALOR: Muestra para cada uno de los agentes, todos los conceptos de la liquidación del Mercado Colombiano, con los cuales se pueden consolidar las Compras y Ventas Totales del Agente para un proceso de liquidación o ajuste mensual.
        """
        total = self.read(target)
        total["FECHA"] = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
        total["FECHA"] = pd.to_datetime(
            total["FECHA"],
            format="%Y-%m-%d",
        )
        total = (
            total.set_index(
                ["FECHA", "CONTRATO", "VENDEDOR", "COMPRADOR", "TIPO", "TIPOMERC", "TIPO ASIGNA"]
            )
            .stack()
            .reset_index()
        )

        total = total.rename(columns={"level_7": "NOMBRE HORA", 0: "VALOR"})
        total["CONCEPTO"] = total["NOMBRE HORA"].apply(lambda x: x.split("_")[0])
        total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
        total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
        total["FECHA_HORA"] = total["FECHA"] + total["HORA"]

        total = (
            total[
                [
                    "FECHA",
                    "HORA",
                    "FECHA_HORA",
                    "CONTRATO",
                    "VENDEDOR",
                    "COMPRADOR",
                    "TIPO",
                    "TIPOMERC",
                    "TIPO ASIGNA",
                    "CONCEPTO",
                    "VALOR",
                ]
            ]
            .set_index(
                [
                    "FECHA",
                    "HORA",
                    "FECHA_HORA",
                    "CONTRATO",
                    "VENDEDOR",
                    "COMPRADOR",
                    "TIPO",
                    "TIPOMERC",
                    "TIPO ASIGNA",
                    "CONCEPTO",
                ]
            )
            .unstack()
            .reset_index()
        )
        cols = [
            f"{l1}_{l0}" if l1 else l0
            for (l0, l1) in zip(
                total.columns.get_level_values(0), total.columns.get_level_values(1)
            )
        ]
        total.columns = pd.Index(cols)

        ret_cols = [
            "FECHA_HORA",
            "CONTRATO",
            "VENDEDOR",
            "COMPRADOR",
            "TIPO",
            "TIPOMERC",
            "TIPO ASIGNA",
            "DESP_VALOR",
            "TRF_VALOR",
        ]
        return total[ret_cols]
