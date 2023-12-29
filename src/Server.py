from threading import Thread;
from struct import pack;
from shutil import copyfile;
from os.path import exists;
from time import sleep;
from os import urandom;
from json import load;

from src.raknet.RakNet import RakNet;

class Server:
    def __init__(self):
        self.running = True;

        #config
        if not exists("server_config.json"):
            copyfile("src/configs/server_config.json", "server_config.json");
        with open("server_config.json", "r", encoding='utf-8') as file:
            self.config = load(file);
            file.close();
        self.ip = self.config["ip"];
        self.port = int(self.config["port"]);
        self.motd1 = self.config["motd1"];
        self.motd2 = self.config["motd2"];
        self.max_players = self.config["max_players"];
        self.seed = self.config["seed"];

        #creating server
        self.server = RakNet(self.ip, self.port);
        self.serverGUID = urandom(8);
        self.serverID = "MCPE;" + self.motd1 + ";630;1.20.50;0;" + str(self.max_players) + ";" + str(self.seed) + ";" + self.motd2 + ";Survival";
        self.magic = b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78";

        #handling packets
        self.raknetThread = Thread(target=self.processPackets, daemon=True);
        self.raknetThread.start();
        self.commandsThread = Thread(target=self.processCommands, daemon=False);
        self.commandsThread.start();

    def processPackets(self):
        while True:
            if not self.running:
                break;
            sleep(0.05);
            got = self.server.recive();
            if(got):
                match(got[0][0]):
                    case 1 | 2: #ping
                        pingid = got[0][1:1+8];
                        newpk = b"\x1c";
                        newpk += self.serverGUID;
                        newpk += pingid;
                        newpk += self.magic;
                        newpk += pack("h", len(self.serverID))[::-1];
                        newpk += self.serverID.encode("UTF-8");
                        self.server.send(newpk, got[1][0], got[1][1]);
                        del newpk;
                        pass;
                    case 5: #open connection request 1
                        newpk = b"\x06";
                        newpk += self.magic;
                        newpk += self.serverGUID;
                        newpk += b"\x00";
                        newpk += pack("h", len(got[0][18:]));
                        self.server.send(newpk, got[1][0], got[1][1]);
                        del newpk;
                        pass;
                    case 7: #open connection request 2
                        newpk = b"\x08";
                        newpk += self.magic;
                        newpk += self.serverGUID;
                        newpk += bytes(got[1][0].encode("UTF-8")) + bytes(str(got[1][1]).encode("UTF-8"));
                        newpk += pack("h", 1000); #idk what to put here... i mean yes, it's mtu but where i supposed to get it
                        newpk += pack("?", False);
                        self.server.send(newpk, got[1][0], got[1][1]);
                        del newpk;
                        pass;
                    case _:
                        print("Unhandled packet " + str(got[0][0]) + ": " + str(got[0]));
                        pass;

    def processCommands(self):
        while True:
            cmd = input();
            cmd = cmd.split(" ");
            match cmd[0]:
                case "stop":
                    self.running = False;
                    break;
                case "": #miss input
                    pass;
                case _:
                    print("Uknown command");
                    pass;