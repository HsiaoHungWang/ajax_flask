from flask import Blueprint
from flask_restful import Api
from resources.hello_api import HelloWorld, TextResource, ImageResource, JsonResource  #hello.py 檔案中的 HelloWorld 類別名稱
from resources.items_api import Items, Item  
from resources.member_api import MembersResource, MemberResource, MemberExistCheck
from resources.address_api import  CityResource, DistrictResource, RoadResource
from resources.demo_api import QueryStringDemo, PathDemo, FormDataDemo, JsonDemo, ImageUploadDemo
from resources.spot_api import Spots, SpotCategoryStats, SpotsByDistrict, SpotTitleSearch
from resources.attraction_api import Attractions, AttractionTitleSearch
from resources.attraction_recognition_api import AttractionImageRecognition


api_bp = Blueprint('api', __name__)
api = Api(api_bp)


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

api.add_resource(Spots, '/spots')
api.add_resource(SpotCategoryStats, '/categories')
api.add_resource(SpotsByDistrict, '/spot-district')

api.add_resource(Attractions, '/attractions')
api.add_resource(AttractionTitleSearch, '/attraction-title')
api.add_resource(AttractionImageRecognition, '/attraction/recognize')


api.add_resource(MembersResource, '/members')
api.add_resource(MemberResource, '/members/<int:id>')
api.add_resource(MemberExistCheck, '/member/check/<string:name>')