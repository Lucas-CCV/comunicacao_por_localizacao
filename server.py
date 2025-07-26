from __future__     import annotations

from typing         import (List, Optional)
from geopy.distance import great_circle
from enum           import Enum



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


    def __str__(self):
        return f'({self.lat}, {self.lon})'


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



class Server:

    class Returns(Enum):
        NO_ERROR = 0
        WRONG_USER_NAME = 1


    def __init__(self):
        self.user_list: List[UserInformation] = []


    def add_user(self, user: UserInformation):
        self.user_list.append(user)


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


    def get_list_by_coordinate(self, user_info: UserInformation) -> List[UserInformation]:
        user_list_by_distance: List[UserInformation] = []

        for user in self.user_list:
            if user != user_info and user.coordinate.get_distance(user_info.coordinate) < user_info.distance:
                user_list_by_distance.append(user)

        return user_list_by_distance


    def send_message(self):
        pass


if __name__ == '__main__':
    coord_1 = Coordinate(19.0760, 72.8777)
    coord_2 = Coordinate(18.5204, 73.8567)

    user1 = UserInformation(user_name="lucas", distance=130000,latitude=19.0760, longitude=72.8777)
    user2 = UserInformation(user_name="pedro", distance=10,latitude=18.5204, longitude=73.8567)

    server = Server()

    server.add_user(user1)
    server.add_user(user2)

    some_user = server.get_user_by_name(user_name='lucas')
    if some_user is not None:
        print(some_user.coordinate)

    some_user = server.get_list_by_coordinate(user1)

    print(some_user[0])



