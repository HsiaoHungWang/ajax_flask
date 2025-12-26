from flask_restful import Resource
import time
class HelloWorld(Resource):
    def get(self):
        # time.sleep(5)  # 模擬延遲
        return {'message':'Hello, RESTful API!!'}