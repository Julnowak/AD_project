import socket
import json
import threading
import datetime
import time

import numpy as np
import pandas as pd

print_lock = threading.Lock()

class Client():
    def __init__(self, ip, port, connection):
        self.connection = connection
        self.ip = ip
        self.port = port

    def run(self):
        start = time.time()
        while True:
            if start - time.time() > 1/self.fs:
                self.buffer.append(np.random.uniform(self.min_val, self.max_val))


class GenericSensor(threading.Thread):
    def __init__(self, name, serial_number, unit, min_val, max_val, fs, lon, lat, ip_address='localhost', port = None) -> None:
        threading.Thread.__init__(self)
        self.name = name
        self.serial_number = serial_number
        self.ip_address = ip_address
        
        self.unit = unit
        self.max_val = max_val
        self.min_val = min_val
        self.fs = fs
        self.lon = lon
        self.lat = lat
        
        self.server = socket.socket()
        if port is None:
            self.server.bind((self.ip_address, 0))
            self.port = self.server.getsockname()[1]
        else:
            self.server.bind((self.ip_address, port))
            self.port = port

        self.clients = []
        self.buffer = []

    def broadcast_val(self):
        while True:
            if len(self.buffer) > 0:
                val = self.buffer.pop(0)
                data = self.measure_to_json(val[0],val[1])
                for client in self.clients:
                    try:
                        client.connection.sendall(str.encode(data))
                    except BrokenPipeError as ex:
                        self.clients.remove(client)

    def measurement_sim(self):
        start = time.time()
        while True:
            if np.abs(start - time.time()) > (1.0/self.fs):
                self.buffer.append((np.random.uniform(self.min_val, self.max_val),time.time()))
                start = time.time()
     
    def run(self):
        self.run = True
        thread_measurement_sim = threading.Thread(target = self.measurement_sim)
        thread_measurement_sim.start()

        thread_broadcast_val= threading.Thread(target = self.broadcast_val)
        thread_broadcast_val.start()

        self.server.listen(5)

        while self.run :
            try:
                connection, (ip, port) = self.server.accept()
                client = Client(ip, port, connection)
                self.clients.append(client)
            except:
                self.server.close()

        self.server.close()

    def measure_to_json(self, val,date):
        dict__ = {'name': self.name,
                'serial_number': self.serial_number, 
                'ip_address': self.ip_address,
                'port': self.port,
                'unit': self.unit,
                'lon':self.lon,
                'lat':self.lat,
                'value': val,
                'date': date
                }
        return json.dumps(dict__)

    def __str__(self) -> str:
        description = 'name: {},\n\tserial_number: {},\n\tip_address: {},\n\tport:{},\n\tunit:{},\n\tlon:{},\n\tlat:{}'.format(
            self.name,
            self.serial_number, 
            self.ip_address,
            self.port,
            self.unit,
            self.lon,
            self.lat,
            )
        return description
    
    def sensor2dict(self)->dict:
        return {
            'name': self.name, 
            'serial_number':self.serial_number, 
            'unit': self.unit, 
            'min_val': self.min_val, 
            'max_val': self.max_val, 
            'fs': self.fs, 
            'lon': self.lon, 
            'lat': self.lat, 
            'ip_address': self.ip_address,
            'port': self.port
        }
    
    def kill(self):
        self.run = False