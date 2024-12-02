import sqlite3
from datetime import datetime
from src.logica.security import encriptar_contraseña, desencriptar_contraseña
import pandas as pd
from tkinter import messagebox, filedialog
from contextlib import contextmanager
import pytz


def convertir_a_hora_local(hora_utc):
    """Convierte la hora UTC a la hora local en la zona horaria de Lima."""
    utc_time = datetime.strptime(hora_utc, "%Y-%m-%d %H:%M:%S")
    utc_time = pytz.utc.localize(utc_time)  # Localiza como UTC
    local_time = utc_time.astimezone(pytz.timezone('America/Lima'))  # Ajusta a la zona horaria de Lima
    return local_time.strftime("%Y-%m-%d %H:%M:%S")


# Context manager para manejar la conexión a la base de datos
@contextmanager
def conectar_db():
    conn = sqlite3.connect("base_datos.db")
    try:
        yield conn  # Devuelve la conexión para usarla dentro del contexto
    finally:
        conn.close()  # Asegura que se cierre la conexión al finalizar


# Crear las tablas solo una vez cuando se inicia el programa
def inicializar_db():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS contraseñas (
                            cuenta TEXT PRIMARY KEY, 
                            contraseña TEXT, 
                            categoria TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS historial (
                            cuenta TEXT, 
                            accion TEXT, 
                            fecha_hora TEXT)''')
        conn.commit()


# Registrar una acción en el historial
def registrar_historial(accion, cuenta):
    fecha_hora_actual = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S")  # Obtener la fecha y hora actual en formato "YYYY-MM-DD HH:MM:SS"
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute(""" 
            INSERT INTO historial (accion, cuenta, fecha_hora) 
            VALUES (?, ?, ?)
        """, (accion, cuenta, fecha_hora_actual))
        conn.commit()


# Función para agregar una nueva contraseña
def agregar_contraseña(cuenta, contraseña, categoria):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contraseñas (cuenta, contraseña, categoria) VALUES (?, ?, ?)",
                       (cuenta, encriptar_contraseña(contraseña), categoria))
        conn.commit()
    # Registrar la acción en el historial
    registrar_historial("agregado", cuenta)


# Obtener todas las contraseñas
def obtener_contraseñas():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cuenta, contraseña, categoria FROM contraseñas")
        datos = cursor.fetchall()
    return datos


# Buscar una contraseña por cuenta
def buscar_contraseña(cuenta):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT contraseña FROM contraseñas WHERE cuenta=?", (cuenta,))
        resultado = cursor.fetchone()
    return desencriptar_contraseña(resultado[0]) if resultado else None


# Editar una contraseña existente
def editar_contraseña(cuenta, nueva_contraseña):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE contraseñas SET contraseña = ? WHERE cuenta = ?",
                       (encriptar_contraseña(nueva_contraseña), cuenta))
        conn.commit()
    # Registrar la acción en el historial
    registrar_historial("editado", cuenta)


# Borrar una contraseña
def borrar_contraseña(cuenta):
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contraseñas WHERE cuenta = ?", (cuenta,))
        conn.commit()
    # Registrar la acción en el historial
    registrar_historial("borrado", cuenta)


# Obtener el historial de acciones
def obtener_historial():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cuenta, accion, fecha_hora FROM historial ORDER BY fecha_hora DESC")
        historial = cursor.fetchall()
    return historial


# Exportar contraseñas a un archivo Excel
def exportar_a_excel(archivo=None):
    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cuenta, contraseña, categoria FROM contraseñas")
            datos = cursor.fetchall()

        # Desencriptar las contraseñas antes de exportarlas
        from src.logica.security import desencriptar_contraseña  # Asegúrate de tener importada esta función
        datos_desencriptados = []
        for cuenta, contraseña_encriptada, categoria in datos:
            try:
                contraseña_desencriptada = desencriptar_contraseña(contraseña_encriptada)
            except Exception as e:
                contraseña_desencriptada = f"Error: {e}"  # Para manejar casos donde la desencriptación falle
            datos_desencriptados.append((cuenta, contraseña_desencriptada, categoria))

        # Si no se proporciona un archivo, usar filedialog
        if not archivo:
            archivo = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                   filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])

        if archivo:
            columnas = ["cuenta", "contraseña", "categoria"]
            # Crear el DataFrame con los datos desencriptados
            df = pd.DataFrame(datos_desencriptados, columns=columnas)
            df.to_excel(archivo, index=False)

            # Registrar en el historial para cada cuenta exportada
            for cuenta, _, _ in datos:
                registrar_historial("exportado", cuenta)

            messagebox.showinfo("Éxito", f"Contraseñas exportadas a {archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar: {e}")


# Importar contraseñas desde un archivo Excel
def importar_desde_excel(archivo=None, actualizar_lista=None):
    try:
        if not archivo:
            archivo = filedialog.askopenfilename(
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")])

        if not archivo:
            return

        # Leer los datos del archivo Excel
        df = pd.read_excel(archivo)

        # Validar que las columnas requeridas existan
        columnas_requeridas = {"cuenta", "contraseña", "categoria"}
        if not columnas_requeridas.issubset(df.columns):
            messagebox.showerror("Error",
                                 "El archivo Excel no tiene las columnas requeridas: cuenta, contraseña, categoria.")
            return

        with conectar_db() as conn:
            cursor = conn.cursor()
            for _, fila in df.iterrows():
                cuenta = fila["cuenta"]
                contraseña = fila["contraseña"]
                categoria = fila["categoria"]

                # Insertar o actualizar la contraseña
                cursor.execute(""" 
                    INSERT INTO contraseñas (cuenta, contraseña, categoria) 
                    VALUES (?, ?, ?)
                    ON CONFLICT(cuenta) 
                    DO UPDATE SET contraseña = excluded.contraseña, categoria = excluded.categoria
                """, (cuenta, contraseña, categoria))

                # Registrar la acción en el historial como "importado"
                cursor.execute(""" 
                    INSERT INTO historial (accion, cuenta, fecha_hora) 
                    VALUES ('importado', ?, datetime('now'))
                """, (cuenta,))

            conn.commit()

        # Si se proporciona una función para actualizar la lista, se ejecuta
        if actualizar_lista:
            actualizar_lista()

        messagebox.showinfo("Éxito", "Contraseñas importadas correctamente desde el archivo Excel.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al importar datos: {e}")


# Llamada inicial para crear las tablas
inicializar_db()
