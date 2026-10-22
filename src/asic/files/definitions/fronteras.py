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

# Encabezado completo publicado por XM; las columnas nuevas se reportan en el log
KNOWN_COLUMNS = [
    "Código SIC",
    "Nombre de la Frontera",
    "Código Propio",
    "Registrada en el Mercado por",
    "Registrada por primera vez el",
    "Factor de Pérdidas",
    "NIU",
    "NIT",
    "Voltaje (kV)",
    "Nivel de Tensión",
    "Tipo Punto Medicion",
    "Transferencia Máxima [kWh]",
    "Representante Frontera",
    "Inicio Representación Frontera",
    "Representante Anterior",
    "Operador de Red",
    "Operador de Red de la Zona",
    "Agente Exportador",
    "Agente Importador",
    "Tipo de Frontera",
    "Capacidad de Transporte [MW]",
    "Capacidad de transporte - Acuerdo de Conexión Compartida [MW]",
    "Capacidad efectiva [MW]",
    "Nombre del CGM",
    "Código SIC DDV",
    "Predio ID",
    "Nombre del Predio",
    "Representante de la DDV",
    "Número de Serie Med. Ppal.",
    "Marca Med. Ppal.",
    "Modelo Med. Ppal.",
    "Clase del Medidor",
    "Número Elementos Ppal.",
    "Clase del CT",
    "Clase del PT",
    "Último Cambio en Medidor Ppal o Transformadores",
    "Entidad Calibradora Med. Ppal.",
    "Fecha de Calibración Med. Ppal",
    "Ppal Actualizada por última vez el",
    "Número de Serie Med. Resp.",
    "Marca Med. Resp.",
    "Modelo Med. Resp.",
    "Número Elementos Resp.",
    "Último Cambio en Medidor Resp.",
    "Entidad Calibradora Med. Resp.",
    "Fecha de Calibración Med. Resp.",
    "Resp. Actualizada por última vez el",
    "Es Agrupadora",
    "Factor PSF (Para agrupadoras)",
    "Agrupada bajo la",
    "Es Principal de Modelo Embebido",
    "Embebida bajo la",
    "Factor Acordado",
    "Factor Ajuste",
    "Factor de Pérdidas Frontera Principal (para embebidas)",
    "Código CIIU",
    "Clasificación Industral General",  # sic: así viene en el archivo de XM
    "Clasificación Industrial Específica",
    "Departamento",
    "Municipio",
    "Centro Poblado",
    "Dirección",
    "Latitud (°)",
    "Longitud (°)",
    "Altitud (msnm)",
    "Código SIC Submercado Exportador",
    "Código SIC Frontera Generación",
    "Nombre Recurso Generación",
    "Clasificación Recurso",
    "Capacidad Efectiva/Potencia Máxima Declarada",
    "Tipo/Tecnología",
    "Código SIC Frontera Usuario",
    "Código SIC Submercado Consumo",
    "Código SIC Submercado Usuario",
]

FORMAT = {
    "type": "xlsx",
    "sheet_name": "Fronteras Comerciales",
    "required_columns": [
        "Código SIC",
        "Código Propio",
        "NIU",
        "Representante Frontera",
        "Operador de Red",
        "Tipo de Frontera",
    ],
    "known_columns": KNOWN_COLUMNS,
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
