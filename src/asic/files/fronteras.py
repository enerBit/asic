import logging
import pathlib

# Third party imports
import pandas as pd

# Local application imports
from asic.reader import FileReader

from ..metadata import FileItemInfo

logger = logging.getLogger(__name__)

fronteras_format = {
    "type": "xlsx",
    "sheet_name": "Fronteras Comerciales",
    "encoding": "cp1252",
    "dt_fields": {
        "Registrada por primera vez el": {"format": "%d-%m-%Y"},
        "Inicio Representación Frontera": {"format": "%d-%m-%Y"},
        "Último Cambio en Medidor Ppal o Transformadores": {"format": "%d-%m-%Y"},
        "Fecha de Calibración Med. Ppal": {"format": "%d-%m-%Y"},
        "Actualizada por última vez el": {"format": "%Y-%m-%d %H:%M:%S"},
        "Último Cambio en Medidor Resp.": {"format": "%d-%m-%Y"},
        "Fecha de Calibración Med. Resp.": {"format": "%d-%m-%Y"},
    },
    "dtype": {
        "Código SIC": str,
        "Nombre de la Frontera": str,
        "Registrada en el Mercado por": str,
        "Registrada por primera vez el": str,
        "Factor de Pérdidas": float,
        "NIU": str,
        "NIT": str,
        "Voltaje (kV)": str,
        "Nivel de Tensión": str,
        "Tipo Punto Medicion": str,
        "Representante Frontera": str,
        "Inicio Representación Frontera": str,
        "Representante Anterior": str,
        "Operador de Red": str,
        "Operador de Red de la Zona": str,
        "Agente Exportador": str,
        "Agente Importador": str,
        "Tipo de Frontera": str,
        "Nombre del CGM": str,
        "Código SIC DDV": str,
        "Predio ID": str,
        "Nombre del Predio": str,
        "Representante de la DDV": str,
        "Número de Serie Med. Ppal": str,
        "Marca Med. Ppal": str,
        "Clase del Medidor": str,
        "Clase del CT": str,
        "Clase del PT": str,
        "Último Cambio en Medidor Ppal o Transformadores": str,
        "Entidad Calibradora Med. Ppal.": str,
        "Fecha de Calibración Med. Ppal": str,
        "Actualizada por última vez el": str,
        "Número de Serie Med. Resp.": str,
        "Marca Med. Resp.": str,
        "Último Cambio en Medidor Resp.": str,
        "Entidad Calibradora Med. Resp.": str,
        "Fecha de Calibración Med. Resp.": str,
        "Actualizada por última vez el.1": str,  # Added the ".1" since the column name is repeated
        "Es Agrupadora": str,
        "Factor PSF (Para agrupadoras)": float,
        "Agrupada bajo la": str,
        "Es Principal de Modelo Embebido": str,
        "Embebida bajo la": str,
        "Factor Acordado": float,
        "Factor Ajuste": float,
        "Factor de Pérdidas Frontera Principal (para embebidas)": float,
        "Código CIIU": str,
        "Clasificación Industral General": str,
        "Clasificación Industrial Específica": str,
        "NIT.1": str,  # Added the ".1" since the column name is repeated
        "Departamento": str,
        "Municipio": str,
        "Centro Poblado": str,
        "Dirección": str,
        "Latitud (°)": float,
        "Longitud (°)": float,
        "Altitud (msnm)": int,
        "Código SIC Submercado": str,
    },
}


class Fronteras(FileReader):
    def __init__(self):
        return super().__init__(fronteras_format.copy())


def fronteras_preprocess(filepath: pathlib.Path, item: FileItemInfo) -> pd.DataFrame:
    """
    fronteras: se publica un archivo por dia.
    versiones: No aplica
    """
    fronteras_reader = Fronteras()
    total = fronteras_reader.read(filepath)

    return_col = ["Código SIC", "Nombre de la Frontera"]
    return total[return_col]
