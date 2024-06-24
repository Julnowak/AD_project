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

        try:
            limit = text_data_json['limit']
        except:
            limit = 100
        stmt = text(f'SELECT temperature_measurements.temperature, measurements.timestamp FROM temperature_measurements JOIN measurements ON measurements.id = temperature_measurements.measurement_id JOIN sensors ON sensors.id = measurements.sensor_id limit {limit}')
        results = self.session.execute(stmt).fetchall()
        # l = []
        # for i in results:
        #     l.append(l[0])
        print(results)

        # productId = text_data_json['productId']
        # userId = text_data_json['userId']
        #
        # likes = await self.set_like(productId, userId)
        #
        await self.channel_layer.group_send(
            self.socket, {'type': 'info.message', "likes": [1, 2, 3, 4, 5]}
        )

    # Receive message from room group
    async def info_message(self, event):
        print(event)
        likes = event["likes"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"likes": likes}))

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
