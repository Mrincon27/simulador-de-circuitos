import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os


class Componente:
    '''Clase base que representa un componente de un circuito'''

    def __init__(self, valor: float, unidad: str):
        if valor <= 0:
            raise ValueError(f"El valor del componente {self.__class__.__name__} debe ser mayor que cero")
        self._valor = float(valor)
        self._unidad = str(unidad)

    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, nuevo_valor):
        if nuevo_valor <= 0:
            raise ValueError("El valor del componente debe ser mayor que cero")
        self._valor = float(nuevo_valor)

    @property
    def unidad(self):
        return self._unidad

    @unidad.setter
    def unidad(self, nueva_unidad):
        if not isinstance(nueva_unidad, str):
            raise TypeError("La unidad debe ser un string")
        self._unidad = nueva_unidad


class FuenteDC(Componente):
    '''Clase que representa una fuente de corriente continua (voltaje)'''

    def __init__(self, valor, unidad="V"):
        if unidad != "V":
            raise ValueError("Las fuentes de voltaje deben estar en voltios (V)")
        super().__init__(valor, unidad)


class Resistencia(Componente):
    '''Clase que representa una resistencia'''

    def __init__(self, valor, unidad="ohm"):
        if unidad != "ohm":
            raise ValueError("Las resistencias deben estar en ohmios (ohm)")
        super().__init__(valor, unidad)


class Capacitor(Componente):
    '''Clase que representa un capacitor'''

    def __init__(self, valor, unidad="F"):
        if unidad != "F":
            raise ValueError("Los capacitores deben estar en faradios (F)")
        super().__init__(valor, unidad)


class Inductor(Componente):
    '''Clase que representa un inductor'''

    def __init__(self, valor, unidad="H"):
        if unidad != "H":
            raise ValueError("Los inductores deben estar en henrios (H)")
        super().__init__(valor, unidad)


class Circuito:
    '''Clase base que representa un circuito eléctrico'''

    def __init__(self, fuente, componentes, tiempo=np.linspace(0.001, 0.1, 1000)):
        self.fuente = fuente
        self.componentes = componentes
        self.tiempo = tiempo


class CircuitoRC(Circuito):
    '''Circuito que contiene una resistencia y un capacitor'''

    def __init__(self, fuente, resistencia, capacitancia):
        super().__init__(fuente, [resistencia, capacitancia])
        self.resistencia = resistencia
        self.capacitancia = capacitancia

    def voltaje_R(self):
        return self.fuente.valor * np.exp(-self.tiempo / (self.resistencia.valor * self.capacitancia.valor))

    def voltaje_C(self):
        return self.fuente.valor * (1 - np.exp(-self.tiempo / (self.resistencia.valor * self.capacitancia.valor)))

    def corriente_Circuito(self):
        return self.voltaje_R() / self.resistencia.valor


class CircuitoRL(Circuito):
    '''Circuito que contiene una resistencia y un inductor'''

    def __init__(self, fuente, resistencia, inductancia):
        super().__init__(fuente, [resistencia, inductancia])
        self.resistencia = resistencia
        self.inductancia = inductancia

    def corriente_Circuito(self):
        return self.fuente.valor * (1 - np.exp(-self.tiempo / (self.inductancia.valor / self.resistencia.valor))) / self.resistencia.valor

    def voltaje_R(self):
        return self.resistencia.valor * self.corriente_Circuito()

    def voltaje_L(self):
        return self.fuente.valor * np.exp(-self.tiempo / (self.inductancia.valor / self.resistencia.valor))


class CircuitoRLC(Circuito):
    '''Circuito que contiene una resistencia, un inductor y un capacitor'''

    def __init__(self, fuente, resistencia, inductancia, capacitancia):
        super().__init__(fuente, [resistencia, inductancia, capacitancia])
        self.resistencia = resistencia
        self.inductancia = inductancia
        self.capacitancia = capacitancia

    def corriente_Circuito(self):
        return (self.fuente.valor / self.resistencia.valor * (1 - np.exp(-self.tiempo / (self.inductancia.valor / self.resistencia.valor))))

    def voltaje_R(self):
        return self.resistencia.valor * self.corriente_Circuito()

    def voltaje_L(self):
        return self.inductancia.valor * np.gradient(self.corriente_Circuito(), self.tiempo)

    def voltaje_C(self):
        return self.fuente.valor * (1 - np.exp(-self.tiempo / (self.resistencia.valor * self.capacitancia.valor)))


