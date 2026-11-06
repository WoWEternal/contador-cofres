"""
Contador de cofres para Fortnite (atajo manual)
------------------------------------------------
- Flecha arriba -> suma 1
- Flecha abajo  -> resta 1
- Puedes escribir un número y pulsar "Aplicar" (o Enter) para cambiar el contador;
  desde ese valor sigue contando normalmente.
- Botón "Mostrar": abre un contador pequeño (plantilla del cofre + número con
  la fuente Retro Blendy) y minimiza la ventana principal. Arrastra el
  contador con el ratón para moverlo.
  Clic derecho sobre el contador: abrir la ventana principal u ocultarlo.
- El número y la posición del contador se guardan solos.

No lee ni toca el juego: solo detecta teclas del teclado, así que es seguro
con Easy Anti-Cheat. Funciona en Windows y no necesita instalar nada extra
(solo Python 3 con tkinter, que viene incluido).

Consejo: juega en "Pantalla completa en ventana" (Windowed Fullscreen) para
poder ver el contador encima del juego.
"""

import json
import os
import re
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

# ---------------- Configuración ----------------
VK_SUMAR = 0x26   # Flecha arriba
VK_RESTAR = 0x28  # Flecha abajo
NOMBRE_SUMAR = "↑"
NOMBRE_RESTAR = "↓"
INTERVALO_MS = 25  # cada cuánto se revisan las teclas
ARCHIVO = os.path.join(
    os.path.dirname(os.path.abspath(sys.argv[0])), "contador_cofres.json"
)

# Colores del contador pequeño
COLOR_TRANSPARENTE = "#010203"  # se vuelve transparente en Windows
COLOR_BORDE = "#6b7689"
COLOR_FONDO = "#161f29"
COLOR_NUMERO = "#66f2cf"

# Plantilla y fuente
CARPETA_PLANTILLAS = "plantillas"    # plantilla_30.png ... plantilla_100.png
BASE_ANCHO = 440                     # ancho (px) de la plantilla al 100 %
ESCALA_MIN, ESCALA_MAX, ESCALA_PASO = 30, 100, 5
ESCALA_INICIAL = 60                  # tamaño por defecto del contador (%)
ICONO_ICO = "icono.ico"
ICONO_PNG = "icono.png"
CARPETA_FUENTES = "fuentes"          # aquí va "Retro Blendy.otf"
FUENTE_RESPALDO = "Segoe UI"         # si no se encuentra Retro Blendy
# Espacio (en píxeles de la plantilla) donde se escribe el número:
# izquierda, arriba, derecha, abajo
AREA_NUMERO = (130, 20, 408, 92)
TAM_FUENTE_MAX = 50                  # tamaño al 100 %; se reduce si no cabe
# -----------------------------------------------


def ruta_recurso(*partes):
    """Busca un archivo junto al programa o dentro del .exe empaquetado."""
    bases = [os.path.dirname(os.path.abspath(sys.argv[0]))]
    if getattr(sys, "_MEIPASS", None):
        bases.append(sys._MEIPASS)
    bases.append(os.path.dirname(os.path.abspath(__file__)))
    for base in bases:
        ruta = os.path.join(base, *partes)
        if os.path.exists(ruta):
            return ruta
    return None


def cargar_plantilla(escala):
    """Carga la imagen de la plantilla cuyo tamaño se acerque más a `escala`."""
    carpeta = ruta_recurso(CARPETA_PLANTILLAS)
    if not carpeta:
        return None
    mejor = None
    for nombre in os.listdir(carpeta):
        m = re.fullmatch(r"plantilla_(\d+)\.png", nombre)
        if m:
            dif = abs(int(m.group(1)) - escala)
            if mejor is None or dif < mejor[0]:
                mejor = (dif, nombre)
    if mejor is None:
        return None
    try:
        return tk.PhotoImage(file=os.path.join(carpeta, mejor[1]))
    except tk.TclError:
        return None


def cargar_fuente_retro(root):
    """Registra Retro Blendy (sin instalarla) y devuelve su nombre de familia."""
    carpeta = ruta_recurso(CARPETA_FUENTES)
    if not carpeta or _get_key is None:
        return FUENTE_RESPALDO
    antes = set(tkfont.families(root))
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.lower().endswith((".otf", ".ttf")) and "blendy" in nombre.lower():
            try:
                # 0x10 = FR_PRIVATE: solo existe mientras corre el programa
                ctypes.windll.gdi32.AddFontResourceExW(
                    os.path.join(carpeta, nombre), 0x10, 0)
            except Exception:
                continue
            nuevas = set(tkfont.families(root)) - antes
            if nuevas:
                return sorted(nuevas)[0]
            if "Retro Blendy" in tkfont.families(root):
                return "Retro Blendy"
    return FUENTE_RESPALDO

