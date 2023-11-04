import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

sntie_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {"FECHA": {"format": "%Y-%m-%d"}},
    "dtype": {
        "FECHA": str,
        "AGENTE": str,
        "CONCEPTO": str,
        "BANDERA": str,
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


class SNTIE(FileReader):
    def __init__(self):
        return super().__init__(sntie_format.copy())


def sntie_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    SNTIE: se publica un archivo por mes.
    versiones: TXF
    AGENTE:
     EPSC: el codigo del agente ##AQUI VA ENERBIT##
    CONCEPTO:
     DSNTM
    BANDERA:
     S
    """
    sntie_reader = SNTIE()
    total = sntie_reader.read(filepath)
    total = total[
        (total["AGENTE"] == item.agent)
        & (total["CONCEPTO"] == "DSNTM")
        & (total["BANDERA"] == "S")
    ]
    total = (
        total.set_index(["FECHA", "AGENTE", "CONCEPTO", "BANDERA"])
        .stack()
        .reset_index()
    )
    total = total.rename(columns={"level_4": "NOMBRE HORA", 0: "COSTO_TIES"})
    total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
    total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
    total["FECHA_HORA"] = total["FECHA"] + total["HORA"]
    ret_cols = ["FECHA_HORA", "AGENTE", "CONCEPTO", "BANDERA", "COSTO_TIES"]
    return total[ret_cols]
