import tkinter as tk
from tkinter import simpledialog
import urllib.request
import urllib.parse
import json
import random
import threading
 
CANVAS_W = 460
CANVAS_H = 620
ROAD_LEFT = 90
ROAD_RIGHT = 370
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH / LANE_COUNT
CAR_W = 34
CAR_H = 56
 
# Códigos de clima WMO usados por Open-Meteo
WEATHER_DESC = {
    0: "despejado", 1: "despejado", 2: "parcialmente nublado", 3: "nublado",
    45: "niebla", 48: "niebla",
    51: "llovizna", 53: "llovizna", 55: "llovizna",
    56: "llovizna helada", 57: "llovizna helada",
    61: "lluvia", 63: "lluvia", 65: "lluvia",
    66: "lluvia helada", 67: "lluvia helada",
    71: "nieve", 73: "nieve", 75: "nieve", 77: "nieve",
    80: "lluvia", 81: "lluvia", 82: "lluvia",
    85: "nieve", 86: "nieve",
    95: "tormenta", 96: "tormenta", 99: "tormenta",
}
 
 
def categorize(code):
    desc = WEATHER_DESC.get(code, "despejado")
    if desc == "despejado":
        return "despejado"
    if desc in ("parcialmente nublado", "nublado"):
        return "nublado"
    if desc == "niebla":
        return "niebla"
    if desc in ("llovizna", "llovizna helada", "lluvia", "lluvia helada"):
        return "lluvia"
    if desc == "nieve":
        return "nieve"
    if desc == "tormenta":
        return "tormenta"
    return "despejado"
 
 
def fetch_weather(city):
    """Consulta geocodificación + clima actual en Open-Meteo. Lanza excepción si falla."""
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode({
        "name": city, "count": 1, "language": "es"
    })
    with urllib.request.urlopen(geo_url, timeout=6) as resp:
        geo_data = json.loads(resp.read().decode())
    if not geo_data.get("results"):
        raise ValueError("Ciudad no encontrada")
    place = geo_data["results"][0]
    lat, lon = place["latitude"], place["longitude"]
    name = place.get("name", city)
 
    w_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
        "latitude": lat, "longitude": lon, "current_weather": "true"
    })
    with urllib.request.urlopen(w_url, timeout=6) as resp:
        w_data = json.loads(resp.read().decode())
    cw = w_data["current_weather"]
    code = cw["weathercode"]
    return {
        "condition": categorize(code),
        "desc": WEATHER_DESC.get(code, "despejado"),
        "is_day": bool(cw.get("is_day", 1)),
        "temperature": cw.get("temperature"),
        "city_name": name,
    }
 
 