class CircuitoRC_Paralelo(Circuito):
    '''Circuito RC en paralelo'''

    def __init__(self, fuente, resistencia, capacitancia):
        super().__init__(fuente, [resistencia, capacitancia])
        self.resistencia = resistencia
        self.capacitancia = capacitancia

    def voltaje_Circuito(self):
        return np.full_like(self.tiempo, self.fuente.valor)

    def corriente_R(self):
        return np.full_like(self.tiempo, self.fuente.valor / self.resistencia.valor)

    def corriente_C(self):
        return self.capacitancia.valor * np.gradient(self.voltaje_Circuito(), self.tiempo, edge_order=2)

    def corriente_Total(self):
        return self.corriente_R() + self.corriente_C()


class CircuitoRL_Paralelo(Circuito):
    '''Circuito RL en paralelo'''

    def __init__(self, fuente, resistencia, inductancia):
        super().__init__(fuente, [resistencia, inductancia])
        self.resistencia = resistencia
        self.inductancia = inductancia

    def voltaje_Circuito(self):
        return np.full_like(self.tiempo, self.fuente.valor)

    def corriente_R(self):
        return np.full_like(self.tiempo, self.fuente.valor / self.resistencia.valor)

    def corriente_L(self):
        return np.cumsum(self.voltaje_Circuito()) * (self.tiempo[1] - self.tiempo[0]) / self.inductancia.valor

    def corriente_Total(self):
        return self.corriente_R() + self.corriente_L()


class CircuitoRLC_Paralelo(Circuito):
    '''Circuito RLC en paralelo'''

    def __init__(self, fuente, resistencia, inductancia, capacitancia):
        super().__init__(fuente, [resistencia, inductancia, capacitancia])
        self.resistencia = resistencia
        self.inductancia = inductancia
        self.capacitancia = capacitancia

    def voltaje_Circuito(self):
        return np.full_like(self.tiempo, self.fuente.valor)

    def corriente_R(self):
        return np.full_like(self.tiempo, self.fuente.valor / self.resistencia.valor)

    def corriente_L(self):
        return np.cumsum(self.voltaje_Circuito()) * (self.tiempo[1] - self.tiempo[0]) / self.inductancia.valor

    def corriente_C(self):
        return self.capacitancia.valor * np.gradient(self.voltaje_Circuito(), self.tiempo, edge_order=2)

    def corriente_Total(self):
        return self.corriente_R() + self.corriente_L() + self.corriente_C()


class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Circuitos")
        self.root.geometry("400x400")

        tk.Label(root, text="Seleccione el tipo de circuito:", font=("Arial", 12)).pack(pady=10)

        self.boton1 = tk.Button(self.root, text="Circuito RC", font=("Arial", 12),
                                command=lambda: self.abrir_simulador("RC", "circuito_RC.jpg"),
                                bg="lightblue", fg="black")
        self.boton1.pack(pady=10, fill=tk.BOTH, expand=True)

        self.boton2 = tk.Button(self.root, text="Circuito RL", font=("Arial", 12),
                                command=lambda: self.abrir_simulador("RL", "circuito_RL.jpg"),
                                bg="teal", fg="black")
        self.boton2.pack(pady=10, fill=tk.BOTH, expand=True)

        self.boton3 = tk.Button(self.root, text="Circuito RLC", font=("Arial", 12),
                                command=lambda: self.abrir_simulador("RLC", "circuito_RLC.jpg"),
                                bg="pink", fg="black")
        self.boton3.pack(pady=10, fill=tk.BOTH, expand=True)

        # Botón para borrar y finalizar el programa
        self.boton_borrar = tk.Button(self.root, text="Cerrar programa", font=("Arial", 12),
                                      command=self.finalizar_programa, bg="red", fg="white")
        self.boton_borrar.pack(pady=10, fill=tk.BOTH, expand=True)

    def abrir_simulador(self, tipo, image_file):
        self.root.destroy()
        root_circuito = tk.Tk()
        image_path = os.path.join("clases_interfaz", "assets", image_file)
        VentanaCircuito(root_circuito, tipo, image_path)
        root_circuito.mainloop()

    def finalizar_programa(self):
        """Función para finalizar el programa"""
        self.root.destroy()


