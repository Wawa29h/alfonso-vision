#!/usr/bin/env python3
"""
app.py — Interfaz grafica (UI) del clasificador de imagenes CLIP.

Ejecutar:
    python app.py

Permite elegir un perfil de clasificador (general, animales, frutas,
verduras...), abrir una imagen y ver las probabilidades por categoria en
barras. La clasificacion corre en un hilo aparte para que la ventana no se
congele mientras carga el modelo o procesa la imagen.

Los perfiles se definen en clasificadores.py: al agregar uno nuevo, aparece
automaticamente en el menu desplegable de esta ventana.
"""

import queue
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from PIL import Image, ImageTk

import clasificadores
from motor import ErrorModelo, clasificar


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clasificador de imagenes - CLIP")
        self.geometry("860x580")
        self.minsize(760, 500)

        self.imagen_path: str | None = None
        self._preview = None          # referencia viva para que el GC no borre la imagen
        self._cola: queue.Queue = queue.Queue()
        self._ids = list(clasificadores.CLASIFICADORES.keys())

        self._construir_ui()

    # ---------------- construccion de la interfaz ----------------
    def _construir_ui(self):
        barra = ttk.Frame(self, padding=10)
        barra.pack(side="top", fill="x")

        ttk.Label(barra, text="Clasificador:").pack(side="left")
        self.combo = ttk.Combobox(
            barra, state="readonly", width=30,
            values=[c.nombre for c in clasificadores.CLASIFICADORES.values()],
        )
        self.combo.current(0)
        self.combo.pack(side="left", padx=(6, 16))

        ttk.Button(barra, text="Elegir imagen...", command=self.elegir_imagen).pack(side="left")
        self.btn_clasificar = ttk.Button(barra, text="Clasificar", command=self.clasificar_async)
        self.btn_clasificar.pack(side="left", padx=6)

        cuerpo = ttk.Frame(self, padding=(10, 0, 10, 10))
        cuerpo.pack(fill="both", expand=True)

        # panel izquierdo: vista previa de la imagen
        izq = ttk.LabelFrame(cuerpo, text="Imagen", padding=8)
        izq.pack(side="left", fill="both", expand=False)
        self.lbl_img = ttk.Label(
            izq, text="(sin imagen)\n\nUsa 'Elegir imagen...'",
            anchor="center", width=42, justify="center",
        )
        self.lbl_img.pack(fill="both", expand=True)

        # panel derecho: resultados
        der = ttk.LabelFrame(cuerpo, text="Resultados", padding=8)
        der.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.resultados = ttk.Frame(der)
        self.resultados.pack(fill="both", expand=True)

        # barra de estado inferior
        self.estado = tk.StringVar(value="Listo. Elige un clasificador y una imagen.")
        ttk.Label(self, textvariable=self.estado, relief="sunken", anchor="w",
                  padding=(8, 4)).pack(side="bottom", fill="x")

    # ---------------- acciones ----------------
    def elegir_imagen(self):
        path = filedialog.askopenfilename(
            title="Elegir imagen",
            filetypes=[
                ("Imagenes", "*.png *.jpg *.jpeg *.bmp *.webp *.gif"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not path:
            return
        self.imagen_path = path
        self._mostrar_preview(path)
        self.estado.set(f"Imagen: {path}")

    def _mostrar_preview(self, path):
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((340, 340))
            self._preview = ImageTk.PhotoImage(img)
            self.lbl_img.configure(image=self._preview, text="")
        except Exception as e:
            self.lbl_img.configure(image="", text=f"No se pudo abrir la imagen:\n{e}")

    def _clasificador_actual(self):
        return clasificadores.CLASIFICADORES[self._ids[self.combo.current()]]

    def clasificar_async(self):
        if not self.imagen_path:
            self.estado.set("Primero elige una imagen.")
            return

        perfil = self._clasificador_actual()
        self.btn_clasificar.configure(state="disabled")
        self.estado.set(f"Clasificando con '{perfil.nombre}'...")
        self._limpiar_resultados()

        def trabajo():
            try:
                res = clasificar(
                    self.imagen_path, perfil,
                    log=lambda m: self._cola.put(("log", m)),
                )
                self._cola.put(("ok", res))
            except ErrorModelo as e:
                self._cola.put(("error", str(e)))
            except Exception as e:  # noqa: BLE001  (queremos mostrar cualquier fallo)
                self._cola.put(("error", f"Error inesperado: {e}"))

        threading.Thread(target=trabajo, daemon=True).start()
        self.after(100, self._revisar_cola)

    def _revisar_cola(self):
        """Lee mensajes del hilo de trabajo y actualiza la UI (en el hilo de Tk)."""
        try:
            while True:
                tipo, dato = self._cola.get_nowait()
                if tipo == "log":
                    self.estado.set(dato)
                elif tipo == "ok":
                    self._mostrar_resultados(dato)
                    self.estado.set("Listo.")
                    self.btn_clasificar.configure(state="normal")
                    return
                elif tipo == "error":
                    self._mostrar_error(dato)
                    self.estado.set("Error al clasificar.")
                    self.btn_clasificar.configure(state="normal")
                    return
        except queue.Empty:
            pass
        self.after(100, self._revisar_cola)

    # ---------------- render de resultados ----------------
    def _limpiar_resultados(self):
        for w in self.resultados.winfo_children():
            w.destroy()

    def _mostrar_resultados(self, resultados, top=10):
        self._limpiar_resultados()
        for etiqueta, prob in resultados[:top]:
            fila = ttk.Frame(self.resultados)
            fila.pack(fill="x", pady=2)
            ttk.Label(fila, text=etiqueta, width=22, anchor="w").pack(side="left")
            barra = ttk.Progressbar(fila, maximum=1.0, value=float(prob), length=240)
            barra.pack(side="left", padx=6)
            ttk.Label(fila, text=f"{prob*100:5.1f}%", width=7, anchor="e").pack(side="left")

    def _mostrar_error(self, msg):
        self._limpiar_resultados()
        tk.Label(
            self.resultados, text=msg, fg="#b00020",
            justify="left", wraplength=420, anchor="w",
        ).pack(anchor="w", fill="x")


if __name__ == "__main__":
    App().mainloop()
