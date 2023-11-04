import logging
import pathlib

import numpy as np

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

oefagnch_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "CONCEPTO": str,
        "DESCRIPCION": str,
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


class OEFAGNCH(FileReader):
    def __init__(self):
        return super().__init__(oefagnch_format.copy())


def oefagnch_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    OEFAGNCH: es un archivo diario
    versiones: TX2, TXR, TXF
    Información necesaria para el cálculo de las desviaciones positivas horarias de las Obligaciones de Energía Firme 
    para cada uno de los agentes generadores que tiene una desviación diaria positiva. 
    Este archivo sólo se publica cuando el precio de bolsa supera el precio de escasez, para Comercializadores
    """
    oefagnch_reader = OEFAGNCH()
    total = oefagnch_reader.read(filepath)
    total["FECHA"] = f"{item.year:04d}-{item.month:02d}-{item.day:02d}"

    filter = np.full(total.index.shape, True)
    total = total[filter]
    total["FECHA"] = pd.to_datetime(
        total["FECHA"],
        format="%Y-%m-%d",
    )
    total = (
        total.set_index(["FECHA", "CONCEPTO", "DESCRIPCION"])
        .stack()
        .reset_index()
    )
    total = total.rename(columns={"level_3": "NOMBRE HORA", 0: "VALOR"})
    total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
    total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
    total["FECHA_HORA"] = total["FECHA"] + total["HORA"]
    return_cols = ["FECHA_HORA", "CONCEPTO", "DESCRIPCION", "VALOR"]
    return total[return_cols]