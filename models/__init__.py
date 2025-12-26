from flask_sqlalchemy import SQLAlchemy

# 初始化 SQLAlchemy，這會作為所有模型的基類
db = SQLAlchemy()

# 讓所有模型在這裡集合，這樣 app.py 只要匯入 db 就能抓到所有模型
from .member_model import Member
from .user_model import User
# from .spot_model import Spot
from .address_model import Address
# from .category_model import SpotCategory