import os
import tkinter as tk
from tkinter import messagebox
from src.interface.gui import ventana_principal
from src.logica.security import verificar_contraseña_maestra, establecer_contraseña_maestra
from src.database.database import conectar_db


def iniciar_sesion():
    """Verifica la contraseña maestra y, si es correcta, abre la ventana principal."""
    contraseña = entry_maestra.get()
    if verificar_contraseña_maestra(contraseña):
        root.destroy()
        ventana_principal()
    else:
        messagebox.showerror("Error", "Contraseña maestra incorrecta.")


def establecer_contraseña():
    """Establece la contraseña maestra si ambas contraseñas coinciden."""
    nueva_contraseña = entry_nueva_maestra.get()
    confirmar_contraseña = entry_confirmar_maestra.get()
    if nueva_contraseña == confirmar_contraseña and nueva_contraseña:
        establecer_contraseña_maestra(nueva_contraseña)
        messagebox.showinfo("Éxito", "Contraseña maestra establecida.")
        root.destroy()
        ventana_principal()
    else:
        messagebox.showerror("Error", "Las contraseñas no coinciden o están vacías.")


# Configuración de la ventana principal
conectar_db()
root = tk.Tk()
root.title("Inicio de Sesión")
root.geometry("400x300")  # Ajustar tamaño de la ventana
root.resizable(False, False)  # Bloquear redimensionamiento manual

# Centrar la ventana en la pantalla
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 400) // 2
y = (screen_height - 300) // 2
root.geometry(f"400x300+{x}+{y}")

# Interfaz según si existe o no una contraseña maestra
if os.path.exists("master_password.txt"):
    tk.Label(root, text="Introduce la Contraseña Maestra:", font=("Arial", 14)).pack(pady=20)
    entry_maestra = tk.Entry(root, show="*", width=30)
    entry_maestra.pack(pady=10)
    tk.Button(root, text="Ingresar", command=iniciar_sesion).pack(pady=20)
else:
    tk.Label(root, text="Establece una Nueva Contraseña Maestra:", font=("Arial", 14)).pack(pady=20)
    tk.Label(root, text="Contraseña:").pack()
    entry_nueva_maestra = tk.Entry(root, show="*", width=30)
    entry_nueva_maestra.pack(pady=10)
    tk.Label(root, text="Confirmar Contraseña:").pack()
    entry_confirmar_maestra = tk.Entry(root, show="*", width=30)
    entry_confirmar_maestra.pack(pady=10)
    tk.Button(root, text="Establecer Contraseña", command=establecer_contraseña).pack(pady=20)

root.mainloop()
