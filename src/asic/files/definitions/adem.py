import logging
import pathlib

import numpy as np

# Third party imports
import pandas as pd

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
    name_pattern = "(?P<kind>adem)(?P<name_month>[0-9]{2})(?P<name_day>[0-9]{2}).(?P<ext_versioned>[tT]{1}[xX]{1}[a-zA-Z0-9]+)"
    location_pattern = "/informacion_xm/publicok/sic/comercia/(?P<location_year>[0-9]{4})-(?P<location_month>[0-9]{2})/"
    description = "Los archivos de demanda comercial"

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
        ADEM: es un archivo diario
        versiones: TX2, TXR, TXF
        AGENTE
        EPSC: Código SIC del agente comercializador
        CODIGO:
        DMRE: demanda regulada
        PRRE: perdidas reguladas
        """
        total = self.reader.read(filepath)
        total["FECHA"] = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

        filter = np.full(total.index.shape, True)
        filter = filter & (total["CODIGO"].isin(["DMRE", "PRRE"]))
        if self.agent is not None:
            filter = filter & (total["AGENTE"] == self.agent.upper())

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
                total.columns.get_level_values(0), total.columns.get_level_values(1)
            )
        ]
        total.columns = cols  # type: ignore
        return_cols = ["FECHA_HORA", "AGENTE", "DMRE_VALOR", "PRRE_VALOR"]
        return total[return_cols]


if __name__ == "__main__":
    import pathlib

    path = pathlib.Path(
        "./borrar/informacion_xm/PublicoK/SIC/COMERCIA/2023-10/adem1001.Tx2"
    )
    purepath = pathlib.PureWindowsPath("/") / pathlib.PureWindowsPath(
        path.as_posix()
    ).relative_to("./borrar")
    file = ADEM.from_remote_path(purepath)
    print(file)
    data = file.read(path)
    print(data.head(10))
    prepro_data = file.preprocess(path)
    print(prepro_data.head(10))
