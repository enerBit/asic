import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

desbmex_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "FECHA": str,
        "CONCEPTO": str,
        "REPRESENTANTE": str,
        "MERCADO COMERCIALIZACIÓN": str,
        "SUBMERCADO": str,
        "TIPO": str,
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


class DESBMEX(FileReader):
    def __init__(self):
        return super().__init__(desbmex_format.copy())


def desbmex_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    DESBMEX: es un archivo diario
    versiones: TX2, TXR, TXF
    Contiene la información de alivios y demandas asociados a generación excedentaria por submercado en los diferentes mercados de comercialización en que participa.
    """
    desbmex_reader = DESBMEX()
    total = desbmex_reader.read(filepath)
    total["FECHA"] = f"{item.year:04d}-{item.month:02d}-{item.day:02d}"
    total["FECHA"] = pd.to_datetime(
        total["FECHA"],
        format="%Y-%m-%d",
    )
    total = (
        total.set_index(
            [
                "FECHA",
                "CONCEPTO",
                "REPRESENTANTE",
                "MERCADO COMERCIALIZACIÓN",
                "SUBMERCADO",
                "TIPO",
            ]
        )
        .stack()
        .reset_index()
    )
    total = total.rename(columns={"level_6": "NOMBRE HORA", 0: "VALOR"})
    total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
    total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
    total["FECHA_HORA"] = total["FECHA"] + total["HORA"]
    return_cols = [
        "FECHA_HORA",
        "CONCEPTO",
        "REPRESENTANTE",
        "MERCADO COMERCIALIZACIÓN",
        "SUBMERCADO",
        "TIPO",
        "VALOR",
    ]
    return total[return_cols]