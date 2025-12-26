import os
from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
from models import db
from models.member_model import Member
from sqlalchemy.exc import SQLAlchemyError

UPLOAD_FOLDER = 'static/avatars'

# 負責複數資源：/members
class MembersResource(Resource):
    def get(self):
        """讀取所有會員"""
        members = Member.query.all()
        # print (members[0].__dict__)
        # # return members, 200
        return [{
            "MemberId": m.MemberId, 
            "Name": m.Name, 
            "Email": m.Email,
            "Age": m.Age,
            "FileName": m.FileName
        } for m in members], 200

    def post(self):
        """新增會員 (包含檔案與資料)"""
        name = request.form.get("Name")
        email = request.form.get("Email")
        age = request.form.get("Age")
        password = request.form.get("Password")

        # 處理圖片
        file = request.files.get("File")
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        new_member = Member(
            Name=name,
            Email=email,
            Age=age,
            Password=password, # 建議實務上使用 hashed_pw
            FileName=filename
        )

        try:
            db.session.add(new_member)
            db.session.commit()
            return {"message": "成功建立會員", "id": new_member.MemberId}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "資料庫寫入失敗", "error": str(e)}, 500

# 負責單筆資源：/members/<id>
class MemberResource(Resource):
    def get(self, id):
        """讀取單筆會員"""
        member = Member.query.get(id)
        if not member:
            return {"message": "找不到該成員"}, 404
        return {
            "MemberId": member.MemberId,
            "Name": member.Name,
            "Email": member.Email,
            "Age": member.Age,
            "FileName": member.FileName
        }, 200

    def put(self, id):
        """修改單筆會員"""
        member = Member.query.get(id)
        if not member:
            return {"message": "找不到該成員"}, 404

        # 取得更新資料
        member.Name = request.form.get("Name", member.Name)
        member.Email = request.form.get("Email", member.Email)
        member.Age = request.form.get("Age", member.Age)

        # 處理檔案更新
        file = request.files.get("File")
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            member.FileName = filename

        try:
            db.session.commit()
            return {"message": "資料更新成功"}, 200
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "更新失敗"}, 500

    def delete(self, id):
        """刪除單筆會員"""
        member = Member.query.get(id)
        if not member:
            return {"message": "找不到該成員"}, 404
        
        try:
            db.session.delete(member)
            db.session.commit()
            return {"message": f"會員 {id} 已刪除"}, 200
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "刪除失敗"}, 500

# 帳號重複檢查
class MemberExistCheck(Resource):
    def get(self, name):
        member = Member.query.filter_by(Name=name).first()
        return {'name': name, 'exists': member is not None}, 200