#Nơi cấu hình database
"""
1.URL
2.engine
3.SessionLocal
4.get_db
"""
DB_URL = "mysql+pymysql://root:123456@Localhost:3306/fastapi"
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(
    auto
)