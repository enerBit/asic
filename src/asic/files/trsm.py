import logging
import pathlib

import pandas as pd

# Local application imports
from asic.reader import FileReader

# Third party imports
# import pandas as pd
from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

trsm_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {"FECHA": {"format": "%Y-%m-%d"}},
    "dtype": {"FECHA": str, "CODIGO": str, "DESCRIPCION": str, "VALOR": float},
}


class TRSM(FileReader):
    def __init__(self):
        return super().__init__(trsm_format.copy())


def trsm_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    TRSM: se publica un archivo por mes.
    versiones: TXR, TXF
    """
    trsm_reader = TRSM()
    total = trsm_reader.read(filepath)

    total = total[total["CODIGO"] == "MC"]
    return_cols = ["FECHA", "CODIGO", "DESCRIPCION", "VALOR"]
    return total[return_cols]
