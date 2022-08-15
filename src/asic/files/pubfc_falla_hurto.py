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
    "sheet_name": 0,
    "engine": "openpyxl",
    "dt_fields": {
        "Fecha de Reporte de la Falla": {"format": "%Y-%m-%d"},
        "Fecha Máxima de Normalización": {"format": "%Y-%m-%d"},
        "Fecha de Solicitud de Ampliación": {"format": "%Y-%m-%d"},
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
