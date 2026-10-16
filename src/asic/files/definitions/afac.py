
import logging
from collections import defaultdict
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath
import re

import pandas as pd

from asic import ASIC_FILE_CONFIG
from asic.files.file import AsicFile, FileKind, VisibilityEnum

logger = logging.getLogger(__name__)

# Catálogo de conceptos conocidos. XM agrega y retira conceptos entre
# publicaciones, por eso NO se usa para validar: solo para avisar en el log
# cuando aparece un concepto nuevo. Cualquier columna distinta de AGENTE se
# lee como float.
KNOWN_CONCEPTS = [
    "PERDIDA REAL (kWh)",
    "DEMANDA REAL (kWh)",
    "GENERACION REAL (kWh)",
    "COMPRAS EN BOLSA (KWH)",
    "COMPRAS EN BOLSA ($)",
    "VENTAS EN BOLSA (KWH)",
    "VENTAS EN BOLSA ($)",
    "COMPRAS EN DESVIACION (KWH)",
    "COMPRAS EN DESVIACION ($)",
    "VENTAS EN DESVIACION (KWH)",
    "VENTAS EN DESVIACION ($)",
    "COMPRAS EN RECONCILIACION (KWH)",
    "COMPRAS EN RECONCILIACION ($)",
    "VENTAS EN RECONCILIACION (KWH)",
    "VENTAS EN RECONCILIACION ($)",
    "COMPRAS EN CONTRATOS (kWh)",
    "VENTAS EN CONTRATOS (kWh)",
    "COMPRAS ENERGIA EN BOLSA (KWH)",
    "COMPRAS ENERGIA EN BOLSA ($)",
    "VENTAS ENERGIA EN BOLSA (KWH)",
    "VENTAS ENERGIA EN BOLSA ($)",
    "VR CARGO POR CONFIABILIDAD ($)",
    "VD CARGO POR CONFIABILIDAD ($)",
    "NETO CXC ($)",
    "COMPRAS CARGO POR CONFIABILIDAD ($)",
    "VENTAS CARGO POR CONFIABILIDAD ($)",
    "COMPRAS EN BOLSA NACIONAL (KWH)",
    "COMPRAS EN BOLSA NACIONAL ($)",
    "VENTAS EN BOLSA NACIONAL (KWH)",
    "VENTAS EN BOLSA NACIONAL ($)",
    "COMPRAS EN BOLSA INTERNACIONAL (KWH)",
    "COMPRAS EN BOLSA INTERNACIONAL ($)",
    "VENTAS EN BOLSA INTERNACIONAL (KWH)",
    "VENTAS EN BOLSA INTERNACIONAL ($)",
    "SERVICIOS AGC ($)",
    "RESPONSABILIDAD COMERCIAL AGC (KWH)",
    "RESPONSABILIDAD COMERCIAL AGC ($)",
    "TOTAL COMPRAS ($)",
    "TOTAL VENTAS ($)",
    "VALOR A PAGAR POR SRPF ($)",
    "VALOR A RECIBIR POR SRPF ($)",
    "TOTAL RESTRICCIONES ($)",
    "RENTAS DE CONGESTION ($)",
    "RESTRICCIONES ALIVIADAS ($)",
    "VEBO (KWH)",
    "RENTAS DE CONGESTIÓN POR IMPORTACIÓN ($)",
    "DISTRIBUCIÓN SALDO NETO TIE EN MÉRITO ($)",
    "DISTRIBUCIÓN SALDO NETO TIE FUERA DE MÉRITO ($)",
    "COMPRAS BOLSA CON SALDO NETO TIE MÉRITO ($)",
    "RENDIMIENTOS FINANCIEROS POR EXPORTACIONES TIE($)",
    "ALIVIO POR CIOEF ($)",
    "COMPRAS NDC ($)",
    "VENTAS DESVIACIONES OEFH ($)",
    "COMPRAS DESVIACIONES OEFH ($)",
    "DEVOLUCION DINEROS DEL CARGO POR CONFIABILIDAD ($)",
    "COBRO DINERO CARGO POR CONFIABILIDAD ($)",
    "COMPRAS ARRANQUE Y PARADA ($)",
    "VENTAS ARRANQUE Y PARADA ($)",
    "Ventas por EEVE ($)",
    "Compras por EEVE ($)",
    "Restricciones por EEVE ($)",
    "Cobro uso respaldo($)",
    "Alivio restricciones RES 05/2010 ($)",
    "COMPRAS EN BOLSA TIES($)",
    "VENTAS EN BOLSA TIES ($)",
    "MAGNITUD EN Kwh  DE COMPRAS EN BOLSA DE TIES",
    "MAGNITUD EN kwh DE VENTAS EN BOLSA TIES",
    "ALIVIO POR EJECUCION DE GARANTIA ($)",
    "VALOR TOTAL EJECUCION DE GARANTIA ($)",
    "Alivio por VCSRCFVD($)",
    "VOEFV a cargo por la OEFV adquirida en la SRCFV($)",
    "VMOEFV a cargo al Margen del Precio MP SRCFV ($):",
    "Costo de Exportación ($)",
    "Total Costo de Exportación ($)",
    "Total de Generación Ideal en kWh del Agente",
    "Total de Holgura de AGC en kWh asignados al Agente",
    "Energía vendida y embalsada Asignada kWh",
    "VR Demanda Res 155/2014",
    "Alivio Asociado a la Resolución CREG 024/2015 en $",
    "Cobro Autogeneradores Res 024/2015",
    "Valor a favor para generador. Res 178/2015",
    "Valor a cargo para comercializador. Res 178/2015",
    "Valor a cargo para generador. Res 195/2015",
    "Valor a favor para generador. Res 195/2015",
    "Valor a favor para comercializador. Res 195/2015",
    "Valor a cargo para comercializador. Res 195/2015",
    "VALOR A CARGO PAGOS DE ENERGIA EXCEDENTARIA ($)",
    "VALOR A FAVOR POR ENERGIA EXCEDENTARIA ($)",
    "VC_RD resolución 011 de 2015",
    "VF_RD resolución 011 de 2015",
    "Valor a Favor delta ajuste RD",
    "Valor a Cargo delta ajuste RD",
    "VALOR A CARGO R026-2016 ($).",
    "VALOR A FAVOR R026-2016 ($).",
    "VALOR A FAVOR R029-2016 ($).",
    "RF039 resolución 039 de 2016",
    "RC039 resolución 039 de 2016",
    "Balance Final 029 de 2016",
    "Valor a cargo para comercializador. RES. 062 2013",
    "Valor a favor para generador. RES. 062 2013",
    "Valor del DE TIE. RES. 049 2018 (kWh)",
    "Valor del DE TIE. RES. 049 2018 ($)",
    "Magnitud desviación despacho. RES. 060 2019 (kWh)",
    "Valor Desviación Despacho. RES. 060 2019 ($)",
    "Magnitud desviación Redespacho. RES. 060 2019(kWh)",
    "Valor Desviación ReDespacho. RES. 060 2019 ($)",
    "Desviación Generación Variable. RES. 060 2019($)",
    "Alivio desviaciones Res. CREG 060/2019 ($)",
    "VALOR PAGO AJUSTE RES. 140 2017 ($)",
    "VALOR COBRO AJUSTE RES. 140 2017 ($)",
    "VALOR PAGO EXCEDENTE RES. 140 2017 ($)",
    "VALOR COBRO FALTANTE RES. 140 2017 ($)",
    "Valor a cargo para comercializador. Res 207/2020",
    "Valor Fiducia para restricciones. Res 194/2020 ($)",
    "Valor alivio a restricciones. Res 194/2020 ($)",
    "Valor a favor por excedentes de exportación",
    "Valor a cargo por sobrecostos de exportación",
    "Dist alivio excedente VT cuando es menor a cero",
    "Dist cobro faltante VT (+) y no agentes DODEFA (-)",
    "Valor a Pagar por Generación Forzada",
    "Valor Gen. Forzada recaudado en restricciones",
    "Valor a cargo por ingreso regulado",
    "Valor a favor por ingreso regulado",
    "Valor a cargo C - CDNCE",
]

FORMAT = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "required_columns": ["AGENTE"],
    "known_columns": ["AGENTE", *KNOWN_CONCEPTS],
    "dtype": defaultdict[str, type](lambda: float, {"AGENTE": str}),
}


class AFAC(AsicFile):
    kind = FileKind.AFAC
    visibility = VisibilityEnum.PUBLIC
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
    def agent(self) -> str | None:
        return self._agent

    @property
    def version(self) -> str | None:
        return self._version

    def preprocess(self, target: Path | BytesIO | StringIO) -> pd.DataFrame:
        """
        AFAC: es un archivo mensual
        versiones: TXR, TXF, TXn
        VALOR: Muestra para cada uno de los agentes, todos los conceptos de la liquidación del Mercado Colombiano, con los cuales se pueden consolidar las Compras y Ventas Totales del Agente para un proceso de liquidación o ajuste mensual.
        """
        total = self.read(target)
        total.columns = total.columns.str.strip()
        total = total.set_index(["AGENTE"]).stack().reset_index()
        total = total.rename(columns={"level_1": "CONCEPTO", 0: "VALOR"})
        ret_cols = ["AGENTE", "CONCEPTO", "VALOR"]
        return total[ret_cols]
