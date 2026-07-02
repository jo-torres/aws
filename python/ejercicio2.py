import tkinter as tk
from tkinter import ttk

# Función para contar caracteres
def contar_caracteres():
    frase = txt_frase.get()

    cantidad = len(frase)

    lbl_resultado.config(
        text=f"La frase tiene {cantidad} caracteres."
    )

# ---------------- VENTANA ----------------

ventana = tk.Tk()
ventana.title("Contador de Caracteres")
ventana.geometry("500x250")

titulo = tk.Label(
    ventana,
    text="Contador de Caracteres",
    font=("Arial", 16, "bold")
)
titulo.pack(pady=15)

tk.Label(
    ventana,
    text="Ingrese una frase:"
).pack()

txt_frase = ttk.Entry(
    ventana,
    width=50
)
txt_frase.pack(pady=10)

btn = ttk.Button(
    ventana,
    text="Contar caracteres",
    command=contar_caracteres
)
btn.pack(pady=10)

lbl_resultado = tk.Label(
    ventana,
    text="",
    font=("Arial", 12)
)
lbl_resultado.pack(pady=15)

ventana.mainloop()