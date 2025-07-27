# import time
# import traceback
# import stomp
# import timer
# from PyQt6.QtCore import QEventLoop, QTimer, Qt
# from nltk.downloader import update
#
# from client_connection import Connecting
#
# from PyQt6.QtWidgets import (
#     QApplication, QWidget, QVBoxLayout, QLineEdit, QStackedWidget, QTabWidget, QPushButton, QListWidget, QLabel,
#     QMessageBox, QTextEdit, QHBoxLayout,
# )
#
# import sys
#
#
# class Client(QWidget):
#     def __init__(self, stacked_widget):
#         super().__init__()
#         self.history = {}
#         self.contato_atual = None
#         self.user_name = ""
#         self.stacked_widget = stacked_widget
#
#         # Layouts
#         layout = QHBoxLayout(self)
#         self.setLayout(layout)
#
#         # Lista de contatos
#         self.lista_contatos = QListWidget()
#         layout.addWidget(self.lista_contatos, 2)
#
#         # Campo para novo contato
#         self.input_novo_contato = QLineEdit()
#         self.input_novo_contato.setPlaceholderText(f"Novo")
#
#         self.btn_adicionar = QPushButton("Adicionar")
#
#         layout_novo = QHBoxLayout()
#         layout_novo.addWidget(self.input_novo_contato)
#         layout_novo.addWidget(self.btn_adicionar)
#
#         # Área de chat
#         self.chat_area = QTextEdit()
#         self.chat_area.setReadOnly(True)
#         self.nome_contato = QLabel("Selecionar contato")
#
#         self.input_msg = QLineEdit()
#         self.btn_enviar = QPushButton("Enviar")
#
#         layout_chat = QVBoxLayout()
#         layout_chat.addWidget(self.nome_contato)
#         layout_chat.addWidget(self.chat_area)
#         input_layout = QHBoxLayout()
#         input_layout.addWidget(self.input_msg)
#         input_layout.addWidget(self.btn_enviar)
#         layout_chat.addLayout(input_layout)
#
#         right = QVBoxLayout()
#         right.addLayout(layout_novo)
#         right.addLayout(layout_chat)
#
#         layout.addLayout(right, 5)
#
#     def nada(self):
#         pass
#
#
#
#     def switch_to_self(self):
#         self.stacked_widget.setWindowTitle(self.user_name)
#         self.stacked_widget.setMinimumSize(0, 0)
#         self.stacked_widget.setMaximumSize(16777215, 16777215)
#         self.stacked_widget.setGeometry(100, 100, 600, 400)
#         self.stacked_widget.show()
#
#
# def switch_to(index):
#     widget = stacked_widget.widget(index)
#     widget.switch_to_self()
#
#
# app = QApplication(sys.argv)
#
# # Widget que troca entre as telas
# stacked_widget = QStackedWidget()
# stacked_widget.currentChanged.connect(switch_to)
#
# # Cria as duas telas
# tela2 = Client(stacked_widget)
# tela1 = Connecting(stacked_widget)
#
# # Adiciona ao gerenciador de telas
# stacked_widget.addWidget(tela1)  # Índice 0
# stacked_widget.addWidget(tela2)  # Índice 0
#
# sys.exit(app.exec())
#
import threading
import time

from Pyro5.client import Proxy
from Pyro5.core import locate_ns
from Pyro5.server import Daemon, expose

from interfaces import *


class Client:
    def __init__(self, user_name):
        self.server_id = user_name

        thread_servidor = threading.Thread(target=self.register, daemon=True)
        thread_servidor.start()


    @expose
    def receive_message(self, message):
        print(f"message: {message}")


    def register(self):
        daemon = Daemon()

        while True:
            try:
                ns = locate_ns(port=9090)

                uri = daemon.register(self)
                ns.register(self.server_id, uri)
                break
            except Exception as e:
                print(e)

            time.sleep(1)

        print(f"Servidor registrado como {self.server_id}")
        daemon.requestLoop()


while True:
    try:
        ns = locate_ns(port=9090)
        uri_remoto = ns.lookup("|@servidor@|")
        server: ServerInterface = Proxy(uri_remoto)
        break
    except Exception as e:
        print(f"name server connect:  {e}")
        time.sleep(1)


client = Client("lucas")

print(server.add_user(user_name="lucas", distance=130000,latitude=19.0760, longitude=72.8777))
print(server.add_user(user_name="pedro", distance=130000,latitude=18.5204, longitude=73.8567))
print(server.get_list_by_coordinate("lucas"))

server.send_message()