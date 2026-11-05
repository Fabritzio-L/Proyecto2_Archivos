import hashlib
import os


class ServicioIntegridad:
    def __init__(self, ruta_datos: str = "data/contactos.dat", ruta_hash: str = "data/contactos.sha256"):
        self.ruta_datos = ruta_datos
        self.ruta_hash = ruta_hash
        os.makedirs(os.path.dirname(self.ruta_hash), exist_ok=True)

    def calcular_sha256(self):
        #Calcula y retorna el hash SHA-256
        if not os.path.exists(self.ruta_datos):
            return ""
        sha256 = hashlib.sha256()
        try:
            with open(self.ruta_datos, "rb") as archivo:
                while bloque := archivo.read(4096):
                    sha256.update(bloque)
            return sha256.hexdigest()
        except PermissionError as e:
            raise PermissionError("No hay permisos de lectura para calcular el hash de contactos.dat.") from e

    def actualizar_hash(self):
        #recalcula el SHA-256 y lo guarda en contactos.sha256 
        nuevo_hash = self.calcular_sha256()
        if not nuevo_hash:
            return ""
        try:
            with open(self.ruta_hash, "w", encoding="utf-8") as archivo:
                archivo.write(nuevo_hash)
            return nuevo_hash
        except PermissionError as e:
            raise PermissionError("No hay permisos de escritura en contactos.sha256.") from e

    def verificar_integridad(self):
        #Compara el hash actual con el almacenado
        if not os.path.exists(self.ruta_datos):
            return True, "Archivo de datos aún no creado."

        if not os.path.exists(self.ruta_hash):
            return False, "No existe el archivo contactos.sha256 para validar la integridad."

        try:
            with open(self.ruta_hash, "r", encoding="utf-8") as archivo:
                hash_guardado = archivo.read().strip()
        except PermissionError as e:
            raise PermissionError("No hay permisos para leer contactos.sha256.") from e

        hash_actual = self.calcular_sha256()
        if hash_actual == hash_guardado:
            return True, f"Integridad verificada ({hash_actual[:12]}...)"
        return False, "¡Alerta! El archivo contactos.dat fue modificado fuera de la aplicación."