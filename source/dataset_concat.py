import pandas as pd
import os
import argparse

## Configuración del parser de argumentos ##
parser = argparse.ArgumentParser(
    description="Concatena todos los .csvs de /data en un dataset final."
)

parser.add_argument(
    "--out",
    type=str,
    required=True,
    help="Nombre del archivo de salida (por ejemplo: data_vuelos.csv)"
)

args = parser.parse_args()

## ------------------------------------ ##

# Carpeta donde están los CSV
carpeta = "./data"

# Verificar que la carpeta existe
if not os.path.exists(carpeta):
    print(f"Error: La carpeta '{carpeta}' no existe")
    exit(1)

# Lista de todos los archivos CSV en la carpeta
archivos_csv = [f for f in os.listdir(carpeta) if f.endswith(".csv")]

if not archivos_csv:
    print(f"No se encontraron archivos CSV en '{carpeta}'")
    exit(1)

# Lista para ir guardando los DataFrames
dfs = []

print(f"Concatenando {len(archivos_csv)} archivos CSV...")

for archivo in archivos_csv:
    ruta_completa = os.path.join(carpeta, archivo)
    try:
        df = pd.read_csv(ruta_completa)
        dfs.append(df)
        print(f"{archivo} ({len(df)} filas)")
    except Exception as e:
        print(f"Error al leer {archivo}: {e}")

# Concatenar todos los DataFrames
df_concatenado = pd.concat(dfs, ignore_index=True)

# Crear carpeta de salida si no existe
os.makedirs("dataset", exist_ok=True)

# Guardar en un nuevo CSV
ruta_salida = f"dataset/{args.out}"
df_concatenado.to_csv(ruta_salida, index=False, encoding="utf-8")

print(f"\nConcatenados {len(dfs)} archivos CSV en '{ruta_salida}'.")
print(f"Total de filas: {len(df_concatenado)}")