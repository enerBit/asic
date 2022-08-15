import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

ldcbmr_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {"FECHA": {"format": "%Y-%m-%d"}},
    "dtype": {
        "FECHA": str,
        "CODIGO": str,
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


class LDCBMR(FileReader):
    def __init__(self):
        return super().__init__(ldcbmr_format.copy())


def ldcbmr_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    TRSM: se publica un archivo por mes.
    versiones: TXR, TXF
    """
    ldcbmr_reader = LDCBMR()
    total = ldcbmr_reader.read(filepath)

    total = total.set_index(["FECHA", "CODIGO"]).stack().reset_index()
    total = total.rename(columns={"level_2": "NOMBRE HORA", 0: "VALOR"})
    total["HORA"] = (total["NOMBRE HORA"].str.slice(start=-2)).astype(int) - 1
    total["HORA"] = pd.to_timedelta(total["HORA"], unit="h")
    total["FECHA_HORA"] = total["FECHA"] + total["HORA"]

    total = (
        total.set_index(["FECHA", "NOMBRE HORA", "HORA", "FECHA_HORA", "CODIGO"])
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
    return_col = ["FECHA_HORA", "CHDC_VALOR", "VHDC_VALOR"]
    return total[return_col]
