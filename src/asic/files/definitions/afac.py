
import logging
from io import BytesIO, StringIO
from pathlib import Path, PureWindowsPath
import re

import pandas as pd

from asic import ASIC_FILE_CONFIG
from asic.files.file import AsicFile, FileKind, VisibilityEnum

logger = logging.getLogger(__name__)

FORMAT = {
    "type": "csv",
    "sep": ";",
    "encoding": "cp1252",
    "dt_fields": {},
    "dtype": {
        "AGENTE": str,
        "PERDIDA REAL (kWh)": float,
        "DEMANDA REAL (kWh)": float,
        "GENERACION REAL (kWh)": float,
        "COMPRAS EN BOLSA (KWH)": float,
        "COMPRAS EN BOLSA ($)": float,
        "VENTAS EN BOLSA (KWH)": float,
        "VENTAS EN BOLSA ($)": float,
        "COMPRAS EN DESVIACION (KWH)": float,
        "COMPRAS EN DESVIACION ($)": float,
        "VENTAS EN DESVIACION (KWH)": float,
        "VENTAS EN DESVIACION ($)": float,
        "COMPRAS EN RECONCILIACION (KWH)": float,
        "COMPRAS EN RECONCILIACION ($)": float,
        "VENTAS EN RECONCILIACION (KWH)": float,
        "VENTAS EN RECONCILIACION ($)": float,
        "COMPRAS EN CONTRATOS (kWh)": float,
        "VENTAS EN CONTRATOS (kWh)": float,
        "COMPRAS ENERGIA EN BOLSA (KWH)": float,
        "COMPRAS ENERGIA EN BOLSA ($)": float,
        "VENTAS ENERGIA EN BOLSA (KWH)": float,
        "VENTAS ENERGIA EN BOLSA ($)": float,
        "VR CARGO POR CONFIABILIDAD ($)": float,
        "VD CARGO POR CONFIABILIDAD ($)": float,
        "NETO CXC ($)": float,
        "COMPRAS CARGO POR CONFIABILIDAD ($)": float,
        "VENTAS CARGO POR CONFIABILIDAD ($)": float,
        "COMPRAS EN BOLSA NACIONAL (KWH)": float,
        "COMPRAS EN BOLSA NACIONAL ($)": float,
        "VENTAS EN BOLSA NACIONAL (KWH)": float,
        "VENTAS EN BOLSA NACIONAL ($)": float,
        "COMPRAS EN BOLSA INTERNACIONAL (KWH)": float,
        "COMPRAS EN BOLSA INTERNACIONAL ($)": float,
        "VENTAS EN BOLSA INTERNACIONAL (KWH)": float,
        "VENTAS EN BOLSA INTERNACIONAL ($)": float,
        "SERVICIOS AGC ($)": float,
        "RESPONSABILIDAD COMERCIAL AGC (KWH)": float,
        "RESPONSABILIDAD COMERCIAL AGC ($)": float,
        "TOTAL COMPRAS ($)": float,
        "TOTAL VENTAS ($)": float,
        "VALOR A PAGAR POR SRPF ($)": float,
        "VALOR A RECIBIR POR SRPF ($)": float,
        "TOTAL RESTRICCIONES ($)": float,
        "RENTAS DE CONGESTION ($)": float,
        "RESTRICCIONES ALIVIADAS ($)": float,
        "VEBO (KWH)": float,
        "RENTAS DE CONGESTIÓN POR IMPORTACIÓN ($)": float,
        "DISTRIBUCIÓN SALDO NETO TIE EN MÉRITO ($)": float,
        "DISTRIBUCIÓN SALDO NETO TIE FUERA DE MÉRITO ($)": float,
        "COMPRAS BOLSA CON SALDO NETO TIE MÉRITO ($)": float,
        "RENDIMIENTOS FINANCIEROS POR EXPORTACIONES TIE($)": float,
        "ALIVIO POR CIOEF ($)": float,
        "COMPRAS NDC ($)": float,
        "VENTAS DESVIACIONES OEFH ($)": float,
        "COMPRAS DESVIACIONES OEFH ($)": float,
        "DEVOLUCION DINEROS DEL CARGO POR CONFIABILIDAD ($)": float,
        "COBRO DINERO CARGO POR CONFIABILIDAD ($)": float,
        "COMPRAS ARRANQUE Y PARADA ($)": float,
        "VENTAS ARRANQUE Y PARADA ($)": float,
        "Ventas por EEVE ($)": float,
        "Compras por EEVE ($)": float,
        "Restricciones por EEVE ($)": float,
        "Cobro uso respaldo($)": float,
        "Alivio restricciones RES 05/2010 ($)": float,
        "COMPRAS EN BOLSA TIES($)": float,
        " VENTAS EN BOLSA TIES ($)": float,
        " MAGNITUD EN Kwh  DE COMPRAS EN BOLSA DE TIES": float,
        " MAGNITUD EN kwh DE VENTAS EN BOLSA TIES": float,
        "ALIVIO POR EJECUCION DE GARANTIA ($)": float,
        "VALOR TOTAL EJECUCION DE GARANTIA ($)": float,
        "Alivio por VCSRCFVD($)": float,
        "VOEFV a cargo por la OEFV adquirida en la SRCFV($)": float,
        "VMOEFV a cargo al Margen del Precio MP SRCFV ($):": float,
        "Costo de Exportación ($)": float,
        "Total Costo de Exportación ($)": float,
        "Total de Generación Ideal en kWh del Agente": float,
        "Total de Holgura de AGC en kWh asignados al Agente": float,
        "Energía vendida y embalsada Asignada kWh": float,
        "VR Demanda Res 155/2014": float,
        "Alivio Asociado a la Resolución CREG 024/2015 en $": float,
        "Cobro Autogeneradores Res 024/2015": float,
        "Valor a favor para generador. Res 178/2015": float,
        "Valor a cargo para comercializador. Res 178/2015": float,
        "Valor a cargo para generador. Res 195/2015": float,
        "Valor a favor para generador. Res 195/2015": float,
        "Valor a favor para comercializador. Res 195/2015": float,
        "Valor a cargo para comercializador. Res 195/2015": float,
        "VALOR A CARGO PAGOS DE ENERGIA EXCEDENTARIA ($)": float,
        "VALOR A FAVOR POR ENERGIA EXCEDENTARIA ($)": float,
        "VC_RD resolución 011 de 2015": float,
        "VF_RD resolución 011 de 2015": float,
        "Valor a Favor delta ajuste RD": float,
        "Valor a Cargo delta ajuste RD": float,
        "VALOR A CARGO R026-2016 ($).": float,
        "VALOR A FAVOR R026-2016 ($).": float,
        "VALOR A FAVOR R029-2016 ($).": float,
        "RF039 resolución 039 de 2016": float,
        "RC039 resolución 039 de 2016": float,
        "Balance Final 029 de 2016": float,
        "Valor a cargo para comercializador. RES. 062 2013": float,
        "Valor a favor para generador. RES. 062 2013": float,
        "Valor del DE TIE. RES. 049 2018 (kWh)": float,
        "Valor del DE TIE. RES. 049 2018 ($)": float,
        "Magnitud desviación despacho. RES. 060 2019 (kWh)": float,
        "Valor Desviación Despacho. RES. 060 2019 ($)": float,
        "Magnitud desviación Redespacho. RES. 060 2019(kWh)": float,
        "Valor Desviación ReDespacho. RES. 060 2019 (kWh)": float,
        "Desviación Generación Variable. RES. 060 2019(kWh)": float,
        "Alivio desviaciones Res. CREG 060/2019 ($)": float,
        "VALOR PAGO AJUSTE RES. 140 2017 ($)": float,
        "VALOR COBRO AJUSTE RES. 140 2017 ($)": float,
        "VALOR PAGO EXCEDENTE RES. 140 2017 ($)": float,
        "VALOR COBRO FALTANTE RES. 140 2017 ($)": float,
    },
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
        total = total.set_index(["AGENTE"]).stack().reset_index()
        total = total.rename(columns={"level_1": "CONCEPTO", 0: "VALOR"})
        ret_cols = ["AGENTE", "CONCEPTO", "VALOR"]
        return total[ret_cols]
