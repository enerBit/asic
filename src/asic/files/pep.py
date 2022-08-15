import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

pep_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {"AGENTE": str, "VALOR PE": float},
}


class PEP(FileReader):
    def __init__(self):
        return super().__init__(pep_format.copy())


def pep_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    pep: se publica un archivo por día.
    versiones: TX1, TX2, TXR y TXF
    AGENTE:
      SISTEMA: el precio de escasez del sistema
    """
    pep_reader = PEP()
    total = pep_reader.read(filepath)
    total["FECHA"] = f"{item.year:04d}-{item.month:02d}-{item.day:02d}"

    total = total[total["AGENTE"] == "SISTEMA"]

    total["FECHA"] = pd.to_datetime(
        total["FECHA"],
        format="%Y-%m-%d",
    )
    return_cols = ["FECHA", "AGENTE", "VALOR PE"]
    return total[return_cols]
