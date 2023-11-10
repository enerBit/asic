import logging
import pathlib

# Third party imports
import pandas as pd

from asic.files.file import AsicFile, FileKind, VisibilityEnum

logger = logging.getLogger(__name__)
FORMAT = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "CONCEPTO": str,
        "MERCADO": str,
        "CÓDIGO CONTRATO": str,
        "COMPRADOR": str,
        "VENDEDOR": str,
        "TIPO DE DESPACHO": str,
        "TIPO ASIGNA": str,
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


class BALCTTOS(AsicFile):
    kind = FileKind.BALCTTOS
    visibility = VisibilityEnum.AGENT
    name_pattern = "(?P<kind>BalCttos)(?P<name_month>[0-9]{2})(?P<name_day>[0-9]{2}).(?P<ext_versioned>[a-zA-Z0-9]+)"
    location_pattern = "/informacion_xm/USUARIOSK/(?P<location_agent>[a-zA-Z]{4})/SIC/COMERCIA/(?P<location_year>[0-9]{4})-(?P<location_month>[0-9]{2})/"
    description = "Los archivos de despacho de demanda por mercados R y NR, Nacional, TIE e Internacional"

    _format = FORMAT

    @property
    def path(self):
        return self._path

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    @property
    def extension(self):
        return self._extension

    @property
    def version(self):
        return self._version

    @property
    def agent(self):
        return self._agent

    def preprocess(self, filepath: pathlib.Path) -> pd.DataFrame:
        """
        balcttos: se publica un archivo por día.
        versiones: TX2, TXR y TXF
        CONCEPTO:
        EBRC: Energía en bolsa regulada a cargo, en kWh.
        EBOC: Energía en bolsa no regulada a cargo, en kWh.
        AGENTE:
        EPSC: Código SIC del agente comercializador
        """
        total = self.reader.read(filepath)
        total["FECHA"] = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

        total["FECHA"] = pd.to_datetime(
            total["FECHA"],
            format="%Y-%m-%d",
        )
        total = (
            total.set_index(
                [
                    "FECHA",
                    "CONCEPTO",
                    "MERCADO",
                    "CÓDIGO CONTRATO",
                    "COMPRADOR",
                    "VENDEDOR",
                    "TIPO DE DESPACHO",
                    "TIPO ASIGNA",
                ]
            )
            .stack()
            .reset_index()
        )
        total = total.rename(columns={"level_8": "NOMBRE HORA", 0: "VALOR"})
        total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
        total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
        total["FECHA_HORA"] = total["FECHA"] + total["HORA"]
        total["HORA"] = total["FECHA_HORA"].dt.strftime("%H:%M:%S")
        ret_cols = [
            "FECHA_HORA",
            "CONCEPTO",
            "MERCADO",
            "CÓDIGO CONTRATO",
            "COMPRADOR",
            "VENDEDOR",
            "TIPO DE DESPACHO",
            "TIPO ASIGNA",
            "VALOR",
        ]
        return total[ret_cols]
