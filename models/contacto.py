class Contacto:
    LEN_ID = 10
    LEN_NOMBRE = 35
    LEN_TELEFONO = 15
    LEN_CORREO = 35
    LEN_CIUDAD = 25
    TAMANO_REGISTRO = LEN_ID + LEN_NOMBRE + LEN_TELEFONO + LEN_CORREO + LEN_CIUDAD  # 120 bytes

    def __init__(self, id_contacto: int, nombre: str, telefono: str, correo: str, ciudad: str):
        self.id = int(id_contacto)
        self.nombre = nombre.strip()
        self.telefono = telefono.strip()
        self.correo = correo.strip()
        self.ciudad = ciudad.strip()

    @staticmethod
    def _ajustar_campo(valor: str, largo_bytes: int):
        #Si excede el máximo y rellena con espacios usando ljust
        texto = str(valor).strip()
        while len(texto.encode("utf-8")) > largo_bytes:
            texto = texto[:-1]
        espacios_faltantes = largo_bytes - len(texto.encode("utf-8"))
        return texto.ljust(len(texto) + espacios_faltantes)

    def a_registro_fijo(self):
        #Convierte el contacto en una cadena de longitud fija exacta
        return (
            self._ajustar_campo(str(self.id), self.LEN_ID)
            + self._ajustar_campo(self.nombre, self.LEN_NOMBRE)
            + self._ajustar_campo(self.telefono, self.LEN_TELEFONO)
            + self._ajustar_campo(self.correo, self.LEN_CORREO)
            + self._ajustar_campo(self.ciudad, self.LEN_CIUDAD)
        )

    @classmethod
    def desde_bytes(cls, bloque_bytes: bytes):
        #Reconstruye un objeto Contacto a partir de los 120 bytes leídos del archivo
        if len(bloque_bytes) != cls.TAMANO_REGISTRO:
            raise ValueError("El bloque leído no coincide con el tamaño fijo del registro.")

        p1 = cls.LEN_ID
        p2 = p1 + cls.LEN_NOMBRE
        p3 = p2 + cls.LEN_TELEFONO
        p4 = p3 + cls.LEN_CORREO

        id_str = bloque_bytes[0:p1].decode("utf-8").strip()
        nombre = bloque_bytes[p1:p2].decode("utf-8").strip()
        telefono = bloque_bytes[p2:p3].decode("utf-8").strip()
        correo = bloque_bytes[p3:p4].decode("utf-8").strip()
        ciudad = bloque_bytes[p4:].decode("utf-8").strip()

        return cls(int(id_str), nombre, telefono, correo, ciudad)

    def a_diccionario(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "correo": self.correo,
            "ciudad": self.ciudad,
        }