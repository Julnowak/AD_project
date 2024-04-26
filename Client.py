import socket
import threading            
 
class SensorConnection(threading.Thread):
    def __init__(self, port, ip_address='localhost') -> None:
        threading.Thread.__init__(self)
        self.port = port
        self.ip_address = ip_address
        self.sensor_socket = socket.socket()
        self.buffer = []
    
    def run(self):
        try:
            self.sensor_socket.connect((self.ip_address, self.port))
            while True:
                self.buffer.append(self.sensor_socket.recv(1024).decode())
        except:
            self.sensor_socket.close()

if __name__ == '__main__':
    n = 53845

    # Connect to database

    sensors = []
    while n <=  53944:
        sensor = SensorConnection(port=n)
        sensor.start()
        sensors.append(sensor)
        n+= 1
    
    counter = 300 # Czas
    c = 0
    while True:
        list_of_values = []
        while c < counter:
            for sen in sensors:
                if len(sen.buffer)>0:
                    new = sen.buffer.pop(0)
                    list_of_values.append(new)
                    print(new)
            c += 1

        # Insert do bazy wszystkich z list_of_values
        c = 0

    