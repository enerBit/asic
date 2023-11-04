import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

trsd_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "AGENTE": str,
        "TIPO AGENTE": str,
        "VENTAS BOLSA kwh": float,
        "VENTAS DESVIACION kwh": float,
        "VENTAS BOLSA $": float,
        "VENTAS DESVIACION $": float,
        "COMPRAS BOLSA kwh": float,
        "COMPRAS BOLSA $": float,
        "COMPRAS BOLSA CON SALDO NETO TIE MÉRITO ($)": float,
    },
}


class CLIQ(FileReader):
    def __init__(self):
        return super().__init__(trsd_format.copy())


def cliq_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    cliq: se publica un archivo por día.
    versiones: TX2, TXR y TXF
    """
    cliq_reader = CLIQ()
    total = cliq_reader.read(filepath)
    total["FECHA"] = f"{item.year:04d}-{item.month:02d}-{item.day:02d}"
    total = total[total["AGENTE"] == item.agent]
    total["FECHA"] = pd.to_datetime(
        total["FECHA"],
        format="%Y-%m-%d",
    )
    ret_cols = ["FECHA",
                "AGENTE",
                "TIPO AGENTE",
                "VENTAS BOLSA kwh",
                "VENTAS DESVIACION kwh",
                "VENTAS BOLSA $",
                "VENTAS DESVIACION $",
                "COMPRAS BOLSA kwh",
                "COMPRAS BOLSA $",
                "COMPRAS BOLSA CON SALDO NETO TIE MÉRITO ($)"]
    return total[ret_cols]
