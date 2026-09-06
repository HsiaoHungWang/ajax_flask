from flask_restful import Resource
from flask import request
from sqlalchemy import or_, func
from models import db
from models.attraction_model import Attraction, AttractionImage

class Attractions(Resource):
    def get(self):
        # 1. 取得 QueryString 參數
        keyword = request.args.get('keyword', '').strip()
        page = int(request.args.get('page', 1))
        per_page = max(3, min(int(request.args.get('per_page', 9)), 45))
        sort_by = request.args.get('sort_by', 'AttractionID')
        sort_order = request.args.get('sort_order', 'asc').lower()

        # 2. 驗證與設定動態排序
        valid_sort_fields = {'AttractionID': Attraction.AttractionID, 'AttractionName': Attraction.AttractionName}
        sort_column = valid_sort_fields.get(sort_by, Attraction.AttractionID)
        sort_expr = sort_column.asc() if sort_order == 'asc' else sort_column.desc()

        # 3. 建立查詢基礎 (Query Object)
        query = Attraction.query

        # 4. 動態增加篩選條件
        if keyword:
            query = query.filter(
                or_(
                    Attraction.AttractionName.contains(keyword),
                    Attraction.Description.contains(keyword)
                )
            )

        # 5. 分頁
        pagination = query.order_by(sort_expr).paginate(page=page, per_page=per_page, error_out=False)

        # 6. 取得這一頁每個景點的第一張圖片 (以 id 最小的一筆代表)
        attraction_ids = [a.AttractionID for a in pagination.items]
        images = {}
        if attraction_ids:
            first_ids = db.session.query(
                func.min(AttractionImage.id)
            ).filter(AttractionImage.attraction_id.in_(attraction_ids))\
             .group_by(AttractionImage.attraction_id).all()
            first_ids = [row[0] for row in first_ids]

            if first_ids:
                image_rows = AttractionImage.query.filter(AttractionImage.id.in_(first_ids)).all()
                images = {img.attraction_id: img.URL for img in image_rows}

        data = [{
            "AttractionID": a.AttractionID,
            "AttractionName": a.AttractionName,
            "Description": a.Description,
            "City": a.City,
            "Town": a.Town,
            "StreetAddress": a.StreetAddress,
            "Image": images.get(a.AttractionID)
        } for a in pagination.items]

        return {
            'total_pages': pagination.pages,
            'total_count': pagination.total,
            'data': data
        }, 200

class AttractionTitleSearch(Resource):
    def get(self):
        keyword = request.args.get('keyword', '')

        results = Attraction.query.filter(Attraction.AttractionName.like(f'%{keyword}%'))\
                    .order_by(Attraction.AttractionID.asc())\
                    .limit(10).all()

        return [row.AttractionName for row in results], 200


class AttractionCityStats(Resource):
    """各縣市景點數量統計（長條圖用）。"""
    def get(self):
        results = db.session.query(
            Attraction.City,
            func.count(Attraction.AttractionID).label("count")
        ).filter(Attraction.City.isnot(None), Attraction.City != "")\
         .group_by(Attraction.City)\
         .order_by(func.count(Attraction.AttractionID).desc()).all()

        # 沿用 {category, count} 的鍵名，前端沿用既有邏輯
        data = [{"category": row.City, "count": row.count} for row in results]
        return {"data": data}, 200


class AttractionsByCity(Resource):
    """某縣市的所有景點座標（地圖用）。"""
    def get(self):
        city = request.args.get('city', '').strip()

        query = Attraction.query.with_entities(
            Attraction.AttractionName,
            Attraction.PositionLat,
            Attraction.PositionLon,
        )
        if city:
            query = query.filter(Attraction.City == city)

        results = query.all()
        data = [
            {
                "title": row.AttractionName,
                "lat": row.PositionLat,
                "lng": row.PositionLon,
            }
            for row in results
            if row.PositionLat and row.PositionLon
        ]
        return data, 200
