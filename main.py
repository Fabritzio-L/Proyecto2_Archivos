import ventana_principal


def main():
    app = ventana_principal.VentanaPrincipal()
    app.after(200, lambda: app.on_verificar_integridad(silencioso=True))
    app.mainloop()


if __name__ == "__main__":
    main()