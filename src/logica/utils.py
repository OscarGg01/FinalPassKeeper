import tkinter as tk
import pyperclip


def copiar_al_portapapeles(texto):
    """Copia el texto al portapapeles y borra el contenido después de 60 segundos."""
    pyperclip.copy(texto)

    root = tk.Tk()
    root.withdraw()  # Oculta la ventana de Tkinter
    root.clipboard_clear()  # Limpia el portapapeles
    root.clipboard_append(texto)  # Copia el texto al portapapeles
    root.update()  # Actualiza el portapapeles

    # Define una función para borrar el portapapeles
    def borrar_portapapeles():
        root.clipboard_clear()
        root.update()

    # Programa el borrado del portapapeles después de 60 segundos (60000 milisegundos)
    root.after(60000, borrar_portapapeles)

    # Cierra la ventana oculta después de 60 segundos para evitar que el proceso quede abierto
    root.after(60000, root.destroy)
