import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from src.database.database import agregar_contraseña, obtener_contraseñas, editar_contraseña, borrar_contraseña
from src.logica.utils import copiar_al_portapapeles
from src.interface.gui import generar_contraseña_aleatoria
import pyperclip


class TestPasswordManager(unittest.TestCase):

    def setUp(self):
        # Configuración inicial antes de cada prueba
        self.cuenta = "test_cuenta"
        self.contraseña = "test_contraseña_segura_123!"
        self.categoria = "test_categoria"

    def tearDown(self):
        # Limpieza después de cada prueba
        try:
            borrar_contraseña(self.cuenta)
        except Exception:
            pass

    # ---- Pruebas de Base de Datos ----
    def test_agregar_contraseña(self):
        agregar_contraseña(self.cuenta, self.contraseña, self.categoria)
        contraseñas = obtener_contraseñas()
        cuentas = [c[0] for c in contraseñas]
        self.assertIn(self.cuenta, cuentas, "La cuenta no fue agregada correctamente.")

    def test_editar_contraseña(self):
        from src.logica.security import desencriptar_contraseña  # Importar la función de desencriptar
        agregar_contraseña(self.cuenta, self.contraseña, self.categoria)
        nueva_contraseña = "nueva_contraseña_segura_456!"
        editar_contraseña(self.cuenta, nueva_contraseña)
        contraseñas = obtener_contraseñas()
        for c in contraseñas:
            if c[0] == self.cuenta:
                contraseña_desencriptada = desencriptar_contraseña(c[1])  # Desencriptar la contraseña recuperada
                self.assertEqual(
                    contraseña_desencriptada, nueva_contraseña,
                    "La contraseña no fue editada correctamente."
                )

    def test_borrar_contraseña(self):
        agregar_contraseña(self.cuenta, self.contraseña, self.categoria)
        borrar_contraseña(self.cuenta)
        contraseñas = obtener_contraseñas()
        cuentas = [c[0] for c in contraseñas]
        self.assertNotIn(self.cuenta, cuentas, "La cuenta no fue eliminada correctamente.")

    # ---- Pruebas de Utilidades ----
    def test_generar_contraseña_aleatoria(self):
        contraseña = generar_contraseña_aleatoria()
        self.assertEqual(len(contraseña), 15, "La longitud de la contraseña generada no es correcta.")
        self.assertTrue(any(c.isupper() for c in contraseña), "La contraseña debe tener al menos una letra mayúscula.")
        self.assertTrue(any(c.islower() for c in contraseña), "La contraseña debe tener al menos una letra minúscula.")
        self.assertTrue(any(c in "!@#$%^&*()_+[]{}|;:',.<>?/`~" for c in contraseña),
                        "La contraseña debe tener al menos un carácter especial.")

    def test_copiar_al_portapapeles(self):
        copiar_al_portapapeles(self.contraseña)
        self.assertEqual(pyperclip.paste(), self.contraseña, "La contraseña no fue copiada correctamente al portapapeles.")

    # ---- Pruebas de Interfaz Gráfica ----
    @patch("tkinter.Tk")
    def test_centrar_ventana(self, MockTk):
        from src.interface.gui import centrar_ventana
        ventana = MockTk()
        ventana.winfo_screenwidth.return_value = 1920
        ventana.winfo_screenheight.return_value = 1080
        ventana.geometry = MagicMock()
        centrar_ventana(ventana, 800, 600)
        ventana.geometry.assert_called_with("800x600+560+240")

    @patch("tkinter.Tk")
    def test_ventana_principal(self, MockTk):
        from src.interface.gui import ventana_principal
        root = MockTk()
        root.mainloop = MagicMock()
        ventana_principal()
        root.mainloop.assert_called_once()


if __name__ == "__main__":
    unittest.main()