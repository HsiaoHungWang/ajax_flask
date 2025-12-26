from flask import Blueprint
from flask_restful import Api
from resources.hello_api import HelloWorld  #hello.py 檔案中的 HelloWorld 類別名稱
from resources.image_api import ImageResource 
from resources.items_api import Items, Item  
from resources.member_api import MembersResource, MemberResource, MemberExistCheck
from resources.address_api import  CityResource, DistrictResource, RoadResource
from resources.demo_api import QueryStringDemo, PathDemo, FormDataDemo, JsonDemo



api_bp = Blueprint('api', __name__)
api = Api(api_bp)



 #設定路由
api.add_resource(HelloWorld, '/hello')  
api.add_resource(ImageResource, '/image')

api.add_resource(Items, '/items')
api.add_resource(Item, '/item/<int:id>')

api.add_resource(CityResource, '/cities')
api.add_resource(DistrictResource, '/districts')
api.add_resource(RoadResource, '/roads')


api.add_resource(QueryStringDemo, '/demo/query')
api.add_resource(PathDemo, '/demo/path/<string:name>/<int:age>')
api.add_resource(FormDataDemo, '/demo/form')
api.add_resource(JsonDemo, '/demo/json')    

# 集合操作 (所有會員)
api.add_resource(MembersResource, '/members')
    
# 單體操作 (特定 ID)
api.add_resource(MemberResource, '/member/<int:id>')
    
# 特殊功能 (姓名檢查)
api.add_resource(MemberExistCheck, '/member/check/<string:name>')