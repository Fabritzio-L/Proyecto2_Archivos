import json
import os


class GestorIndice:
    def __init__(self, ruta_indice: str = "data/indice.json"):
        self.ruta_indice = ruta_indice
        os.makedirs(os.path.dirname(self.ruta_indice), exist_ok=True)

    def cargar_indice(self):
        #Retorna el diccionario {id_str: numero_registro}
        if not os.path.exists(self.ruta_indice):
            return {}
        try:
            with open(self.ruta_indice, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                if not isinstance(datos, dict):
                    raise ValueError("Formato de índice inválido.")
                return {str(k): int(v) for k, v in datos.items()}
        except (json.JSONDecodeError, ValueError) as e:
            raise RuntimeError(f"El archivo de índice está corrupto: {e}") from e
        except PermissionError as e:
            raise PermissionError("No hay permisos de lectura para indice.json.") from e

    def guardar_indice(self, indice: dict[str, int]):
        #Guarda el diccionario de índice en formato JSON UTF-8
        try:
            with open(self.ruta_indice, "w", encoding="utf-8") as archivo:
                json.dump(indice, archivo, indent=4, ensure_ascii=False)
        except PermissionError as e:
            raise PermissionError("No hay permisos de escritura para indice.json.") from e

    def obtener_numero_registro(self, id_contacto: int):
        indice = self.cargar_indice()
        return indice.get(str(id_contacto))

    def registrar_id(self, id_contacto: int, numero_registro: int):
        indice = self.cargar_indice()
        indice[str(id_contacto)] = numero_registro
        self.guardar_indice(indice)