class VentanaCircuito:
    def __init__(self, root, tipo, image_path):
        self.root = root
        self.root.title(f"Simulación {tipo}")
        self.root.geometry("800x600")  # Tamaño más pequeño
        self.root.resizable(True, True)
        self.image_path = image_path
        self.tipo_circuito = tipo
        self.parametros = {}
        self.configuracion = "serie"

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0, minsize=50)
        self.root.rowconfigure(1, weight=1, minsize=150)
        self.root.rowconfigure(2, weight=1, minsize=50)

        frame_botones = tk.Frame(self.root)
        frame_botones.grid(row=0, column=0, sticky="nsew")

        frame_botones.columnconfigure([0, 1, 2, 3, 4, 5], weight=1)
        frame_botones.rowconfigure(0, weight=1)

        tk.Button(frame_botones, text="Serie", command=self.serie).grid(row=0, column=0, sticky="nsew")
        tk.Button(frame_botones, text="Paralelo", command=self.paralelo).grid(row=0, column=1, sticky="nsew")
        tk.Button(frame_botones, text="Simular", command=self.simular).grid(row=0, column=2, sticky="nsew")
        tk.Button(frame_botones, text="Guardar", command=self.guardar_circuito).grid(row=0, column=3, sticky="nsew")
        tk.Button(frame_botones, text="Cargar", command=self.cargar_circuito).grid(row=0, column=4, sticky="nsew")
        tk.Button(frame_botones, text="Menú", command=self.volverMenu).grid(row=0, column=5, sticky="nsew")

        self.frame_imagen_circuito = tk.Frame(self.root, bd=2, relief="solid", bg="lightgreen")
        self.frame_imagen_circuito.grid(row=1, column=0, sticky="nsew")

        self.frame_parametros = tk.Frame(self.root, bd=2, relief="solid", bg="lightblue")
        self.frame_parametros.grid(row=2, column=0, sticky="nsew")

        self.crear_campos_parametros()
        self.cargar_imagen()

    def crear_campos_parametros(self):
        campos = {"resistencia": "Resistencia (Ω)", "voltaje": "Voltaje (V)"}
        if self.tipo_circuito in ["RC", "RLC"]:
            campos["capacitor"] = "Capacitor (F)"
        if self.tipo_circuito in ["RL", "RLC"]:
            campos["inductor"] = "Inductor (H)"

        for i, (clave, etiqueta) in enumerate(campos.items(), start=0):
            # Centrar y agrandar el texto
            ttk.Label(self.frame_parametros, text=etiqueta, background="lightblue", font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=10, sticky="ew")
            self.parametros[clave] = ttk.Entry(self.frame_parametros, width=15, font=("Arial", 12))
            self.parametros[clave].grid(row=i, column=1, padx=10, pady=10, sticky="ew")

        # Centrar los campos en el frame
        self.frame_parametros.columnconfigure(0, weight=1)
        self.frame_parametros.columnconfigure(1, weight=1)

    def cargar_imagen(self):
        try:
            imagen = Image.open(self.image_path)
            width, height = 400, 200  # Tamaño fijo para la imagen
            imagen = imagen.resize((width, height))
            self.imagen_tk = ImageTk.PhotoImage(imagen)
            label_imagen = tk.Label(self.frame_imagen_circuito, image=self.imagen_tk)
            label_imagen.place(relwidth=1, relheight=1)
        except FileNotFoundError:
            error_label = tk.Label(self.frame_imagen_circuito, text="Imagen no encontrada", fg="red", font=("Arial", 14))
            error_label.pack(expand=True)
        except Exception as e:
            error_label = tk.Label(self.frame_imagen_circuito, text=f"Error: {e}", fg="red", font=("Arial", 14))
            error_label.pack(expand=True)

    def obtener_valores(self):
        valores = {}
        for clave, entry in self.parametros.items():
            try:
                valores[clave] = float(entry.get())
            except ValueError:
                messagebox.showerror("Error", f"Valor inválido para {clave}")
                return None
        return valores

    def simular(self):
        valores = self.obtener_valores()
        if valores is None:
            return

        tiempo = np.linspace(0, 0.1, 1000)
        if self.tipo_circuito == "RC":
            if self.configuracion == "serie":
                circuito = CircuitoRC(FuenteDC(valores["voltaje"]), Resistencia(valores["resistencia"]), Capacitor(valores["capacitor"]))
            else:
                circuito = CircuitoRC_Paralelo(FuenteDC(valores["voltaje"]), Resistencia(valores["resistencia"]), Capacitor(valores["capacitor"]))
        elif self.tipo_circuito == "RL":
            if self.configuracion == "serie":
                circuito = CircuitoRL(FuenteDC(valores["voltaje"]), Resistencia(valores["resistencia"]), Inductor(valores["inductor"]))
            else:
                circuito = CircuitoRL_Paralelo(FuenteDC(valores["voltaje"]), Resistencia(valores["resistencia"]), Inductor(valores["inductor"]))
        elif self.tipo_circuito == "RLC":
            if self.configuracion == "serie":
                circuito = CircuitoRLC(FuenteDC(valores["voltaje"]), Resistencia(valores["resistencia"]), Inductor(valores["inductor"]), Capacitor(valores["capacitor"]))
            else:
                circuito = CircuitoRLC_Paralelo(FuenteDC(valores["voltaje"]), Resistencia(valores["resistencia"]), Inductor(valores["inductor"]), Capacitor(valores["capacitor"]))

        self.mostrar_graficas(circuito, tiempo)

    def mostrar_graficas(self, circuito, tiempo):
        # Crear una nueva ventana para las gráficas
        ventana_graficas = tk.Toplevel(self.root)
        ventana_graficas.title("Gráficas del Circuito")
        ventana_graficas.geometry("800x600")  # Tamaño más pequeño

        # Crear las gráficas
        fig, axs = plt.subplots(2, 1, figsize=(8, 6))
        
        # Gráfica de voltajes
        if self.configuracion == "serie":
            axs[0].plot(tiempo, circuito.voltaje_R(), label="Voltaje en R")
            if hasattr(circuito, 'voltaje_C'):
                axs[0].plot(tiempo, circuito.voltaje_C(), label="Voltaje en C")
            if hasattr(circuito, 'voltaje_L'):
                axs[0].plot(tiempo, circuito.voltaje_L(), label="Voltaje en L")
        else:
            # En paralelo, el voltaje es el mismo en todos los componentes
            axs[0].plot(tiempo, np.full_like(tiempo, circuito.fuente.valor), label="Voltaje en R, L, C")
        
        axs[0].set_title("Voltajes")
        axs[0].legend()
        axs[0].grid()

        # Gráfica de corriente
        if hasattr(circuito, 'corriente_Circuito'):
            axs[1].plot(tiempo, circuito.corriente_Circuito(), label="Corriente")
        elif hasattr(circuito, 'corriente_Total'):
            axs[1].plot(tiempo, circuito.corriente_Total(), label="Corriente Total")
        
        axs[1].set_title("Corriente")
        axs[1].legend()
        axs[1].grid()

        # Integrar la figura en la ventana de gráficas
        canvas = FigureCanvasTkAgg(fig, master=ventana_graficas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def serie(self):
        self.configuracion = "serie"
        print("Configuración en Serie")

    def paralelo(self):
        self.configuracion = "paralelo"
        print("Configuración en Paralelo")

    def guardar_circuito(self):
        valores = self.obtener_valores()
        if valores is None:
            return

        nombre_archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if nombre_archivo:
            with open(nombre_archivo, "w") as archivo:
                json.dump(valores, archivo)
            messagebox.showinfo("Guardado", "Circuito guardado correctamente.")

    def cargar_circuito(self):
        nombre_archivo = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if nombre_archivo:
            with open(nombre_archivo, "r") as archivo:
                valores = json.load(archivo)
            for clave, entry in self.parametros.items():
                if clave in valores:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(valores[clave]))
            messagebox.showinfo("Cargado", "Circuito cargado correctamente.")

    def volverMenu(self):
        self.root.destroy()
        root_menu = tk.Tk()
        VentanaPrincipal(root_menu)
        root_menu.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    VentanaPrincipal(root)
    root.mainloop()