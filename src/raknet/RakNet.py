import socket as sc;

class RakNet:
    def __init__(self, ip: str, port: int):
        self.socket = sc.socket(sc.AF_INET, sc.SOCK_DGRAM, sc.SOL_UDP);
        self.socket.setsockopt(sc.SOL_SOCKET, sc.SO_REUSEADDR, 1);
        self.socket.setsockopt(sc.SOL_SOCKET, sc.SO_BROADCAST, 1);
        try:
            self.socket.bind((ip, port));
        except sc.error:
            raise Exception(f"Failed bind on {ip, str(port)}");
        self.socket.setblocking(False);

    def recive(self):
        try:
            return self.socket.recvfrom(65535);
        except sc.error:
            return False;

    def send(self, data: bytes, ip: str, port: int):
        try:
            self.socket.sendto(data, (ip, port));
        except sc.error:
            return "Failed sending data";

    def close(self):
        self.socket.close();