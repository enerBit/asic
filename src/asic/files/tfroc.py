import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

tfroc_format = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "FECHA": str,
        "CODIGO FRONTERA": str,
        "NIVEL DE TENSION": float,
        "FACTOR DE PERDIDAS": float,
        "FACTOR DE PULSOS ": float,
        "FACTOR DE DISPLAY": float,
        "AGENTE COMERCIAL QUE EXPORTA": str,
        "AGENTE COMERCIAL QUE IMPORTA": str,
        "MERCADO COMERCIALIZACIÓN QUE EXPORTA": str,
        "MERCADO COMERCIALIZACIÓN QUE IMPORTA": str,
    },
}


class TFROC(FileReader):
    def __init__(self):
        return super().__init__(tfroc_format.copy())


def tfroc_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    TFROC: se publica un archivo por dia.
    versiones: TX2, TXR, TXF
    """
    tfroc_reader = TFROC()
    total = tfroc_reader.read(filepath)

    ret_cols = [
        "FECHA",
        "CODIGO FRONTERA",
        "NIVEL DE TENSION",
        "FACTOR DE PERDIDAS",
        "FACTOR DE PULSOS ",
        "FACTOR DE DISPLAY",
        "AGENTE COMERCIAL QUE EXPORTA",
        "AGENTE COMERCIAL QUE IMPORTA",
        "MERCADO COMERCIALIZACIÓN QUE EXPORTA",
        "MERCADO COMERCIALIZACIÓN QUE IMPORTA",
    ]
    return total[ret_cols]
