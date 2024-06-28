import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import select, func, case
from sqlalchemy import MetaData, Table, inspect, text

Base = declarative_base()
metadata = MetaData()


class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connected')
        self.socket = "socket"

        db_string = "mysql+pymysql://szewczyk:hbe2m7tZmX56ectN@mysql.agh.edu.pl/szewczyk"
        self.engine = create_engine(db_string)

        tables = {column_name: Table(column_name, metadata, autoload_with=self.engine) for column_name in
                  inspect(self.engine).get_table_names()}

        # Define table aliases
        self.measurements = tables['measurements']
        self.sensors = tables['sensors']
        self.pressure_measurements = tables["pressure_measurements"]
        self.wind_measurements = tables["wind_measurements"]
        self.cloud_measurements = tables["cloud_measurements"]
        self.temperature_measurements = tables["temperature_measurements"]

        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        stmt = text('select * from sensors')
        results = self.session.execute(stmt).fetchall()
        print(results)

        # Join room group
        await self.channel_layer.group_add(self.socket, self.channel_name)

        print(get_channel_layer())
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        print('disconnected')
        self.session.close()
        await self.channel_layer.group_discard(self.socket, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)

        ##### FILTERS #####

        try:
            limit = text_data_json['limit']
        except:
            limit = 100

        try:
            start_date = text_data_json['startdate']
            if start_date is None:
                start_date = datetime.datetime(1990,1,1,1)
            print(start_date)
        except:
            start_date = datetime.datetime(1990,1,1,1)

        try:
            end_date = text_data_json['enddate']
            if end_date is None:
                end_date = datetime.datetime.now()
        except:
            end_date = datetime.datetime.now()

        try:
            sensor_loc = text_data_json['sensor']
            if sensor_loc is None:
                sensor_loc = "New York"
        except:
            sensor_loc = "New York"

        ##### TEMPERATURE #####
        stmt = text(f'SELECT temperature_measurements.temperature, measurements.timestamp FROM temperature_measurements '
                    f'JOIN measurements ON measurements.id = temperature_measurements.measurement_id '
                    f'JOIN sensors ON sensors.id = measurements.sensor_id '
                    f'WHERE location = "{sensor_loc}" AND measurements.timestamp BETWEEN "{start_date}" AND "{end_date}"'
                    f'LIMIT {limit}')
        results = self.session.execute(stmt).fetchall()

        temp_y = []
        date_x = []
        for i in results:
            temp_y.append(i[0])
            date_x.append(str(i[1]))

        stmt = text(
            f'''
                SELECT 
                    MAX(subquery.temperature), 
                    MIN(subquery.temperature), 
                    AVG(subquery.temperature) 
                FROM (
                    SELECT temperature_measurements.temperature
                    FROM temperature_measurements 
                    JOIN measurements ON measurements.id = temperature_measurements.measurement_id 
                    JOIN sensors ON sensors.id = measurements.sensor_id 
                    WHERE location = "{sensor_loc}" AND measurements.timestamp BETWEEN "{start_date}" AND "{end_date}"
                    LIMIT {limit}
                ) AS subquery
            ''')
        minMaxAvgTemp = self.session.execute(stmt).fetchone()

        ##### HUMIDITY #####
        stmt = text(
            f'SELECT temperature_measurements.humidity, measurements.timestamp FROM temperature_measurements '
            f'JOIN measurements ON measurements.id = temperature_measurements.measurement_id '
            f'JOIN sensors ON sensors.id = measurements.sensor_id '
            f'WHERE location = "{sensor_loc}" AND measurements.timestamp BETWEEN "{start_date}" AND "{end_date}"'
            f'LIMIT {limit}')
        results = self.session.execute(stmt).fetchall()

        hum_y = []
        date_humx = []
        for i in results:
            hum_y.append(i[0])
            date_humx.append(str(i[1]))

        stmt = text(
            f'''
                SELECT 
                    MAX(subquery.humidity), 
                    MIN(subquery.humidity), 
                    AVG(subquery.humidity) 
                FROM (
                    SELECT temperature_measurements.humidity
                    FROM temperature_measurements 
                    JOIN measurements ON measurements.id = temperature_measurements.measurement_id 
                    JOIN sensors ON sensors.id = measurements.sensor_id 
                    WHERE location = "{sensor_loc}" AND measurements.timestamp BETWEEN "{start_date}" AND "{end_date}"
                    LIMIT {limit}
                ) AS subquery
            ''')
        minMaxAvgHum = self.session.execute(stmt).fetchone()

        ##### SENSORS #####
        stmt2 = text(
            f'SELECT * FROM sensors')
        sensors = self.session.execute(stmt2).all()

        sens = []
        for s in sensors:
            sens.append({"id": s[0], "name": s[1], "location": s[2]})


        ###### CLOUDY #####

        query = (
            select(
                case(
                    (self.cloud_measurements.c.cloud_cover_total <= 33, 'Słonecznie'),
                    (self.cloud_measurements.c.cloud_cover_total.between(34, 66), 'Umiarkowanie'),
                    else_='Pochmurno'
                ).label('cloud_status'),
                func.count().label('count')
            )
            .select_from(self.cloud_measurements)
            .join(self.measurements, self.cloud_measurements.c.measurement_id == self.measurements.c.id)
            .join(self.sensors, self.measurements.c.sensor_id == self.sensors.c.id)
            .where(self.sensors.c.location.in_((sensor_loc, )))
            .filter(self.measurements.c.timestamp.between(start_date, end_date))
            .group_by('cloud_status')
            .order_by(func.count().desc())
            )

        stmt = text(f'''
                    SELECT cloud_status, COUNT(*) FROM(
            SELECT 
                CASE
                    WHEN cloud_cover_total <= 33 THEN 'Słonecznie'
                    WHEN cloud_cover_total > 33 AND cloud_cover_total <= 66 THEN 'Umiarkowanie'
                    ELSE 'Pochmurnie'
                END 
            AS cloud_status, cloud_cover_total,  measurements.timestamp,  sensors.location
            FROM cloud_measurements
            JOIN measurements ON measurements.id = cloud_measurements.measurement_id 
            JOIN sensors ON sensors.id = measurements.sensor_id
            WHERE location = "{sensor_loc}" AND measurements.timestamp BETWEEN "{start_date}" AND "{end_date}"
            LIMIT {limit}
            ) AS subquery
            GROUP BY cloud_status
                ''')

        cloudy_data = self.session.execute(stmt).fetchall()
        print(cloudy_data)

        ##### PRESSURE #####

        query = (
            select(self.pressure_measurements.c.surface_pressure, self.measurements.c.timestamp, self.sensors.c.location)
                .join(self.measurements, self.pressure_measurements.c.measurement_id == self.measurements.c.id)
                .join(self.sensors, self.measurements.c.sensor_id == self.sensors.c.id)
                .where(self.sensors.c.location.in_((sensor_loc,)))
                .filter(self.measurements.c.timestamp.between(start_date, end_date))
                .limit(limit)
        )

        stmt = text(
            f'''
                        SELECT 
                            MAX(subquery.surface_pressure), 
                            MIN(subquery.surface_pressure), 
                            AVG(subquery.surface_pressure) 
                        FROM (
                            SELECT pressure_measurements.surface_pressure
                            FROM pressure_measurements
                            JOIN measurements ON measurements.id = pressure_measurements.measurement_id 
                            JOIN sensors ON sensors.id = measurements.sensor_id 
                            WHERE location = "{sensor_loc}" AND measurements.timestamp BETWEEN "{start_date}" AND "{end_date}"
                            LIMIT {limit}
                        ) AS subquery
                    ''')
        minMaxAvgPress = self.session.execute(stmt).fetchone()
        pressure_data = self.session.execute(query).fetchall()

        press_val = []
        press_date = []
        for i in pressure_data:
            press_val.append(i[0])
            press_date.append(str(i[1]))

        ##### WIND #####

        query = (
            select(self.wind_measurements.c.wind_speed_10m, self.wind_measurements.c.wind_gusts_10m,
                   self.wind_measurements.c.wind_direction_10m, self.measurements.c.timestamp, self.sensors.c.id)
                .join(self.measurements, self.wind_measurements.c.measurement_id == self.measurements.c.id)
                .join(self.sensors, self.measurements.c.sensor_id == self.sensors.c.id)
                .where(self.sensors.c.location.in_((sensor_loc,)))
                .limit(limit)
                .filter(self.measurements.c.timestamp.between(start_date, end_date))

        )

        stmt = text(
            f'''
                                SELECT 
                                    MAX(subquery.wind_speed_10m), 
                                    MIN(subquery.wind_speed_10m), 
                                    AVG(subquery.wind_speed_10m) 
                                FROM (
                                    SELECT wind_measurements.wind_speed_10m
                                    FROM wind_measurements
                                    JOIN measurements ON measurements.id = wind_measurements.measurement_id 
                                    JOIN sensors ON sensors.id = measurements.sensor_id 
                                    WHERE location = "{sensor_loc}" AND measurements.timestamp BETWEEN "{start_date}" AND "{end_date}"
                                    LIMIT {limit}
                                ) AS subquery
                            ''')

        minMaxAvgWindSpeed = self.session.execute(stmt).fetchone()
        windy_data = self.session.execute(query).fetchall()

        windy_speed = []
        windy_gusts = []
        windy_direct = []
        windy_date = []

        for i in windy_data:
            windy_speed.append(i[0])
            windy_gusts.append(i[1])
            windy_direct.append(i[2])
            windy_date.append(str(i[3]))

        # print(windy_data)

        await self.channel_layer.group_send(
            self.socket, {'type': 'info.message', "temperature_plot": {"temperature": temp_y, "date": date_x,
                                                                       "max": round(minMaxAvgTemp[0], 2), "min": round(minMaxAvgTemp[1],2), "avg": round(minMaxAvgTemp[2],2)},
                          "humidity_plot": {"humidity": hum_y, "date": date_humx,
                                            "max": round(minMaxAvgHum[0], 2), "min": round(minMaxAvgHum[1],2), "avg": round(minMaxAvgHum[2],2)}, "sensors": sens,
                          "cloudy_plot": {"status": list(s[0] for s in cloudy_data), "number": list(s[1] for s in cloudy_data)},
                          "pressure_plot": {"date": press_date, "value": press_val,
                                            "max": round(minMaxAvgPress[0], 2), "min": round(minMaxAvgPress[1],2), "avg": round(minMaxAvgPress[2],2)},
                          "windy_plot": {"speed": windy_speed, "gusts": windy_gusts, "direction": windy_direct, "date": windy_date,
                                         "max": round(minMaxAvgWindSpeed[0], 2), "min": round(minMaxAvgWindSpeed[1],2), "avg": round(minMaxAvgWindSpeed[2],2)},
                          "sensor": sensor_loc}
        )

    # Receive message from room group
    async def info_message(self, event):
        temperature_plot = event["temperature_plot"]
        humidity_plot = event["humidity_plot"]
        cloudy_plot = event["cloudy_plot"]
        sensors = event["sensors"]
        sensor_loc = event["sensor"]
        pressure_plot = event["pressure_plot"]
        windy_plot = event["windy_plot"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"cloudy_plot": cloudy_plot, "humidity_plot": humidity_plot, "temperature_plot": temperature_plot, "sensors": sensors,
                                              "sensor": sensor_loc, "pressure_plot": pressure_plot, "windy_plot": windy_plot}))