class CarreraClimatica:
    THEMES = {
        "despejado_dia":   {"sky": "#87CEEB", "grass": "#4caf50", "road": "#555555"},
        "despejado_noche": {"sky": "#0b1026", "grass": "#1b3a1b", "road": "#333333"},
        "nublado_dia":     {"sky": "#a9b7c6", "grass": "#5a7a52", "road": "#555555"},
        "nublado_noche":   {"sky": "#1c1f2b", "grass": "#243924", "road": "#333333"},
        "lluvia_dia":      {"sky": "#607d8b", "grass": "#3d5c3d", "road": "#3a3a3a"},
        "lluvia_noche":    {"sky": "#101820", "grass": "#1a2a1a", "road": "#2a2a2a"},
        "nieve_dia":       {"sky": "#dfefff", "grass": "#f0f8ff", "road": "#7a7a85"},
        "nieve_noche":     {"sky": "#1b2436", "grass": "#c9d6e3", "road": "#5a5a65"},
        "niebla_dia":      {"sky": "#c9c9c9", "grass": "#7a8a7a", "road": "#606060"},
        "niebla_noche":    {"sky": "#2b2b2b", "grass": "#2a332a", "road": "#3a3a3a"},
        "tormenta_dia":    {"sky": "#3a3f4b", "grass": "#33422e", "road": "#2f2f2f"},
        "tormenta_noche":  {"sky": "#0a0a12", "grass": "#141d12", "road": "#232323"},
    }
 
    def __init__(self, root):
        self.root = root
        self.root.title("🏎️ Carrera Climática")
        self.root.configure(bg="#111")
        self.root.resizable(False, False)
 
        self.weather = {"condition": "despejado", "desc": "despejado", "is_day": True,
                         "temperature": None, "city_name": "—"}
 
        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, bg="#87CEEB", highlightthickness=0)
        self.canvas.pack()
 
        self.info_label = tk.Label(root, text="Obteniendo clima...", font=("Helvetica", 10),
                                    bg="#111", fg="#eee")
        self.info_label.pack(fill="x")
 
        self.root.bind("<Left>", lambda e: self.set_input(-1))
        self.root.bind("<Right>", lambda e: self.set_input(1))
        self.root.bind("<KeyRelease-Left>", lambda e: self.clear_input(-1))
        self.root.bind("<KeyRelease-Right>", lambda e: self.clear_input(1))
        self.root.bind("<space>", lambda e: self.restart() if self.game_over else None)
 
        self.reset_state()
        self.ask_city_and_fetch()
        self.loop()
 
    def set_input(self, d):
        self.move_dir = d
 
    def clear_input(self, d):
        if self.move_dir == d:
            self.move_dir = 0
 
    def reset_state(self):
        self.player_x = ROAD_LEFT + ROAD_WIDTH / 2 - CAR_W / 2
        self.move_dir = 0
        self.obstacles = []
        self.particles = []
        self.score = 0
        self.speed = 4
        self.spawn_timer = 0
        self.game_over = False
        self.dash_offset = 0
        self.flash = 0
 
    def ask_city_and_fetch(self):
        city = simpledialog.askstring(
            "Ubicación", "¿En qué ciudad estás? (para ambientar el clima)",
            initialvalue="Santiago, Chile", parent=self.root
        )
        if not city:
            city = "Santiago, Chile"
        self.info_label.config(text=f"Obteniendo clima de {city}...")
        threading.Thread(target=self._fetch_thread, args=(city,), daemon=True).start()
 
    def _fetch_thread(self, city):
        try:
            data = fetch_weather(city)
            self.weather = data
            msg = f"📍 {data['city_name']} — {data['desc'].capitalize()}"
            if data["temperature"] is not None:
                msg += f", {data['temperature']}°C"
            self.root.after(0, lambda: self.info_label.config(text=msg))
        except Exception:
            self.root.after(0, lambda: self.info_label.config(
                text="⚠️ No se pudo obtener el clima (revisa tu conexión). Usando ambiente despejado."))
 
    def theme_key(self):
        suffix = "dia" if self.weather["is_day"] else "noche"
        return f"{self.weather['condition']}_{suffix}"
 
    # ---------- Loop principal ----------
    def loop(self):
        if not self.game_over:
            self.update_game()
        self.render()
        self.root.after(33, self.loop)
 
    def update_game(self):
        self.player_x += self.move_dir * 7
        self.player_x = max(ROAD_LEFT + 4, min(ROAD_RIGHT - CAR_W - 4, self.player_x))
 
        self.speed = 4 + self.score // 200
        self.dash_offset = (self.dash_offset + self.speed) % 40
 
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            lane = random.randint(0, LANE_COUNT - 1)
            x = ROAD_LEFT + lane * LANE_WIDTH + (LANE_WIDTH - CAR_W) / 2
            color = random.choice(["#e53935", "#fdd835", "#5e35b1", "#00897b", "#f4511e"])
            self.obstacles.append({"x": x, "y": -CAR_H, "color": color})
            self.spawn_timer = max(18, 45 - self.score // 100)
 
        for obs in self.obstacles:
            obs["y"] += self.speed + 2
        self.obstacles = [o for o in self.obstacles if o["y"] < CANVAS_H + CAR_H]
 
        for obs in self.obstacles:
            if self.check_collision(obs):
                self.game_over = True
 
        self.score += 1
        self.update_particles()
 
    def check_collision(self, obs):
        px1, px2 = self.player_x, self.player_x + CAR_W
        py1, py2 = CANVAS_H - CAR_H - 20, CANVAS_H - 20
        ox1, ox2 = obs["x"], obs["x"] + CAR_W
        oy1, oy2 = obs["y"], obs["y"] + CAR_H
        return px1 < ox2 and px2 > ox1 and py1 < oy2 and py2 > oy1
 
    def update_particles(self):
        cond = self.weather["condition"]
        if cond in ("lluvia", "tormenta"):
            for _ in range(3):
                self.particles.append({"x": random.randint(0, CANVAS_W), "y": -10, "type": "rain"})
        elif cond == "nieve":
            self.particles.append({"x": random.randint(0, CANVAS_W), "y": -10, "type": "snow",
                                    "drift": random.uniform(-1, 1)})
 
        for p in self.particles:
            if p["type"] == "rain":
                p["y"] += 22
            else:
                p["y"] += 3
                p["x"] += p.get("drift", 0)
        self.particles = [p for p in self.particles if p["y"] < CANVAS_H]
 
        if cond == "tormenta" and random.random() < 0.02:
            self.flash = 3
        if self.flash > 0:
            self.flash -= 1
 
    # ---------- Render ----------
    def render(self):
        self.canvas.delete("all")
        theme = self.THEMES.get(self.theme_key(), self.THEMES["despejado_dia"])
 
        sky_color = "#ffffff" if self.flash > 0 else theme["sky"]
        self.canvas.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=sky_color, outline="")
 
        if self.weather["is_day"] and self.weather["condition"] in ("despejado", "nublado"):
            self.canvas.create_oval(370, 30, 420, 80, fill="#ffe082", outline="")
        elif not self.weather["is_day"]:
            self.canvas.create_oval(370, 30, 410, 70, fill="#f5f5f5", outline="")
 
        self.canvas.create_rectangle(0, 0, ROAD_LEFT, CANVAS_H, fill=theme["grass"], outline="")
        self.canvas.create_rectangle(ROAD_RIGHT, 0, CANVAS_W, CANVAS_H, fill=theme["grass"], outline="")
        self.canvas.create_rectangle(ROAD_LEFT, 0, ROAD_RIGHT, CANVAS_H, fill=theme["road"], outline="")
 
        for lane in range(1, LANE_COUNT):
            x = ROAD_LEFT + lane * LANE_WIDTH
            y = -40 + self.dash_offset
            while y < CANVAS_H:
                self.canvas.create_rectangle(x - 2, y, x + 2, y + 20, fill="#eeeeee", outline="")
                y += 40
 
        if self.weather["condition"] == "niebla":
            self.canvas.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill="#dddddd", stipple="gray50", outline="")
 
        for p in self.particles:
            if p["type"] == "rain":
                self.canvas.create_line(p["x"], p["y"], p["x"] - 3, p["y"] + 12, fill="#bcd4e6", width=2)
            else:
                self.canvas.create_oval(p["x"], p["y"], p["x"] + 4, p["y"] + 4, fill="white", outline="")
 
        for obs in self.obstacles:
            self.draw_car(obs["x"], obs["y"], obs["color"])
 
        self.draw_car(self.player_x, CANVAS_H - CAR_H - 20, "#2979ff")
 
        self.canvas.create_text(70, 20, text=f"🏁 {self.score}", fill="white", font=("Helvetica", 14, "bold"))
 
        if self.game_over:
            self.canvas.create_rectangle(60, 240, CANVAS_W - 60, 380, fill="#000000", stipple="gray25", outline="")
            self.canvas.create_text(CANVAS_W / 2, 280, text="💥 ¡Chocaste!", fill="white", font=("Helvetica", 20, "bold"))
            self.canvas.create_text(CANVAS_W / 2, 315, text=f"Puntaje final: {self.score}", fill="white", font=("Helvetica", 14))
            self.canvas.create_text(CANVAS_W / 2, 350, text="Presiona ESPACIO para reintentar", fill="#ffd54f", font=("Helvetica", 11))
 
    def draw_car(self, x, y, color):
        self.canvas.create_rectangle(x, y + 8, x + CAR_W, y + CAR_H - 8, fill=color, outline="#111", width=1)
        self.canvas.create_rectangle(x + 5, y, x + CAR_W - 5, y + 18, fill=color, outline="#111", width=1)
        self.canvas.create_rectangle(x + 6, y + 4, x + CAR_W - 6, y + 14, fill="#bbdefb", outline="")
        self.canvas.create_rectangle(x - 2, y + 10, x + 2, y + 22, fill="#111", outline="")
        self.canvas.create_rectangle(x + CAR_W - 2, y + 10, x + CAR_W + 2, y + 22, fill="#111", outline="")
        self.canvas.create_rectangle(x - 2, y + CAR_H - 24, x + 2, y + CAR_H - 12, fill="#111", outline="")
        self.canvas.create_rectangle(x + CAR_W - 2, y + CAR_H - 24, x + CAR_W + 2, y + CAR_H - 12, fill="#111", outline="")
 
    def restart(self):
        self.reset_state()
 
 
def main():
    root = tk.Tk()
    CarreraClimatica(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()
 