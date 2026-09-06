from flask import Blueprint
from flask_restful import Api
from flask_sock import Sock
from resources.hello_api import HelloWorld, TextResource, ImageResource, JsonResource  #hello.py 檔案中的 HelloWorld 類別名稱
from resources.items_api import Items, Item  
from resources.member_api import MembersResource, MemberResource, MemberExistCheck
from resources.address_api import  CityResource, DistrictResource, RoadResource
from resources.demo_api import QueryStringDemo, PathDemo, FormDataDemo, JsonDemo, ImageUploadDemo
from resources.attraction_api import (
    Attractions,
    AttractionTitleSearch,
    AttractionCityStats,
    AttractionsByCity,
)
from resources.attraction_recognition_api import AttractionImageRecognition
from resources.attraction_recognition_stream_api import attraction_recognize_stream
from resources.attraction_recognition_local_api import attraction_recognize_local
from resources.attraction_recognition_ws_api import init_ws


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# WebSocket 路由（flask_sock），掛在同一個 api 藍圖上 → /api/attraction/recognize-ws
sock = Sock(api_bp)
init_ws(sock)


# http://127.0.0.1:5000/api/  #api哪裡來的
 #設定路由
 # http://127.0.0.1:5000/api/hello
api.add_resource(HelloWorld, '/hello')  
# http://127.0.0.1:5000/api/text
api.add_resource(TextResource, '/text')
# http://127.0.0.1:5000/api/image  
api.add_resource(ImageResource, '/image')
api.add_resource(JsonResource, '/json')

api.add_resource(Items, '/items')
# http://127.0.0.1:5000/api/items/1
api.add_resource(Item, '/items/<int:id>')

api.add_resource(CityResource, '/cities')
api.add_resource(DistrictResource, '/districts')
api.add_resource(RoadResource, '/roads')


api.add_resource(QueryStringDemo, '/demo/query')
# http://127.0.0.1:5000/api/demo/path/John/25
api.add_resource(PathDemo, '/demo/path/<string:name>/<int:age>')
api.add_resource(FormDataDemo, '/demo/form')
api.add_resource(JsonDemo, '/demo/json')  
api.add_resource(ImageUploadDemo, '/demo/image')  

api.add_resource(Attractions, '/attractions')
api.add_resource(AttractionTitleSearch, '/attraction-title')
api.add_resource(AttractionCityStats, '/attraction-city-stats')
api.add_resource(AttractionsByCity, '/attractions-by-city')
api.add_resource(AttractionImageRecognition, '/attraction/recognize')
# 串流版不是 flask_restful 的 Resource，直接掛一般的 Flask 路由
api_bp.add_url_rule(
    '/attraction/recognize-stream',
    view_func=attraction_recognize_stream,
    methods=['POST'],
)
# 地端模型版（Ollama），一樣走 SSE 串流
api_bp.add_url_rule(
    '/attraction/recognize-local',
    view_func=attraction_recognize_local,
    methods=['POST'],
)


api.add_resource(MembersResource, '/members')
api.add_resource(MemberResource, '/members/<int:id>')
api.add_resource(MemberExistCheck, '/member/check/<string:name>')