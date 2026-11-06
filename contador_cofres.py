"""
Contador de cofres para Fortnite (atajo manual)
------------------------------------------------
- Flecha arriba -> suma 1
- Flecha abajo  -> resta 1
- Puedes escribir un número y pulsar "Aplicar" (o Enter) para cambiar el contador;
  desde ese valor sigue contando normalmente.
- El número se guarda solo y se recupera al abrir el programa.

No lee ni toca el juego: solo detecta teclas del teclado, así que es seguro
con Easy Anti-Cheat. Funciona en Windows y no necesita instalar nada extra
(solo Python 3 con tkinter, que viene incluido).

Consejo: juega en "Pantalla completa en ventana" (Windowed Fullscreen) para
poder ver el contador encima del juego.
"""

import json
import os
import sys
import tkinter as tk
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
# -----------------------------------------------

try:
    import ctypes
    _get_key = ctypes.windll.user32.GetAsyncKeyState
except Exception:  # No es Windows
    _get_key = None


def tecla_pulsada(vk):
    if _get_key is None:
        return False
    return bool(_get_key(vk) & 0x8000)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Contador de cofres")
        self.root.geometry("300x280")
        self.root.resizable(False, False)
        self.root.configure(bg="#1b1d2a")
        self.root.attributes("-topmost", True)

        self.cuenta = self.cargar()
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

        self.var_top = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="Siempre visible", variable=self.var_top,
                       command=self.cambiar_top, bg=fondo, fg=texto,
                       selectcolor=fondo, activebackground=fondo,
                       activeforeground=texto).pack()

        tk.Button(root, text="Reiniciar a 0", command=self.reiniciar).pack(pady=6)

        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.revisar_teclas()

    # --- Persistencia ---
    def cargar(self):
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                return int(json.load(f).get("cuenta", 0))
        except Exception:
            return 0

    def guardar(self):
        try:
            with open(ARCHIVO, "w", encoding="utf-8") as f:
                json.dump({"cuenta": self.cuenta}, f)
        except Exception:
            pass

    # --- Lógica ---
    def refrescar(self):
        self.lbl.config(text=str(self.cuenta))
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

    def cambiar_top(self):
        self.root.attributes("-topmost", self.var_top.get())

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
