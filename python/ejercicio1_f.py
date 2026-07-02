import tkinter as tk
from tkinter import ttk

# Función que obtiene los datos y los muestra
def guardar_datos():

    nombre = txt_nombre.get()
    apellido = txt_apellido.get()
    pais = txt_pais.get()
    hijas = txt_hijas.get()
    pais_conocer = txt_pais_conocer.get()

    resultado.config(
        text=f"""
DATOS INGRESADOS

Nombre: {nombre}

Apellido: {apellido}

País: {pais}

Hija(s): {hijas}

País que deseas conocer: {pais_conocer}
"""
    )


# ---------------- VENTANA ----------------

ventana = tk.Tk()
ventana.title("Formulario Personal")
ventana.geometry("500x850")
ventana.resizable(False, False)

titulo = tk.Label(
    ventana,
    text="Formulario Personal",
    font=("Arial", 18, "bold")
)
titulo.pack(pady=15)

# Nombre
tk.Label(ventana, text="Nombre").pack()
txt_nombre = ttk.Entry(ventana, width=40)
txt_nombre.pack(pady=5)

# Apellido
tk.Label(ventana, text="Apellido").pack()
txt_apellido = ttk.Entry(ventana, width=40)
txt_apellido.pack(pady=5)

# País
tk.Label(ventana, text="País").pack()
txt_pais = ttk.Entry(ventana, width=40)
txt_pais.pack(pady=5)

# Hijas
tk.Label(ventana, text="Nombre de la(s) hija(s)").pack()
txt_hijas = ttk.Entry(ventana, width=40)
txt_hijas.pack(pady=5)

# País que desea conocer
tk.Label(ventana, text="País que deseas conocer").pack()
txt_pais_conocer = ttk.Entry(ventana, width=40)
txt_pais_conocer.pack(pady=5)

# Botón
boton = ttk.Button(
    ventana,
    text="Guardar",
    command=guardar_datos
)
boton.pack(pady=20)

# Resultado
resultado = tk.Label(
    ventana,
    text="",
    justify="left",
    font=("Arial", 11)
)
resultado.pack(pady=10)

ventana.mainloop()