import logging
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath

# Third party imports
import pandas as pd

from asic import ASIC_FILE_CONFIG
from asic.files.file import AsicFile, FileKind, VisibilityEnum

# Local application imports

logger = logging.getLogger(__name__)

DATE_FORMAT = {"format": "%d-%m-%Y"}
CALIBRATION_DATE_FORMAT = {"format": "%d/%m/%Y"}

FORMAT = {
    "type": "xlsx",
    "sheet_name": "Fronteras Comerciales",
    "dt_fields": {
        "Registrada por primera vez el": DATE_FORMAT,
        "Inicio Representación Frontera": DATE_FORMAT,
        "Último Cambio en Medidor Ppal o Transformadores": DATE_FORMAT,
        "Fecha de Calibración Med. Ppal": CALIBRATION_DATE_FORMAT,
        "Ppal Actualizada por última vez el": DATE_FORMAT,
        "Último Cambio en Medidor Resp.": DATE_FORMAT,
        "Fecha de Calibración Med. Resp.": CALIBRATION_DATE_FORMAT,
        "Resp. Actualizada por última vez el": DATE_FORMAT,
    },
    # Identificadores como texto para no perder ceros a la izquierda
    "dtype": {
        "Código SIC": str,
        "Código Propio": str,
        "NIU": str,
        "NIT": str,
        "Código SIC DDV": str,
        "Predio ID": str,
        "Número de Serie Med. Ppal.": str,
        "Clase del Medidor": str,
        "Clase del CT": str,
        "Clase del PT": str,
        "Número de Serie Med. Resp.": str,
        "Agrupada bajo la": str,
        "Embebida bajo la": str,
        "Código CIIU": str,
        "Código SIC Submercado Exportador": str,
        "Código SIC Frontera Generación": str,
        "Código SIC Frontera Usuario": str,
        "Código SIC Submercado Consumo": str,
        "Código SIC Submercado Usuario": str,
    },
}


class FRONTERAS(AsicFile):
    kind = FileKind.FRONTERAS
    visibility = VisibilityEnum.AGENT
    name_pattern = ASIC_FILE_CONFIG[kind].name_pattern
    location_pattern = ASIC_FILE_CONFIG[kind].location_pattern
    location = ASIC_FILE_CONFIG[kind].location_template
    description = ASIC_FILE_CONFIG[kind].description

    _format = FORMAT

    @property
    def path(self) -> PureWindowsPath:
        return self._path

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int | None:
        return self._day

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def version(self) -> str | None:
        return self._version

    @property
    def agent(self) -> str | None:
        return self._agent

    def preprocess(self, target: Path | BytesIO | StringIO) -> pd.DataFrame:
        """
        FRONTERAS: snapshot del universo de fronteras comerciales del agente.
        Se publica de forma diaria pero esporádica (sin cronograma fijo).
        Ya viene en formato tidy (una fila por frontera); se agrega FECHA,
        la fecha de publicación tomada del nombre del archivo.
        """
        total = self.read(target)
        if total.empty:
            # XM a veces publica el archivo con la hoja vacía
            logger.warning(f"Empty '{self._format['sheet_name']}' sheet in {self.path}")
        total.insert(
            0,
            "FECHA",
            pd.Timestamp(year=self.year, month=self.month, day=self.day or 1),
        )
        return total
