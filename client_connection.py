import time
import traceback
from typing import List

import stomp
import requests

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QHBoxLayout, QLineEdit
)

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QObject, QEventLoop, QTimer
from requests.auth import HTTPBasicAuth
from waitingspinnerwidget import QtWaitingSpinner


class BrokerListener(QObject, stomp.ConnectionListener):
    message_received  = pyqtSignal(str, str, str, str)
    message_error     = pyqtSignal(str)


    def __init__(self, user):
        super().__init__()
        self.user = user


    def on_message(self, frame):
        message_type = frame.headers["destination"].split("/")[1]
        message_destination = frame.headers["destination"].split("/")[2]
        user = frame.body[:frame.body.find(":")]
        message = frame.body[frame.body.find(":")+1:]

        self.message_received.emit(user, message_type, message_destination, message)


    def on_error(self, frame):
        self.message_error.emit(frame.body)



class BrokerConnectThread(QThread):
    conectado = pyqtSignal(object, object)
    erro = pyqtSignal(str)


    def __init__(self, user, host='localhost', port=61613):
        super().__init__()
        self.user = user
        self.host = host
        self.port = port
        self.error = ""


    def set_error(self, error):
        self.error = error


    def run(self):
        try:
            conn = stomp.Connection12([(self.host, self.port)])
            listener = BrokerListener(self.user)
            listener.message_error.connect(self.set_error)
            conn.set_listener('', listener)
            conn.connect("user", "user", wait=True)
            conn.send(destination=f"/queue/user_{self.user}", body=f"")

            loop = QEventLoop()
            QTimer.singleShot(100, loop.quit)  # aguarda 50ms
            loop.exec()

            if self.error != "":
                self.error = ""
                raise ValueError("usuario não existe")
            self.conectado.emit(conn, listener)
        except Exception as e:
            self.erro.emit("falha na conexão")


class Connecting(QWidget):
    conn_signal = pyqtSignal(object, object)
    user_signal = pyqtSignal(object)

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.conn = None
        self.listener = None

        self.label_status = QLabel("Digite seu nome:")
        self.spinner = QtWaitingSpinner(self, centerOnParent=False)
        self.thread = None

        # Campo para o nome do usuário
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Seu nome de usuário")

        # Botão conectar
        self.btn_connect = QPushButton("Conectar")
        self.btn_connect.clicked.connect(self.conectar)

        # Layout do status com spinner
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.spinner)
        status_layout.addWidget(self.label_status)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout principal
        layout = QVBoxLayout()
        layout.addLayout(status_layout)
        layout.addWidget(self.input_user)
        layout.addWidget(self.btn_connect)

        self.setLayout(layout)


    def switch_to_self(self):
        self.stacked_widget.setFixedSize(300, 200)
        self.stacked_widget.setWindowTitle("Conectando")
        self.stacked_widget.show()


    def conectar(self):
        self.spinner.start()
        self.label_status.setText("Conectando...")

        self.thread = BrokerConnectThread(self.input_user.text())
        self.thread.conectado.connect(self.on_conectado)
        self.thread.erro.connect(self.on_erro)
        self.thread.start()


    def on_conectado(self, conn, listener):
        self.listener = listener
        self.conn = conn
        self.spinner.stop()
        self.label_status.setText(f"Conectado como {self.input_user.text()}")
        QMessageBox.information(self, "Conectado", "Conectado com sucesso ao broker.")
        self.user_signal.emit(self.input_user.text())
        self.conn_signal.emit(conn, self.listener)

        self.stacked_widget.setCurrentIndex(1)


    def on_erro(self, erro):
        self.spinner.stop()
        self.label_status.setText(f"Seu nome de usuário")
        QMessageBox.critical(self, "Erro", f"Erro: {erro}")






