from flask import request
from flask_restful import Resource
from models import db
from models.address_model import Address # 假設你的模型名稱是 Address

class CityResource(Resource):
    def get(self):
        # ORM 寫法：查詢 Address 模型中的 city 欄位並去重
        results = db.session.query(Address.City).distinct().all()
        
        # results 會是像 [('台北市',), ('台中市',)] 這樣的 tuple 清單
        # 使用 row[0] 或 row.city 取得值
        return [row.City for row in results], 200

class DistrictResource(Resource):
    def get(self):
        city = request.args.get('city')
        if not city:
            return {"message": "請提供城市名稱"}, 400
            
        # ORM 寫法：filter_by 或 filter
        results = db.session.query(Address.Site_Id)\
                    .filter(Address.City == city)\
                    .distinct().all()
        
        return [row.Site_Id for row in results], 200
        
class RoadResource(Resource):
    def get(self):
        site_id = request.args.get('site_id')
        if not site_id:
            return {"message": "請提供區域 ID (site_id)"}, 400
            
        # ORM 寫法
        results = db.session.query(Address.Road)\
                    .filter(Address.Site_Id == site_id)\
                    .distinct().all()
        
        return [row.Road for row in results], 200