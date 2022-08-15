import logging
import pathlib

import numpy as np

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

adem_format = {
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


class ADEM(FileReader):
    def __init__(self):
        return super().__init__(adem_format.copy())


def adem_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    ADEM: es un archivo diario
    versiones: TX2, TXR, TXF
    AGENTE
    EPSC: aqui va enerbit
    CODIGO:
    DMRE: demanda regulada
    PRRE: perdidas reguladas
    """
    adem_reader = ADEM()
    total = adem_reader.read(filepath)
    total["FECHA"] = f"{item.year:04d}-{item.month:02d}-{item.day:02d}"

    filter = np.full(total.index.shape, True)
    filter = filter & (total["CODIGO"].isin(["DMRE", "PRRE"]))
    if item.agent is not None:
        filter = filter & (total["AGENTE"] == item.agent.upper())

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
            ["FECHA", "NOMBRE HORA", "HORA", "FECHA_HORA", "AGENTE", "CODIGO", "VALOR"]
        ]
        .set_index(["FECHA", "NOMBRE HORA", "HORA", "FECHA_HORA", "AGENTE", "CODIGO"])
        .unstack()
        .reset_index()
    )
    cols = [
        f"{l1}_{l0}" if l1 else l0
        for (l0, l1) in zip(
            total.columns.get_level_values(0), total.columns.get_level_values(1)
        )
    ]
    total.columns = cols
    return_cols = ["FECHA_HORA", "AGENTE", "DMRE_VALOR", "PRRE_VALOR"]
    return total[return_cols]


if __name__ == "__main__":
    import pathlib

    reader = ADEM()
    path = pathlib.Path("./files/PublicoK/SIC/COMERCIA/2022-06/adem0617.TxF")
    data = reader.read(path)
    print(data.head(10))
    f_info = FileItemInfo(
        path=path,
        year=2022,
        month=6,
        day=17,
        extension=".txf",
        code="adem",
        version="004",
        agent="enbc",
    )
    prepro_data = adem_preprocess(path, f_info)
    print(prepro_data.head(10))
