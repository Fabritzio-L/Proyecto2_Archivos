import os
import zipfile
from datetime import datetime


class ServicioArchivosSistema:
    def __init__(self, ruta_datos: str = "data/contactos.dat", ruta_indice: str = "data/indice.json"):
        self.ruta_datos = ruta_datos
        self.ruta_indice = ruta_indice

    def crear_respaldo_zip(self, carpeta_destino: str = "exports"):
        #Comprime contactos.dat e indice.json y retorna los tamaños original y comprimido
        if not os.path.exists(self.ruta_datos) or not os.path.exists(self.ruta_indice):
            raise FileNotFoundError("Deben existir contactos.dat e indice.json para crear el respaldo.")

        os.makedirs(carpeta_destino, exist_ok=True)
        marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_zip = os.path.join(carpeta_destino, f"respaldo_{marca_tiempo}.zip")

        tamano_original = os.stat(self.ruta_datos).st_size + os.stat(self.ruta_indice).st_size

        try:
            with zipfile.ZipFile(ruta_zip, "w", compression=zipfile.ZIP_DEFLATED) as archivo_zip:
                archivo_zip.write(self.ruta_datos, arcname="contactos.dat")
                archivo_zip.write(self.ruta_indice, arcname="indice.json")
        except PermissionError as e:
            raise PermissionError("No hay permisos para crear el archivo de respaldo ZIP.") from e

        tamano_comprimido = os.stat(ruta_zip).st_size
        return {
            "ruta_zip": ruta_zip,
            "tamano_original": tamano_original,
            "tamano_comprimido": tamano_comprimido,
        }

    def obtener_metadatos(self):
        #Obtiene tamaño, fecha de modificación y permisos
        if not os.path.exists(self.ruta_datos):
            return {
                "archivo": self.ruta_datos,
                "existe": False,
                "tamano_bytes": 0,
                "ultima_modificacion": "No creado aún",
                "permiso_lectura": False,
                "permiso_escritura": False,
            }

        estadisticas = os.stat(self.ruta_datos)
        fecha_mod = datetime.fromtimestamp(estadisticas.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        lectura = os.access(self.ruta_datos, os.R_OK)
        escritura = os.access(self.ruta_datos, os.W_OK)

        return {
            "archivo": self.ruta_datos,
            "existe": True,
            "tamano_bytes": estadisticas.st_size,
            "ultima_modificacion": fecha_mod,
            "permiso_lectura": lectura,
            "permiso_escritura": escritura,
        }