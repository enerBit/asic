import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

pubfc_falla_hurto_format = {
    "type": "xlsx",
    "sheet_name" "encoding": "cp1252",
    "dt_fields": {
        "Fecha de Reporte de la Falla": {"format": "%Y-%m-%d %H:%M:%S"},
        "Fecha Máxima de Normalización": {"format": "%Y-%m-%d %H:%M:%S"},
        "Fecha de Solicitud de Ampliación": {"format": "%Y-%m-%d %H:%M:%S"},
    },
    "dtype": {
        "Código SIC": str,
        "Tipo de Frontera": str,
        "Equipo en Falla": str,
        "Fecha de Reporte de la Falla": str,
        "Fecha Máxima de Normalización": str,
        "Días en Falla": int,
        "Solicitó Ampliación de Plazo": str,
        "Fecha de Solicitud de Ampliación": str,
        "Requerimientos": str,
        "Agente que Reportó la Falla": str,
        "Agente Representante": str,
        "Operador de Red": str,
    },
}


class PubFCFallaHurto(FileReader):
    def __init__(self):
        return super().__init__(pubfc_falla_hurto_format.copy())


def pubfc_falla_hurto_preprocess(
    filepath: pathlib.Path, item: FileItemInfo
) -> pd.DataFrame:
    """
    PUBFC: se publica un archivo por dia.
    versiones: No aplica
    """
    pubfc_reader = PubFCFallaHurto()
    total = pubfc_reader.read(filepath)

    return_col = ["Código SIC", "Fecha de Reporte de la Falla"]
    return total[return_col]
