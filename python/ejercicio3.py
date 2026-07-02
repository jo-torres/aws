import tkinter as tk
from tkinter import ttk

# Función que dibuja el rombo
def dibujar_rombo():

    resultado.delete("1.0", tk.END)

    n = int(txt_numero.get())

    # Parte superior
    for i in range(1, n + 1):

        espacios = " " * (n - i)
        estrellas = "*" * (2 * i - 1)

        resultado.insert(tk.END, espacios + estrellas + "\n")

    # Parte inferior
    for i in range(n - 1, 0, -1):

        espacios = " " * (n - i)
        estrellas = "*" * (2 * i - 1)

        resultado.insert(tk.END, espacios + estrellas + "\n")


# ---------------- Ventana ----------------

ventana = tk.Tk()

ventana.title("Dibujar Rombo")

ventana.geometry("500x500")

titulo = tk.Label(
    ventana,
    text="Dibujar un Rombo",
    font=("Arial", 16, "bold")
)

titulo.pack(pady=15)

tk.Label(
    ventana,
    text="Ingrese un número:"
).pack()

txt_numero = ttk.Entry(
    ventana,
    width=20
)

txt_numero.pack(pady=10)

boton = ttk.Button(
    ventana,
    text="Dibujar",
    command=dibujar_rombo
)

boton.pack(pady=10)

resultado = tk.Text(
    ventana,
    width=30,
    height=18,
    font=("Courier New", 14)
)

resultado.pack(pady=15)

ventana.mainloop()