try:
    import ctypes
    _get_key = ctypes.windll.user32.GetAsyncKeyState
except Exception:  # No es Windows
    _get_key = None


def tecla_pulsada(vk):
    if _get_key is None:
        return False
    return bool(_get_key(vk) & 0x8000)


def pildora(canvas, x0, y0, x1, y1, color):
    """Dibuja un rectángulo con los extremos totalmente redondeados."""
    r = (y1 - y0) / 2
    canvas.create_oval(x0, y0, x0 + 2 * r, y1, fill=color, outline=color)
    canvas.create_oval(x1 - 2 * r, y0, x1, y1, fill=color, outline=color)
    canvas.create_rectangle(x0 + r, y0, x1 - r, y1, fill=color, outline=color)


def dibujar_cofre(canvas, x, y, s):
    """Dibuja un cofre en (x, y) dentro de una caja de 100x90 escalada por s."""
    def p(px, py):
        return x + px * s, y + py * s

    def rect(x0, y0, x1, y1, fill, outline="#5a2d0c", w=2):
        a, b = p(x0, y0)
        c, d = p(x1, y1)
        canvas.create_rectangle(a, b, c, d, fill=fill, outline=outline, width=w)

    madera = "#b5622e"
    madera_osc = "#8f4a22"
    oro = "#ffc22e"
    oro_osc = "#f0961a"

    # Tapa abovedada
    a, b = p(14, 6)
    c, d = p(86, 58)
    canvas.create_arc(a, b, c, d, start=0, extent=180, fill=madera,
                      outline="#5a2d0c", width=2)
    # Cuerpo
    rect(14, 32, 86, 78, madera_osc)
    # Tablas de la tapa
    for yy in (22, 32):
        a, b = p(24, yy)
        c, d = p(76, yy)
        canvas.create_line(a, b, c, d, fill=madera_osc, width=2)
    # Bandas verticales de oro
    rect(14, 18, 28, 78, oro)
    rect(72, 18, 86, 78, oro)
    # Banda horizontal central
    rect(8, 38, 92, 54, oro)
    # Franja inferior
    rect(10, 68, 90, 80, oro_osc)
    # Remaches
    for px, py in ((14, 46), (86, 46), (16, 74), (84, 74)):
        a, b = p(px, py)
        canvas.create_oval(a - 2 * s, b - 2 * s, a + 2 * s, b + 2 * s,
                           fill=oro_osc, outline="")
    # Cerradura
    a, b = p(40, 34)
    c, d = p(60, 62)
    canvas.create_rectangle(a, b, c, d, fill=oro, outline="#5a2d0c", width=2)
    a, b = p(46, 41)
    c, d = p(54, 49)
    canvas.create_oval(a, b, c, d, fill="#3a1d08", outline="")
    a, b = p(48.5, 46)
    c, d = p(51.5, 56)
    canvas.create_rectangle(a, b, c, d, fill="#3a1d08", outline="")


