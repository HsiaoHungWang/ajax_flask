from flask_restful import Resource
class Items(Resource):
    def get(self):                                                # GET /items
        return {'message': '讀取所有資料'}, 200
    def post(self):                                              # POST /items
        return {'message': '新增資料'}, 201

class Item(Resource):
    def get(self, id):                                           # GET /items/<id>   
        return {'message': f'根據{id}讀取資料'}, 200
    def put(self, id):                                           # PUT /items/<id>    
        return {'message': f'根據{id}修改資料'}, 200   
    def delete(self, id):                                      # DELETE /items/<id>
        return {'message': f'根據{id}刪除資料'},200
