from __future__     import annotations

from typing           import (List, Optional)

from Pyro5.client import Proxy
from Pyro5.core import locate_ns
from Pyro5.nameserver import start_ns_loop
from Pyro5.server import expose, Daemon
from geopy.distance   import great_circle
from enum             import Enum
from interfaces       import *

import threading
import time


class Coordinate:
    earth_radius = 6378100


    class Returns(Enum):
        NO_ERROR               = 0
        LATITUDE_NOT_FLOAT     = 1
        LONGITUDE_NOT_FLOAT    = 2
        LATITUDE_OUT_OF_RANGE  = 3
        LONGITUDE_OUT_OF_RANGE = 4


    def __init__(self, latitude: float, longitude: float):
        self.lat: float = latitude
        self.lon: float = longitude


    def get_distance(self, coord: Coordinate) -> int:

        coord1 = (self.lat, self.lon)
        coord2 = (coord.lat, coord.lon)

        distance = great_circle(coord1, coord2).m

        return int(distance)


    def update_coordinate(self, latitude: float, longitude: float) -> Returns:
        if type(latitude) != float:
            return self.Returns.LATITUDE_NOT_FLOAT

        if type(longitude) != float:
            return self.Returns.LONGITUDE_NOT_FLOAT

        if -90 > latitude < 90:
            return self.Returns.LATITUDE_OUT_OF_RANGE

        if -180 < longitude > 180:
            return self.Returns.LATITUDE_OUT_OF_RANGE

        self.lat = latitude
        self.lon = longitude

        return self.Returns.NO_ERROR


    def __str__(self):
        return f'({self.lat}, {self.lon})'



class UserInformation:
    def __init__(self, user_name: str, distance: int,latitude=0.0, longitude=0.0):
        self.name      : str        = user_name
        self.distance  : int        = distance

        self.coordinate: Coordinate = Coordinate(latitude, longitude)


    def update_name(self, name: str):
        self.name = name


    def update_coordinate(self, latitude: float, longitude: float) -> Coordinate.Returns:
        return self.coordinate.update_coordinate(latitude, longitude)


    def __str__(self):
        return f'({self.name}: {self.coordinate})'



class Server(ServerInterface):
    server_id = "|@servidor@|"

    class Returns(Enum):
        NO_ERROR = 0
        WRONG_USER_NAME = 1
        USER_ALREADY_EXISTS = 2

    def __init__(self):
        self.user_list: List[UserInformation] = []

        thread_servidor = threading.Thread(target=start_ns_loop, daemon=True, kwargs={"host":"localhost", "port":9090, "enableBroadcast":False})
        thread_servidor.start()

        thread_servidors = threading.Thread(target=self.register, daemon=True)
        thread_servidors.start()


    @expose
    def add_user(self, user_name: str, distance: int,latitude=0.0, longitude=0.0):
        if self.get_user_by_name(user_name) is not None:
            return self.Returns.USER_ALREADY_EXISTS

        self.user_list.append(UserInformation(user_name, distance,latitude, longitude))
        return self.Returns.NO_ERROR


    @expose
    def update_coordinate(self, user_name:str, latitude: float, longitude: float) -> Optional[Returns, Coordinate.Returns]:
        user = self.get_user_by_name(user_name)
        if user is None:
            return self.Returns.WRONG_USER_NAME
        return user.update_coordinate(latitude, longitude)


    def get_user_by_name(self, user_name:str) -> Optional[UserInformation]:
        for user in self.user_list:
            if user.name == user_name:
                return user
        return None


    @expose
    def get_list_by_coordinate(self, user_name: str) -> List[str]:
        user_list_by_distance: List[str] = []

        user_info: UserInformation = self.get_user_by_name(user_name)

        if user_info is None:
            return []

        for user in self.user_list:
            distance = user_info.coordinate.get_distance(user.coordinate)
            if user != user_info and  user.distance > distance < user_info.distance :
                user_list_by_distance.append(user.name)

        return user_list_by_distance

    def connect(self) -> ClientInterface:
        while True:
            try:
                ns = locate_ns(port=9090)
                uri_remoto = ns.lookup("lucas")
                client: ClientInterface = Proxy(uri_remoto)
                break
            except Exception as e:
                print(f"name server connect:  {e}")
                time.sleep(1)

        return client

    @expose
    def send_message(self):
        client = self.connect()
        client.receive_message("|@servidor@|")


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


if __name__ == '__main__':
    server = Server()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando servidor...")



