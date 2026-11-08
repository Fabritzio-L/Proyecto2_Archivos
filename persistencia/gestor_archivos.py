import os
from models.contacto import Contacto
from persistencia.gestor_indice import GestorIndice


class GestorArchivos:
    def __init__(self, ruta_datos: str = "data/contactos.dat", gestor_indice: GestorIndice = None):
        self.ruta_datos = ruta_datos
        self.gestor_indice = gestor_indice or GestorIndice()
        os.makedirs(os.path.dirname(self.ruta_datos), exist_ok=True)

    def _asegurar_archivo(self):
        if not os.path.exists(self.ruta_datos):
            with open(self.ruta_datos, "wb") as _:
                pass

    def agregar_contacto(self, contacto: Contacto):
        #Agrega un contacto al final, actualiza el índice
        if self.gestor_indice.obtener_numero_registro(contacto.id) is not None:
            raise ValueError(f"El contacto con ID {contacto.id} ya existe.")

        self._asegurar_archivo()
        try:
            with open(self.ruta_datos, "rb+") as archivo:
                archivo.seek(0, os.SEEK_END)
                posicion_bytes = archivo.tell()

                if posicion_bytes % Contacto.TAMANO_REGISTRO != 0:
                    raise RuntimeError("El archivo contactos.dat está corrupto.")

                numero_registro = posicion_bytes // Contacto.TAMANO_REGISTRO
                datos_utf8 = contacto.a_registro_fijo().encode("utf-8")
                archivo.write(datos_utf8)

            self.gestor_indice.registrar_id(contacto.id, numero_registro)
            return numero_registro, posicion_bytes
        except PermissionError as e:
            raise PermissionError("No hay permisos para escribir en contactos.dat.") from e

    def buscar_por_id(self, id_contacto: int):
        #Consulta el índice, hace seek() directo 
        numero_registro = self.gestor_indice.obtener_numero_registro(id_contacto)
        if numero_registro is None:
            raise KeyError(f"No existe ningún contacto con el ID {id_contacto}.")

        if not os.path.exists(self.ruta_datos):
            raise FileNotFoundError("El archivo contactos.dat no existe.")

        desplazamiento = numero_registro * Contacto.TAMANO_REGISTRO
        try:
            with open(self.ruta_datos, "rb") as archivo:
                archivo.seek(desplazamiento)
                posicion_actual = archivo.tell()
                bloque = archivo.read(Contacto.TAMANO_REGISTRO)

                if len(bloque) < Contacto.TAMANO_REGISTRO:
                    raise RuntimeError("Registro incompleto o archivo contactos.dat truncado.")

                contacto = Contacto.desde_bytes(bloque)
                return contacto, numero_registro, posicion_actual
        except PermissionError as e:
            raise PermissionError("No hay permisos de lectura en contactos.dat.") from e

    def modificar_contacto(self, contacto: Contacto):
        #Sobrescribe únicamente el registro en su posición sin reescribir el resto del archivo
        numero_registro = self.gestor_indice.obtener_numero_registro(contacto.id)
        if numero_registro is None:
            raise KeyError(f"No se puede modificar: el ID {contacto.id} no existe en el índice.")

        if not os.path.exists(self.ruta_datos):
            raise FileNotFoundError("El archivo contactos.dat no existe.")

        desplazamiento = numero_registro * Contacto.TAMANO_REGISTRO
        try:
            with open(self.ruta_datos, "rb+") as archivo:
                archivo.seek(desplazamiento)
                posicion_actual = archivo.tell()
                datos_utf8 = contacto.a_registro_fijo().encode("utf-8")
                archivo.write(datos_utf8)
                return numero_registro, posicion_actual
        except PermissionError as e:
            raise PermissionError("No hay permisos de escritura en contactos.dat.") from e

    def listar_todos(self):
        #Recorre los registros registrados en el índice para exportaciones JSON/PDF
        indice = self.gestor_indice.cargar_indice()
        contactos = []
        for id_str in indice:
            contacto, _, _ = self.buscar_por_id(int(id_str))
            contactos.append(contacto)
        return contactos