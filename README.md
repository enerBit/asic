# ASIC

Interfaz de línea de comandos para descargar los archivos de las publicaciones de liquidación del Mercado de Energía Mayorista MEM realizadas por el Administrador del Sistema de Intercambios Comerciales ASIC.

------

> **Requiere acceso al FTP del ASIC en `xmftps.xm.com.co`**

------
## 📝 Archivo de configuración necesario
El sistema requiere que definas la variable de entorno `ASIC_FILE_CONFIG_PATH` apuntando a la ruta del archivo .jsonl que contiene la configuración de los tipos de archivos soportados. 
Este archivo debe contener objetos JSON en formato newline-delimited (un JSON por línea).

#### Ejemplo de variable de entorno
```txt
# Windows
$Env:ASIC_FILE_CONFIG_PATH = "C:\Users\Usuario\Documents\asic_file_config.jsonl"

# Linux
export ASIC_FILE_CONFIG_PATH="/home/Usuario/asic_file_config.jsonl"

# Mac
export ASIC_FILE_CONFIG_PATH="/Users/Usuario/asic_file_config.jsonl"
```
### 📋Estructura esperada:
```json
{"code":"adem", "visibility": "public","name_pattern":"(?P<kind>adem)(?P<name_month>[0-9]{2})(?P<name_day>[0-9]{2}).(?P<ext_versioned>[a-zA-Z0-9]+)", "location_pattern":"/RUTA/PUBLICA/DEL/FTP/(?P<location_year>[0-9]{4})-(?P<location_month>[0-9]{2})/","description":"Los archivos de demanda comercial"}
```


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

2. Listar los archivos publicados para los meses de mayo y junio de 2022 con version de liquidación .tx3:

```txt
> asic list --month 2022-06 --month 2022-05 --version .tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\adem0501.Tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\adem0502.Tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\adem0503.Tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\adem0504.Tx3
          ...
\RUTA\PUBLICA\DEL\FTP\2022-05\pep0530.tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\pep0531.tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\sntie05.tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\afac05.tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\trsm05.tx3
\RUTA\PUBLICA\DEL\FTP\2022-05\ldcbmr05.tx3
```

3. Descargar los archivos publicados para los meses de mayo y junio de 2022 con version de liquidación .tx3 a la carpeta local `./asic-files/`:

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

### ⚠️ PARA TENER EN CUENTA ⚠️

Tener presente que no se está realizando la verificación de certificados del servidor de XM **neptuno.xm.com.co** al consultar las versiones de liquidación publicadas usando el comando **asic pubs**.

## Tidy data

Los *datos prolijos* ("tidy data" en inglés) son una forma estándar de relacionar el significado de un conjunto de datos a su estructura.
Un conjunto de datos está prolijo o desprolijo dependiendo de cómo se relacionan las filas, columnas y tablas con las observaciones, las variables y los tipos.

En *datos prolijos*:

1. Cada variable es una columna; cada columna es una variable.

1. Cada observación es una fila; cada fila es una observación.

1. Cada valor es una celda; cada celda es un valor único.

Mas detalles en el articulo original [Tidy data][tidy-data]

Esta es la tercera forma normal de Codd, pero con las restricciones enmarcadas en el lenguaje estadístico y el enfoque puesto en un único conjunto de datos en lugar de los muchos conjuntos de datos conectados comunes en las bases de datos relacionales.
Los *datos desprolijos* son cualquier otra disposición de los datos.

[tidy-data]: <http://www.jstatsoft.org/v59/i10/> "Hadley Wickham (2014). Tidy data. The Journal of Statistical Software, 59."

## Contribuir
