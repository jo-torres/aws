import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


# Función que realiza el cálculo
def calcular():

    try:
        numero1 = float(txt_numero1.get())
        numero2 = float(txt_numero2.get())

        operacion = combo_operacion.get()

        if operacion == "Suma":
            resultado = numero1 + numero2

        elif operacion == "Resta":
            resultado = numero1 - numero2

        elif operacion == "Multiplicación":
            resultado = numero1 * numero2

        elif operacion == "División":

            if numero2 == 0:
                messagebox.showerror(
                    "Error",
                    "No se puede dividir por cero."
                )
                return

            resultado = numero1 / numero2

        else:
            messagebox.showwarning(
                "Aviso",
                "Seleccione una operación."
            )
            return

        # Mostrar el resultado sin decimales si es un número entero
        if resultado.is_integer():
            lbl_resultado.config(
                text=f"Resultado: {int(resultado)}"
            )
        else:
            lbl_resultado.config(
                text=f"Resultado: {resultado:.2f}"
            )

    except ValueError:

        messagebox.showerror(
            "Error",
            "Ingrese solamente números."
        )

def limpiar():

    txt_numero1.delete(0, tk.END)
    txt_numero2.delete(0, tk.END)

    combo_operacion.set("")

    lbl_resultado.config(text="Resultado:")

    txt_numero1.focus()

# ---------------- VENTANA ----------------

ventana = tk.Tk()

ventana.title("Calculadora")

ventana.geometry("450x350")

titulo = tk.Label(
    ventana,
    text="Calculadora",
    font=("Arial", 18, "bold")
)

titulo.pack(pady=15)

# Primer número
tk.Label(
    ventana,
    text="Primer número"
).pack()

txt_numero1 = ttk.Entry(
    ventana,
    width=25
)

txt_numero1.pack(pady=5)

# Segundo número
tk.Label(
    ventana,
    text="Segundo número"
).pack()

txt_numero2 = ttk.Entry(
    ventana,
    width=25
)

txt_numero2.pack(pady=5)

# Operación
tk.Label(
    ventana,
    text="Seleccione una operación"
).pack()

combo_operacion = ttk.Combobox(
    ventana,
    values=[
        "Suma",
        "Resta",
        "Multiplicación",
        "División"
    ],
    state="readonly",
    width=22
)

combo_operacion.pack(pady=10)

# Frame para los botones
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=15)

# Botón Calcular
btn_calcular = ttk.Button(
    frame_botones,
    text="Calcular",
    command=calcular
)

btn_calcular.grid(row=0, column=0, padx=10)

# Botón Limpiar
btn_limpiar = ttk.Button(
    frame_botones,
    text="Limpiar",
    command=limpiar
)

btn_limpiar.grid(row=0, column=1, padx=10)

# Resultado
lbl_resultado = tk.Label(
    ventana,
    text="Resultado:",
    font=("Arial", 14, "bold")
)

lbl_resultado.pack(pady=20)

btn_salir = ttk.Button(
    frame_botones,
    text="Salir",
    command=ventana.destroy
)

btn_salir.grid(row=0, column=2, padx=10)

ventana.mainloop()