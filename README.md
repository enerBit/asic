# ASIC

Interfaz de línea de comandos para descargar los archivos de las publicaciones de liquidación del Mercado de Energía Mayorista MEM realizadas por el Administrador del Sistema de Intercambios Comerciales ASIC.

------

> **Requiere acceso al FTP del ASIC en `xmftps.xm.com.co`**

------

## Ejemplos

Antes de poder usar los comandos que usan el servir FTP de XM, debes proveer la información de autenticación (se recomienda usar variables de entorno).

```txt
$Env:ASIC_FTPS_HOST = "xmftps.xm.com.co"
$Env:ASIC_FTPS_USER = "Isamdnt\88888888"
$Env:ASIC_FTPS_PASSWORD = "m1MuySeCreTAClAV."
$Env:ASIC_FTPS_PORT = 210
```

1. Cuales versiones de liquidación se han publicado en los últimos días:

```txt
> asic pubs --days-old 20
Listing latest published settlements by ASIC in the last 20 days
2022-05:TX3 -- published: 2022-07-19
2022-06:TXR -- published: 2022-07-05
```

1. Listar los archivos publicados para los meses de mayo y junio de 2022 con version de liquidación .tx3:

```txt
> asic list --month 2022-06 --month 2022-05 --version .tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\adem0501.Tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\adem0502.Tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\adem0503.Tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\adem0504.Tx3
          ...
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\pep0530.tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\pep0531.tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\sntie05.tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\afac05.tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\trsm05.tx3
\INFORMACION_XM\PUBLICOK\SIC\COMERCIA\2022-05\ldcbmr05.tx3
```

1. Descargar los archivos publicados para los meses de mayo y junio de 2022 con version de liquidación .tx3 a la carpeta local `./asic-files/`:

```txt
> asic download --month 2022-06 --month 2022-05 --version .tx3 asic-files
Dowloading files... ━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   6% 0:01:05
```


## CLI

Interfaz de línea de comandos (CLI).

### Instalación

1. Crear un ambiente virtual de python

```sh
python -m venv venv
```

1. Activar el ambiente virtual

```sh
.\venv\Scripts\activate
```

1. Instalar paquete

```sh
python -m pip install asic
```

### Ejecución

La CLI misma ofrece ayuda de como usarla.
La opción `--help` imprime la ayuda de cada comando en la pantalla.

```txt
> asic --help 

 Usage: asic [OPTIONS] COMMAND [ARGS]...

 Commands:
  download           Download files from asic's ftp server to local DESTINATION folder.
  list               List files from asic's ftp server.
  pubs               Check latest published settlements in asic's website. 
```

```txt
> asic pubs --help

 Usage: asic pubs [OPTIONS]

 Check latest published settlements in asic's website.
```

## Contribuir
