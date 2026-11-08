from UI.ventana_principal import VentanaPrincipal


def main():
    app = VentanaPrincipal()
    app.after(200, lambda: app.on_verificar_integridad(silencioso=True))
    app.mainloop()


if __name__ == "__main__":
    main()