class Contador:
    """Ventana pequeña: plantilla del cofre + número, sin bordes y siempre visible."""

    ALTO_RESPALDO = 76

    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=COLOR_TRANSPARENTE)
        try:
            self.win.attributes("-transparentcolor", COLOR_TRANSPARENTE)
        except tk.TclError:
            pass  # solo existe en Windows

        self.imagen = cargar_plantilla(app.escala)

        alto = self.imagen.height() if self.imagen else self.ALTO_RESPALDO
        ancho = self.imagen.width() if self.imagen else 200
        self.canvas = tk.Canvas(self.win, width=ancho, height=alto,
                                bg=COLOR_TRANSPARENTE, highlightthickness=0,
                                cursor="fleur")
        self.canvas.pack()
        self.fuente = tkfont.Font(family=app.familia_fuente,
                                  size=-TAM_FUENTE_MAX, weight="normal")

        self.menu = tk.Menu(self.win, tearoff=0)
        self.menu.add_command(label="Abrir ventana principal",
                              command=self.app.abrir_principal)
        self.menu.add_command(label="Ocultar contador", command=self.app.ocultar)

        self.canvas.bind("<ButtonPress-1>", self.empezar_arrastre)
        self.canvas.bind("<B1-Motion>", self.arrastrar)
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.app.guardar())
        self.canvas.bind("<Button-3>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))

        self.dibujar()
        x, y = self.app.pos
        self.win.geometry(f"+{x}+{y}")

    def dibujar(self):
        texto = str(self.app.cuenta)
        k = 1.0
        if self.imagen:
            k = self.imagen.width() / BASE_ANCHO
            izq, arr, der, aba = (v * k for v in AREA_NUMERO)
            self.canvas.config(width=self.imagen.width(),
                               height=self.imagen.height())
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=self.imagen, anchor="nw")
        else:
            # Respaldo si falta plantilla.png: pastilla dibujada con código
            ancho_t = tkfont.Font(family=self.app.familia_fuente,
                                  size=-TAM_FUENTE_MAX).measure(texto)
            ancho = 28 + 72 + 22 + ancho_t + 34
            self.canvas.config(width=ancho)
            self.canvas.delete("all")
            pildora(self.canvas, 2, 2, ancho - 2, self.ALTO_RESPALDO - 2, COLOR_BORDE)
            pildora(self.canvas, 5, 5, ancho - 5, self.ALTO_RESPALDO - 5, COLOR_FONDO)
            dibujar_cofre(self.canvas, 26, 11, 0.62)
            izq, arr, der, aba = 28 + 72 + 10, 5, ancho - 20, self.ALTO_RESPALDO - 5

        # Tamaño del número: crece con el contador y se reduce si no cabe
        tam = max(8, int(min(TAM_FUENTE_MAX * k, (aba - arr) * 0.95)))
        self.fuente.config(size=-tam)
        while tam > 8 and self.fuente.measure(texto) > der - izq:
            tam -= 1
            self.fuente.config(size=-tam)
        self.canvas.create_text((izq + der) / 2, (arr + aba) / 2, text=texto,
                                anchor="center", font=self.fuente, fill=COLOR_NUMERO)

    def cambiar_escala(self):
        self.imagen = cargar_plantilla(self.app.escala)
        self.dibujar()

    def empezar_arrastre(self, e):
        self._dx = e.x_root - self.win.winfo_x()
        self._dy = e.y_root - self.win.winfo_y()

    def arrastrar(self, e):
        x, y = e.x_root - self._dx, e.y_root - self._dy
        self.win.geometry(f"+{x}+{y}")
        self.app.pos = (x, y)

    def destruir(self):
        self.win.destroy()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Contador de cofres")
        self.root.geometry("300x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#1b1d2a")

        self.poner_icono()
        self.familia_fuente = cargar_fuente_retro(root)
        self.pos = (60, 60)
        self.escala = ESCALA_INICIAL
        self.cuenta = self.cargar()
        self.contador = None
        self.prev_sumar = False
        self.prev_restar = False

        fondo = "#1b1d2a"
        texto = "#e8e8f0"

        tk.Label(root, text="COFRES ABIERTOS", bg=fondo, fg="#8f9bff",
                 font=("Segoe UI", 12, "bold")).pack(pady=(14, 0))

        self.lbl = tk.Label(root, text=str(self.cuenta), bg=fondo, fg="#ffd24d",
                            font=("Segoe UI", 54, "bold"))
        self.lbl.pack()

        fila = tk.Frame(root, bg=fondo)
        fila.pack(pady=4)
        tk.Button(fila, text=f"-1 ({NOMBRE_RESTAR})", width=10,
                  command=self.restar).pack(side="left", padx=4)
        tk.Button(fila, text=f"+1 ({NOMBRE_SUMAR})", width=10,
                  command=self.sumar).pack(side="left", padx=4)

        fila2 = tk.Frame(root, bg=fondo)
        fila2.pack(pady=10)
        tk.Label(fila2, text="Cambiar a:", bg=fondo, fg=texto).pack(side="left")
        self.entrada = tk.Entry(fila2, width=7, justify="center",
                                font=("Segoe UI", 12))
        self.entrada.pack(side="left", padx=5)
        self.entrada.bind("<Return>", lambda e: self.aplicar())
        tk.Button(fila2, text="Aplicar", command=self.aplicar).pack(side="left")

        fila_t = tk.Frame(root, bg=fondo)
        fila_t.pack(pady=(2, 0))
        tk.Label(fila_t, text="Tamaño del contador:", bg=fondo,
                 fg=texto).pack(side="left")
        self.lbl_escala = tk.Label(fila_t, text=f"{self.escala}%", bg=fondo,
                                   fg="#ffd24d", width=5,
                                   font=("Segoe UI", 10, "bold"))
        self.lbl_escala.pack(side="left")
        self.slider = tk.Scale(root, from_=ESCALA_MIN, to=ESCALA_MAX,
                               resolution=ESCALA_PASO, orient="horizontal",
                               showvalue=False, length=240, bg=fondo,
                               troughcolor="#2a2d40", highlightthickness=0,
                               command=self.cambiar_escala)
        self.slider.set(self.escala)
        self.slider.pack()

        fila3 = tk.Frame(root, bg=fondo)
        fila3.pack(pady=6)
        self.btn_mostrar = tk.Button(fila3, text="Mostrar", width=10,
                                     command=self.alternar)
        self.btn_mostrar.pack(side="left", padx=4)
        tk.Button(fila3, text="Reiniciar a 0", width=12,
                  command=self.reiniciar).pack(side="left", padx=4)

        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.revisar_teclas()

    # --- Persistencia ---
    def cargar(self):
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.pos = (int(datos.get("x", 60)), int(datos.get("y", 60)))
            esc = int(datos.get("escala", ESCALA_INICIAL))
            self.escala = max(ESCALA_MIN, min(ESCALA_MAX, esc))
            return int(datos.get("cuenta", 0))
        except Exception:
            return 0

    def guardar(self):
        try:
            with open(ARCHIVO, "w", encoding="utf-8") as f:
                json.dump({"cuenta": self.cuenta, "escala": self.escala,
                           "x": self.pos[0], "y": self.pos[1]}, f)
        except Exception:
            pass

    def poner_icono(self):
        ico, png = ruta_recurso(ICONO_ICO), ruta_recurso(ICONO_PNG)
        if ico and _get_key is not None:
            try:
                self.root.iconbitmap(ico)
                return
            except tk.TclError:
                pass
        if png:
            try:
                self._icono = tk.PhotoImage(file=png)
                self.root.iconphoto(True, self._icono)
            except tk.TclError:
                pass

    def cambiar_escala(self, valor):
        nueva = int(float(valor))
        self.lbl_escala.config(text=f"{nueva}%")
        if nueva == self.escala:
            return
        self.escala = nueva
        if self.contador is not None:
            self.contador.cambiar_escala()
        self.guardar()

    # --- Contador pequeño ---
    def alternar(self):
        if self.contador is None:
            self.mostrar()
        else:
            self.ocultar()

    def mostrar(self):
        if self.contador is None:
            self.contador = Contador(self)
        self.btn_mostrar.config(text="Ocultar")
        self.root.iconify()  # minimiza la ventana grande

    def ocultar(self):
        if self.contador is not None:
            self.contador.destruir()
            self.contador = None
        self.btn_mostrar.config(text="Mostrar")
        self.root.deiconify()
        self.guardar()

    def abrir_principal(self):
        self.root.deiconify()
        self.root.lift()

    # --- Lógica ---
    def refrescar(self):
        self.lbl.config(text=str(self.cuenta))
        if self.contador is not None:
            self.contador.dibujar()
        self.guardar()

    def sumar(self):
        self.cuenta += 1
        self.refrescar()

    def restar(self):
        if self.cuenta > 0:
            self.cuenta -= 1
            self.refrescar()

    def aplicar(self):
        valor = self.entrada.get().strip()
        try:
            nuevo = int(valor)
            if nuevo < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Número no válido",
                                   "Escribe un número entero, 0 o mayor.")
            return
        self.cuenta = nuevo
        self.entrada.delete(0, "end")
        self.refrescar()
        self.root.focus_set()  # quita el foco de la caja de texto

    def reiniciar(self):
        if messagebox.askyesno("Reiniciar", "¿Poner el contador en 0?"):
            self.cuenta = 0
            self.refrescar()

    def revisar_teclas(self):
        sumar = tecla_pulsada(VK_SUMAR)
        restar = tecla_pulsada(VK_RESTAR)
        if sumar and not self.prev_sumar:
            self.sumar()
        if restar and not self.prev_restar:
            self.restar()
        self.prev_sumar = sumar
        self.prev_restar = restar
        self.root.after(INTERVALO_MS, self.revisar_teclas)

    def cerrar(self):
        self.guardar()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
