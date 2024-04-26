import random
import uuid
import csv
import os

import pandas as pd
import numpy as np

from GenericSensor import GenericSensor

if __name__ == "__main__":

    if not os.path.exists('iot_sensor_grid.csv'):
        # settings
        dict_sensor_type_unit = {'temperature':'C',
                                'humidity':'%',
                                'luminosity':'lx',
                                'wind_speed': 'm/s',
                                'atmospheric_pressure': 'hpa'
                                }

        ## sensors measurements range
        dict_sensor_type_range = {'temperature':(-30, 40),
                                'humidity':(0,100),
                                'luminosity':(0,1e5),
                                'wind_speed': (0,5),
                                'atmospheric_pressure': (965,1045)
                                }

        ## sensors fs range
        fs_range = [0.001, 0.01, 0.1, 1, 10, 100, 1000]

        location_number = 30
        ## location random list:(lon,lat)
        lon_range = (19850928, 20179723)
        lat_range = (50010828, 50110891)
        location_list =[ (np.random.randint(lon_range[0],lon_range[1])*1e-6,np.random.randint(lat_range[0],lat_range[1])*1e-6) for i in range(0,location_number)]

        #generate_structure
        sensors_number = 100

        list_sensors_params = []
        dic_sensors_type_number = {key:0 for key in dict_sensor_type_unit.keys()}

        for i in range(0,sensors_number):
            sensor, unit = random.choice(list(dict_sensor_type_unit.items()))
            location = random.choice(location_list)
            list_sensors_params.append({
                'name': f'{sensor}_{dic_sensors_type_number[sensor]}', 
                'serial_number': str(uuid.uuid4().hex), 
                'unit': unit, 
                'min_val': dict_sensor_type_range[sensor][0], 
                'max_val': dict_sensor_type_range[sensor][1], 
                'fs': random.choice(fs_range), 
                'lon': location[0], 
                'lat': location[1], 
                'ip_address':'localhost'
            })

            dic_sensors_type_number[sensor] += 1

        with open('iot_sensor_grid.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = list_sensors_params[0].keys())
            writer.writeheader()
            writer.writerows(list_sensors_params)
    


    grid_structure_data = pd.read_csv('iot_sensor_grid.csv')
    if 'port' not in grid_structure_data:
        grid_structure_data['port'] = None
    
    sensors_list = []
    for id, row in grid_structure_data.iterrows():

        sensors_list.append(GenericSensor(
                                            name = row['name'], 
                                            serial_number = row ['serial_number'] , 
                                            unit = row['unit'], 
                                            min_val = row['min_val'], 
                                            max_val = row['max_val'], 
                                            fs = row['fs'],  
                                            lon = row['lon'], 
                                            lat = row['lat'], 
                                            ip_address= row['ip_address'], 
                                            port = row['port'] 
                                          ))

    sensors_list_dict = [element.sensor2dict() for element in sensors_list]
    with open('iot_sensor_grid.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = sensors_list_dict[0].keys())
            writer.writeheader()
            writer.writerows(sensors_list_dict)

    
    try:
        for sensor in sensors_list:
            print(sensor)
            sensor.start()
        for sensor in sensors_list:
            sensor.join()
        while True:
            pass
    except:
        for sensor in sensors_list:
            sensor.kill()
        for sensor in sensors_list:
            sensor.join()
    finally:
        for sensor in sensors_list:
            sensor.kill()
        for sensor in sensors_list:
            sensor.join()