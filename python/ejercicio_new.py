"""
🌳 Árbol de Hábitos
Una app de Tkinter donde un árbol crece visualmente cada vez que
cumples un hábito. Si te saltas un día, el árbol se marchita un poco
y tienes que empezar de nuevo la racha.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import random
from datetime import date, datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arbol_habito_data.json")


class ArbolHabitos:
    def __init__(self, root):
        self.root = root
        self.root.title("🌳 Árbol de Hábitos")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.data = self.load_data()

        self.build_ui()
        self.draw_tree()

    # ---------- Persistencia ----------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "habito": "Mi hábito",
            "streak": 0,
            "total": 0,
            "last_date": None,
            "wilted": False,
        }

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # ---------- Interfaz ----------
    def build_ui(self):
        title_frame = tk.Frame(self.root, bg="#1a1a2e")
        title_frame.pack(pady=(15, 5))

        self.habit_label = tk.Label(
            title_frame, text=self.data["habito"], font=("Georgia", 16, "bold"),
            fg="#eaeaea", bg="#1a1a2e"
        )
        self.habit_label.pack(side="left")

        edit_btn = tk.Button(
            title_frame, text="✏️", command=self.edit_habit_name, bd=0,
            bg="#1a1a2e", fg="#eaeaea", activebackground="#1a1a2e", cursor="hand2"
        )
        edit_btn.pack(side="left", padx=5)

        self.canvas = tk.Canvas(self.root, width=460, height=400, bg="#16213e", highlightthickness=0)
        self.canvas.pack(pady=10)

        stats_frame = tk.Frame(self.root, bg="#1a1a2e")
        stats_frame.pack(pady=5)

        self.streak_label = tk.Label(stats_frame, text="", font=("Helvetica", 12), fg="#f4a259", bg="#1a1a2e")
        self.streak_label.pack()

        self.total_label = tk.Label(stats_frame, text="", font=("Helvetica", 10), fg="#8d99ae", bg="#1a1a2e")
        self.total_label.pack()

        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 10, "italic"), fg="#8d99ae", bg="#1a1a2e")
        self.status_label.pack(pady=5)

        self.mark_btn = tk.Button(
            self.root, text="✅ Marcar como cumplido hoy", font=("Helvetica", 12, "bold"),
            bg="#4caf50", fg="white", activebackground="#43a047", bd=0, padx=15, pady=10,
            cursor="hand2", command=self.mark_today
        )
        self.mark_btn.pack(pady=10)

        reset_btn = tk.Button(
            self.root, text="🔄 Reiniciar árbol", font=("Helvetica", 9),
            bg="#1a1a2e", fg="#8d99ae", bd=0, cursor="hand2", command=self.reset_tree
        )
        reset_btn.pack()

        self.update_labels()

    def edit_habit_name(self):
        new_name = simpledialog.askstring(
            "Editar hábito", "¿Qué hábito quieres seguir?", initialvalue=self.data["habito"]
        )
        if new_name:
            self.data["habito"] = new_name
            self.habit_label.config(text=new_name)
            self.save_data()

    # ---------- Lógica ----------
    def check_wilt_status(self):
        """Si se saltó al menos un día completo, la racha se reinicia."""
        if self.data["last_date"] is None:
            return
        last = datetime.strptime(self.data["last_date"], "%Y-%m-%d").date()
        gap = (date.today() - last).days
        if gap > 1:
            self.data["streak"] = 0
            self.data["wilted"] = True
        else:
            self.data["wilted"] = False

    def mark_today(self):
        today_str = date.today().isoformat()
        if self.data["last_date"] == today_str:
            messagebox.showinfo("Ya registrado", "¡Ya marcaste tu hábito hoy! Vuelve mañana 🌱")
            return

        self.check_wilt_status()

        self.data["streak"] += 1
        self.data["total"] += 1
        self.data["last_date"] = today_str
        self.data["wilted"] = False
        self.save_data()

        self.update_labels()
        self.draw_tree()

    def reset_tree(self):
        if messagebox.askyesno("Reiniciar", "¿Seguro que quieres reiniciar tu árbol? Perderás tu progreso."):
            self.data["streak"] = 0
            self.data["total"] = 0
            self.data["last_date"] = None
            self.data["wilted"] = False
            self.save_data()
            self.update_labels()
            self.draw_tree()

    def update_labels(self):
        self.check_wilt_status()
        self.save_data()

        streak = self.data["streak"]
        total = self.data["total"]

        if self.data["wilted"] and streak == 0 and total > 0:
            self.streak_label.config(text="🥀 Racha perdida — vuelve a empezar", fg="#c96f6f")
        else:
            self.streak_label.config(text=f"🔥 Racha actual: {streak} día{'s' if streak != 1 else ''}", fg="#f4a259")

        self.total_label.config(text=f"Total de veces cumplido: {total}")
        self.status_label.config(text=self.get_stage_message(streak))

        today_str = date.today().isoformat()
        if self.data["last_date"] == today_str:
            self.mark_btn.config(state="disabled", text="✅ ¡Hecho por hoy!", bg="#555")
        else:
            self.mark_btn.config(state="normal", text="✅ Marcar como cumplido hoy", bg="#4caf50")

    def get_stage_message(self, streak):
        if streak == 0:
            return "Una semilla espera ser plantada..."
        elif streak <= 2:
            return "Un pequeño brote está asomando 🌱"
        elif streak <= 5:
            return "Tu árbol empieza a tomar forma 🌿"
        elif streak <= 10:
            return "¡Está creciendo fuerte! 🌳"
        elif streak <= 20:
            return "Un árbol frondoso y saludable 🌳✨"
        else:
            return "¡Un árbol magnífico en flor! 🌸🌳"

    # ---------- Dibujo ----------
    def draw_tree(self):
        self.canvas.delete("all")
        w, h = 460, 400

        self.canvas.create_rectangle(0, 0, w, h, fill="#16213e", outline="")

        random.seed(42)
        for _ in range(30):
            x = random.randint(0, w)
            y = random.randint(0, h - 100)
            r = random.choice([1, 1, 2])
            self.canvas.create_oval(x, y, x + r, y + r, fill="#e0e0e0", outline="")
        random.seed()

        ground_y = h - 40
        self.canvas.create_rectangle(0, ground_y, w, h, fill="#2d3142", outline="")

        streak = self.data["streak"]
        wilted = self.data["wilted"] and streak == 0 and self.data["total"] > 0
        cx = w // 2

        if streak == 0 and self.data["total"] == 0:
            self.canvas.create_oval(cx - 8, ground_y - 10, cx + 8, ground_y + 5, fill="#8d6e63", outline="")
            self.canvas.create_text(cx, ground_y - 30, text="Planta tu primera semilla 🌱",
                                     fill="#8d99ae", font=("Helvetica", 10))
            return

        trunk_height = min(20 + streak * 8, 200)
        trunk_width = min(6 + streak * 0.8, 26)

        trunk_color = "#5d4037" if not wilted else "#4a3f3a"
        leaf_color = "#4caf50" if not wilted else "#7a7a5a"
        leaf_color2 = "#66bb6a" if not wilted else "#8a8a6a"

        trunk_top_y = ground_y - trunk_height

        self.canvas.create_polygon(
            cx - trunk_width / 2, ground_y,
            cx - trunk_width / 4, trunk_top_y,
            cx + trunk_width / 4, trunk_top_y,
            cx + trunk_width / 2, ground_y,
            fill=trunk_color, outline=""
        )

        if streak >= 6:
            branch_len = min(20 + streak * 2, 70)
            self.canvas.create_line(cx, trunk_top_y + 20, cx - branch_len, trunk_top_y - 10,
                                     fill=trunk_color, width=5)
            self.canvas.create_line(cx, trunk_top_y + 30, cx + branch_len, trunk_top_y - 5,
                                     fill=trunk_color, width=5)

        base_r = 0
        if streak >= 1:
            base_r = min(25 + streak * 3, 90)
            self.canvas.create_oval(cx - base_r, trunk_top_y - base_r * 1.3, cx + base_r, trunk_top_y + base_r * 0.3,
                                     fill=leaf_color, outline="")
        if streak >= 3:
            r2 = min(20 + streak * 2, 60)
            self.canvas.create_oval(cx - base_r - r2 * 0.6, trunk_top_y - base_r * 0.6,
                                     cx - base_r + r2 * 0.8, trunk_top_y + r2 * 0.5,
                                     fill=leaf_color2, outline="")
            self.canvas.create_oval(cx + base_r - r2 * 0.8, trunk_top_y - base_r * 0.6,
                                     cx + base_r + r2 * 0.6, trunk_top_y + r2 * 0.5,
                                     fill=leaf_color2, outline="")

        if streak >= 21 and not wilted:
            random.seed(streak)
            for _ in range(12):
                fx = cx + random.randint(-base_r, base_r)
                fy = trunk_top_y + random.randint(-int(base_r * 1.2), int(base_r * 0.2))
                self.canvas.create_oval(fx - 4, fy - 4, fx + 4, fy + 4, fill="#ffb6c1", outline="")
            random.seed()

        if wilted:
            for i in range(5):
                fx = cx - 60 + i * 30 + random.randint(-10, 10)
                fy = ground_y - random.randint(0, 15)
                self.canvas.create_oval(fx, fy, fx + 8, fy + 8, fill="#8a8a5a", outline="")


def main():
    root = tk.Tk()
    ArbolHabitos(root)
    root.mainloop()


if __name__ == "__main__":
    main()