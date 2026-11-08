import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from contacto import Contacto


class ServicioExportacion:
    def __init__(
        self,
        ruta_json: str = "exportados/contactos_exportados.json",
        ruta_pdf: str = "exportados/reporte_contactos.pdf",
    ):
        self.ruta_json = ruta_json
        self.ruta_pdf = ruta_pdf
        os.makedirs(os.path.dirname(self.ruta_json), exist_ok=True)

    def exportar_a_json(self, lista_contactos: list[Contacto]):
        #Exporta todos los contactos a un archivo JSON en UTF-8
        datos = [c.a_diccionario() for c in lista_contactos]
        try:
            with open(self.ruta_json, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            return self.ruta_json
        except PermissionError as e:
            raise PermissionError("No hay permisos para escribir el archivo JSON exportado.") from e

    def _dibujar_encabezado_tabla(self, c: canvas.Canvas, y: int):
        #Dibuja los títulos de las columnas y una línea divisoria en la posición Y actual.
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y, "ID")
        c.drawString(85, y, "Nombre")
        c.drawString(230, y, "Teléfono")
        c.drawString(315, y, "Correo")
        c.drawString(470, y, "Ciudad")
        c.line(40, y - 5, 555, y - 5)
        return y - 20

    def generar_pdf_desde_json(self):
        #Lee el archivo JSON exportado y genera el reporte PDF 
        if not os.path.exists(self.ruta_json):
            raise FileNotFoundError("Primero debe exportar los contactos a JSON antes de generar el PDF.")

        try:
            with open(self.ruta_json, "r", encoding="utf-8") as archivo:
                contactos = json.load(archivo)
        except json.JSONDecodeError as e:
            raise RuntimeError("El archivo JSON exportado está corrupto.") from e
        except PermissionError as e:
            raise PermissionError("No hay permisos de lectura para el archivo JSON exportado.") from e

        try:
            c = canvas.Canvas(self.ruta_pdf)
            y = 790

            # Título y fecha de generación
            c.setFont("Helvetica-Bold", 16)
            c.drawString(40, y, "Reporte de Agenda de Contactos")
            y -= 20

            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            c.setFont("Helvetica", 10)
            c.drawString(40, y, f"Fecha de generación: {fecha_actual}")
            y -= 30

            # Encabezados de columnas
            y = self._dibujar_encabezado_tabla(c, y)
            c.setFont("Helvetica", 9)

            # Filas de contactos
            for contacto in contactos:
                if y < 50:
                    c.showPage()
                    y = 790
                    y = self._dibujar_encabezado_tabla(c, y)
                    c.setFont("Helvetica", 9)

                c.drawString(40, y, str(contacto.get("id", ""))[:8])
                c.drawString(85, y, str(contacto.get("nombre", ""))[:25])
                c.drawString(230, y, str(contacto.get("telefono", ""))[:14])
                c.drawString(315, y, str(contacto.get("correo", ""))[:28])
                c.drawString(470, y, str(contacto.get("ciudad", ""))[:16])
                y -= 18

            c.save()
            return self.ruta_pdf

        except PermissionError as e:
            raise PermissionError("No se pudo guardar el PDF. Verifique que no esté abierto en otro programa.") from e