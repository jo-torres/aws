def solicitar_datos():
    datos = {
        "Nombre": input("Ingrese su nombre: "),
        "Apellido": input("Ingrese su apellido: "),
        "País": input("Ingrese su país: "),
        "Hijas": input("Ingrese el nombre de sus hijas: "),
        "País que desea conocer": input("¿Qué país desea conocer?: ")
    }

    return datos


def mostrar_datos(datos):
    print("\n===== RESUMEN =====")
    for clave, valor in datos.items():
        print(f"{clave}: {valor}")


# Programa principal
persona = solicitar_datos()
mostrar_datos(persona)