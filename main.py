import ventana_principal


def main():
    app = ventana_principal.VentanaPrincipal()
    app.registrar_evento("Aplicación iniciada. Esperando verificación SHA-256...")
    app.mainloop()


if __name__ == "__main__":
    main()