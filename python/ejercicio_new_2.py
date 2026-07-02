"""
👁️‍🗨️ Lector Accesible
Convierte texto pegado, imágenes cargadas o capturas de cámara en voz,
resaltando palabra por palabra mientras lee. Pensado para personas con
dislexia, baja visión, o cualquiera que prefiera escuchar en vez de leer.

INSTALACIÓN (ejecuta en tu terminal):
    pip install pyttsx3 pytesseract pillow opencv-python --break-system-packages

Además necesitas el motor OCR "Tesseract" instalado en tu sistema (no es
una librería de Python, es un programa aparte):
    - Windows: https://github.com/UB-Mannheim/tesseract/wiki
    - macOS:   brew install tesseract tesseract-lang
    - Linux:   sudo apt install tesseract-ocr tesseract-ocr-spa

Para usar tu CELULAR como cámara: instala una app como "Iriun Webcam" o
"DroidCam" en tu celular y su programa complementario en tu computador.
Una vez conectados, tu celular aparecerá como una cámara más (índice 1, 2...)
en el selector de cámara de esta app.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    Image = None
    ImageTk = None
    ImageOps = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import cv2
except ImportError:
    cv2 = None


class LectorAccesible:
    def __init__(self, root):
        self.root = root
        self.root.title("👁️‍🗨️ Lector Accesible")
        self.root.geometry("780x520")
        self.root.minsize(600, 420)
        self.root.resizable(True, True)
        self.root.configure(bg="#f4f6fb")

        self.engine = None
        self.reading = False
        self.cam = None
        self.cam_running = False
        self.last_frame = None
        self._word_token = None
        self.current_read_widget = None

        self.font_size = tk.IntVar(value=18)
        self.rate = tk.IntVar(value=170)
        self.cam_index = tk.IntVar(value=0)

        self.build_ui()
        self.warn_missing_libs()

    # ---------------- Avisos ----------------
    def warn_missing_libs(self):
        faltantes = []
        if pyttsx3 is None:
            faltantes.append("pyttsx3 (voz)")
        if Image is None:
            faltantes.append("pillow (imágenes)")
        if pytesseract is None:
            faltantes.append("pytesseract (OCR)")
        if cv2 is None:
            faltantes.append("opencv-python (cámara)")
        if faltantes:
            messagebox.showwarning(
                "Faltan librerías",
                "Algunas funciones estarán deshabilitadas porque falta instalar:\n\n- "
                + "\n- ".join(faltantes)
                + "\n\nRevisa las instrucciones en la parte superior del archivo .py"
            )

    # ---------------- Interfaz ----------------
    def build_ui(self):
        top = tk.Frame(self.root, bg="#f4f6fb")
        top.pack(fill="x", pady=10, padx=10)
        tk.Label(top, text="👁️‍🗨️ Lector Accesible", font=("Georgia", 20, "bold"),
                 bg="#f4f6fb", fg="#22223b").pack(side="left")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_texto = tk.Frame(self.tabs, bg="#ffffff")
        self.tab_imagen = tk.Frame(self.tabs, bg="#ffffff")
        self.tab_camara = tk.Frame(self.tabs, bg="#ffffff")

        self.tabs.add(self.tab_texto, text="✍️ Pegar texto")
        self.tabs.add(self.tab_imagen, text="🖼️ Cargar imagen")
        self.tabs.add(self.tab_camara, text="📷 Cámara")

        self.build_tab_texto()
        self.build_tab_imagen()
        self.build_tab_camara()

        controls = tk.Frame(self.root, bg="#f4f6fb")
        controls.pack(fill="x", padx=10, pady=8)

        tk.Label(controls, text="Tamaño de letra:", bg="#f4f6fb").grid(row=0, column=0, padx=5)
        tk.Scale(controls, from_=12, to=40, orient="horizontal", variable=self.font_size,
                 command=self.update_font_size, length=130, bg="#f4f6fb").grid(row=0, column=1, padx=5)

        tk.Label(controls, text="Velocidad de voz:", bg="#f4f6fb").grid(row=0, column=2, padx=5)
        tk.Scale(controls, from_=80, to=280, orient="horizontal", variable=self.rate,
                 length=130, bg="#f4f6fb").grid(row=0, column=3, padx=5)

        self.play_btn = tk.Button(controls, text="🔊 Leer en voz alta", font=("Helvetica", 12, "bold"),
                                   bg="#4caf50", fg="white", command=self.toggle_read, padx=10, pady=6)
        self.play_btn.grid(row=0, column=4, padx=12)

        self.stop_btn_ref = tk.Button(controls, text="⏹ Detener", command=self.stop_reading, padx=10, pady=6)
        self.stop_btn_ref.grid(row=0, column=5, padx=5)

    def build_tab_texto(self):
        self.text_widget = tk.Text(self.tab_texto, wrap="word", font=("Helvetica", self.font_size.get()),
                                    padx=10, pady=10, undo=True, height=10)
        self.text_widget.pack(fill="x", padx=10, pady=10)
        self.text_widget.insert("1.0", "Pega aquí el texto que quieres escuchar...")
        self.text_widget.tag_config("resaltado", background="#ffe082")

    def build_tab_imagen(self):
        top = tk.Frame(self.tab_imagen, bg="#ffffff")
        top.pack(fill="x", pady=10)
        tk.Button(top, text="📂 Elegir imagen...", command=self.load_image_file,
                  bg="#3f51b5", fg="white", padx=10, pady=6).pack()

        self.image_preview = tk.Label(self.tab_imagen, bg="#eeeeee")
        self.image_preview.pack(pady=5)

        tk.Label(self.tab_imagen, text="Texto detectado:", bg="#ffffff",
                 font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10)
        self.image_text_widget = tk.Text(self.tab_imagen, wrap="word", height=8,
                                          font=("Helvetica", self.font_size.get()))
        self.image_text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.image_text_widget.tag_config("resaltado", background="#ffe082")

    def build_tab_camara(self):
        top = tk.Frame(self.tab_camara, bg="#ffffff")
        top.pack(fill="x", pady=10)

        tk.Label(top, text="Cámara #:", bg="#ffffff").pack(side="left", padx=(10, 2))
        tk.Spinbox(top, from_=0, to=4, width=3, textvariable=self.cam_index).pack(side="left")

        self.cam_btn = tk.Button(top, text="📷 Iniciar cámara", command=self.toggle_camera,
                                  bg="#3f51b5", fg="white", padx=10, pady=6)
        self.cam_btn.pack(side="left", padx=10)

        self.capture_btn = tk.Button(top, text="📸 Capturar y leer", command=self.capture_and_ocr,
                                      bg="#009688", fg="white", padx=10, pady=6, state="disabled")
        self.capture_btn.pack(side="left", padx=10)

        self.cam_label = tk.Label(self.tab_camara, bg="#000000")
        self.cam_label.pack(pady=5)

        tk.Label(self.tab_camara, text="Texto detectado:", bg="#ffffff",
                 font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10)
        self.cam_text_widget = tk.Text(self.tab_camara, wrap="word", height=6,
                                        font=("Helvetica", self.font_size.get()))
        self.cam_text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.cam_text_widget.tag_config("resaltado", background="#ffe082")

    def update_font_size(self, *_):
        size = self.font_size.get()
        self.text_widget.config(font=("Helvetica", size))
        self.image_text_widget.config(font=("Helvetica", size))
        self.cam_text_widget.config(font=("Helvetica", size))

    # ---------------- Imagen / OCR ----------------
    def load_image_file(self):
        if Image is None:
            messagebox.showerror("Falta una librería", "Instala pillow: pip install pillow --break-system-packages")
            return
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")])
        if not path:
            return
        img = Image.open(path)
        self.show_preview(img, self.image_preview)
        self.run_ocr(img, self.image_text_widget)

    def show_preview(self, pil_img, label_widget):
        preview = pil_img.copy()
        preview.thumbnail((420, 300))
        tk_img = ImageTk.PhotoImage(preview)
        label_widget.config(image=tk_img)
        label_widget.image = tk_img

    def preprocess_for_ocr(self, pil_img):
        """Mejora la imagen antes de mandarla al OCR: blanco y negro, más
        contraste, y la agranda si es muy chica. Esto ayuda mucho con fotos
        de cámara, que suelen venir borrosas o con poco contraste."""
        if ImageOps is None:
            return pil_img
        img = pil_img.convert("RGB")
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img, cutoff=1)
        w, h = img.size
        if max(w, h) < 1200:
            scale = 1200 / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        return img

    def run_ocr(self, pil_img, text_widget):
        if pytesseract is None:
            messagebox.showerror("Falta una librería",
                                  "Instala pytesseract y el motor Tesseract OCR (ver instrucciones arriba en el archivo).")
            return
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", "Reconociendo texto...")

        def worker():
            try:
                processed = self.preprocess_for_ocr(pil_img)
                text = pytesseract.image_to_string(processed, lang="spa+eng", config="--psm 6")
                if not text.strip():
                    text = "(No se detectó texto. Acerca más la cámara, mejora la luz, o asegúrate de que el texto esté derecho y enfocado.)"
            except Exception as e:
                text = f"[Error de OCR: {e}]\n\nAsegúrate de tener Tesseract instalado en tu sistema."

            def update():
                text_widget.delete("1.0", "end")
                text_widget.insert("1.0", text.strip())
            self.root.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    # ---------------- Cámara ----------------
    def toggle_camera(self):
        if cv2 is None or Image is None:
            messagebox.showerror("Falta una librería", "Instala opencv-python y pillow para usar la cámara.")
            return
        if not self.cam_running:
            self.cam = cv2.VideoCapture(self.cam_index.get())
            if not self.cam.isOpened():
                messagebox.showerror("Cámara no encontrada",
                                      "No se pudo acceder a esa cámara. Prueba otro número de cámara.")
                return
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cam_running = True
            self.cam_btn.config(text="⏹ Detener cámara")
            self.capture_btn.config(state="normal")
            self.update_camera_frame()
        else:
            self.cam_running = False
            self.cam_btn.config(text="📷 Iniciar cámara")
            self.capture_btn.config(state="disabled")
            if self.cam:
                self.cam.release()
            self.cam_label.config(image="")

    def update_camera_frame(self):
        if not self.cam_running or self.cam is None:
            return
        ret, frame = self.cam.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            self.last_frame = img
            preview = img.copy()
            preview.thumbnail((480, 360))
            tk_img = ImageTk.PhotoImage(preview)
            self.cam_label.config(image=tk_img)
            self.cam_label.image = tk_img
        self.root.after(30, self.update_camera_frame)

    def capture_and_ocr(self):
        if self.last_frame is None:
            return
        self.run_ocr(self.last_frame, self.cam_text_widget)

    # ---------------- Lectura en voz alta ----------------
    def current_widget(self):
        idx = self.tabs.index(self.tabs.select())
        if idx == 0:
            return self.text_widget
        elif idx == 1:
            return self.image_text_widget
        return self.cam_text_widget

    def toggle_read(self):
        if self.reading:
            self.stop_reading()
        else:
            self.start_reading()

    def start_reading(self):
        if pyttsx3 is None:
            messagebox.showerror("Falta una librería", "Instala pyttsx3: pip install pyttsx3 --break-system-packages")
            return
        widget = self.current_widget()
        text = widget.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Sin texto", "No hay texto para leer.")
            return

        widget.tag_remove("resaltado", "1.0", "end")
        widget.tag_add("resaltado", "1.0", "end")
        self.current_read_widget = widget
        self.reading = True
        self.play_btn.config(text="⏸ Leyendo...", bg="#ff9800", state="disabled")
        self.stop_btn_ref.config(state="disabled")
        # Forzamos que la interfaz se repinte AHORA, antes de bloquearse
        # con la lectura (que corre en este mismo hilo principal).
        self.root.update_idletasks()

        self._speak_now(text, self.rate.get())

    def _speak_now(self, text, rate):
        """Lee el texto de forma SÍNCRONA en el hilo principal. La ventana
        queda congelada mientras lee (no responde a clics), pero a cambio
        evitamos el crash fatal de Python que causaba correr pyttsx3 en un
        hilo aparte junto con Tkinter en este sistema."""
        try:
            # pyttsx3.init() guarda una caché interna (_activeEngines) y
            # devuelve el MISMO motor cada vez, aunque parezca que se crea
            # uno nuevo. Ese motor reciclado es el que se "rompe" después
            # de la primera lectura, así que forzamos que sea uno nuevo.
            try:
                if hasattr(pyttsx3, "_activeEngines"):
                    pyttsx3._activeEngines.pop(None, None)
            except Exception:
                pass

            engine = pyttsx3.init()
            self.engine = engine

            voices = engine.getProperty("voices")
            if not voices:
                messagebox.showerror(
                    "Sin voces instaladas",
                    "Windows no tiene ninguna voz de lectura instalada.\n"
                    "Ve a Configuración > Hora e idioma > Voz, y descarga una voz en español o inglés."
                )
            else:
                engine.setProperty("rate", rate)
                engine.setProperty("volume", 1.0)
                engine.say(text)
                engine.runAndWait()
                try:
                    engine.stop()
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("Error al leer en voz alta", str(e))
        finally:
            try:
                if hasattr(pyttsx3, "_activeEngines"):
                    pyttsx3._activeEngines.pop(None, None)
            except Exception:
                pass
            self.engine = None
            self.finish_reading()

    def highlight_word(self, widget, start, end):
        widget.tag_remove("resaltado", "1.0", "end")
        widget.tag_add("resaltado", start, end)
        widget.see(start)

    def finish_reading(self):
        self.reading = False
        self.play_btn.config(text="🔊 Leer en voz alta", bg="#4caf50", state="normal")
        self.stop_btn_ref.config(state="normal")
        if self.current_read_widget is not None:
            self.current_read_widget.tag_remove("resaltado", "1.0", "end")

    def stop_reading(self):
        self.reading = False
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass
        self.finish_reading()

    def on_close(self):
        self.cam_running = False
        if self.cam:
            self.cam.release()
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = LectorAccesible(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()