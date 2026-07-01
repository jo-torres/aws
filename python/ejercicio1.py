def solicitar_datos():
    print("===== FORMULARIO PERSONAL =====")

    nombre = input("Ingrese su nombre: ")
    apellido = input("Ingrese su apellido: ")
    pais = input("Ingrese su país: ")
    hijas = input("Ingrese el nombre de sus hijas (separadas por coma si son varias): ")
    pais_conocer = input("¿Qué país le gustaría conocer?: ")

    return nombre, apellido, pais, hijas, pais_conocer


def mostrar_datos(nombre, apellido, pais, hijas, pais_conocer):
    print("\n===== DATOS INGRESADOS =====")
    print(f"Nombre           : {nombre}")
    print(f"Apellido         : {apellido}")
    print(f"País             : {pais}")
    print(f"Nombre(s) hija(s): {hijas}")
    print(f"País por conocer : {pais_conocer}")


# Programa principal
nombre, apellido, pais, hijas, pais_conocer = solicitar_datos()
mostrar_datos(nombre, apellido, pais, hijas, pais_conocer)