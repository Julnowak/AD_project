import datetime
import json
import time

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
# from .models import UserLike, Product, UserProduct, AppUser
# from .serializers import UserLikeSerializer

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.sql import text

Base = declarative_base()


class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connected')
        self.socket = "socket"

        db_string = "mysql+pymysql://szyszka1:reiUvwMb9qAjpyiN@mysql.agh.edu.pl/szyszka1"
        self.engine = create_engine(db_string)

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
        await self.channel_layer.group_discard(self.socket, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)

        ##### LIMIT #####
        try:
            limit = text_data_json['limit']
        except:
            limit = 100

        ##### TEMPERATURE #####
        stmt = text(f'SELECT temperature_measurements.temperature, measurements.timestamp FROM temperature_measurements JOIN measurements ON measurements.id = temperature_measurements.measurement_id JOIN sensors ON sensors.id = measurements.sensor_id limit {limit}')
        results = self.session.execute(stmt).fetchall()
        # print(results)

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
                    LIMIT {limit}
                ) AS subquery
            ''')
        minMaxAvgTemp = self.session.execute(stmt).fetchone()

        # min max avg
        print(minMaxAvgTemp)

        ##### HUMIDITY #####
        stmt = text(
            f'SELECT temperature_measurements.humidity, measurements.timestamp FROM temperature_measurements JOIN measurements ON measurements.id = temperature_measurements.measurement_id JOIN sensors ON sensors.id = measurements.sensor_id limit {limit}')
        results = self.session.execute(stmt).fetchall()
        print(results)

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
                    LIMIT {limit}
                ) AS subquery
            ''')
        minMaxAvgHum = self.session.execute(stmt).fetchone()

        # min max avg
        print(minMaxAvgHum)

        ##### SENSORS #####
        stmt2 = text(
            f'SELECT * FROM sensors')
        sensors = self.session.execute(stmt2).all()

        sens = []
        for s in sensors:
            sens.append({"id": s[0], "name": s[1]})


        ###### CLOUDY #####

        stmt = text('''
            SELECT 
                CASE
                    WHEN cloud_cover_total <= 33 THEN 'sunny'
                    WHEN cloud_cover_total > 33 AND cloud_cover_total <= 66 THEN 'medium'
                    ELSE 'cloudy'
                END AS cloud_status,
                COUNT(*) AS count
            FROM cloud_measurements
            GROUP BY cloud_status
            ORDER BY count DESC 
        ''')

        cloudy_data = self.session.execute(stmt).fetchall()

        print(list(s[0] for s in cloudy_data))

        await self.channel_layer.group_send(
            self.socket, {'type': 'info.message', "temperature_plot": {"temperature": temp_y, "date": date_x,
                                                                       "max": round(minMaxAvgTemp[0], 2), "min": round(minMaxAvgTemp[1],2), "avg": round(minMaxAvgTemp[2],2)},
                          "humidity_plot": {"humidity": hum_y, "date": date_humx,
                                            "max": round(minMaxAvgHum[0], 2), "min": round(minMaxAvgHum[1],2), "avg": round(minMaxAvgHum[2],2)}, "sensors": sens,
                          "cloudy_plot": {"status": list(s[0] for s in cloudy_data), "number": list(s[1] for s in cloudy_data)}}
        )

    # Receive message from room group
    async def info_message(self, event):
        print(event)
        temperature_plot = event["temperature_plot"]
        humidity_plot = event["humidity_plot"]
        cloudy_plot = event["cloudy_plot"]
        sensors = event["sensors"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"cloudy_plot": cloudy_plot, "humidity_plot": humidity_plot, "temperature_plot": temperature_plot, "sensors": sensors}))

    # @sync_to_async
    # def set_like(self, productId, userId):
    #     if UserLike.objects.filter(user_id=int(userId), product_id=productId).exists():
    #         UserLike.objects.get(user_id=int(userId), product_id=productId).delete()
    #     else:
    #         UserLike.objects.create(user_id=int(userId), product_id=productId)
    #     p = Product.objects.get(id=productId)
    #     p.likes = UserLike.objects.filter(product_id=productId).count()
    #     p.save()
    #     likes = UserLike.objects.filter(user_id=userId)
    #     ser = UserLikeSerializer(likes, many=True).data
    #     return ser
