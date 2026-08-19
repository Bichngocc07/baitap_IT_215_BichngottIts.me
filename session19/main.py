from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    relationship,
    Session
)


# ==================================================
# KẾT NỐI MYSQL
# ==================================================

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/supply_chain_db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==================================================
# MODEL WAREHOUSE
# ==================================================

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    warehouse_name = Column(
        String(100),
        nullable=False
    )

    location = Column(
        String(255),
        nullable=False
    )

    packages = relationship(
        "Package",
        back_populates="warehouse"
    )


# ==================================================
# MODEL PACKAGE
# ==================================================

class Package(Base):
    __tablename__ = "packages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    package_code = Column(
        String(100),
        unique=True,
        nullable=False
    )

    weight = Column(
        Float,
        nullable=False
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )

    warehouse = relationship(
        "Warehouse",
        back_populates="packages"
    )

    # Quan hệ 1 - 1
    waybill = relationship(
        "Waybill",
        back_populates="package",
        uselist=False
    )


# ==================================================
# MODEL WAYBILL
# ==================================================

class Waybill(Base):
    __tablename__ = "waybills"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    tracking_number = Column(
        String(100),
        unique=True,
        nullable=False
    )

    shipping_status = Column(
        String(50),
        nullable=False
    )

    package_id = Column(
        Integer,
        ForeignKey("packages.id"),
        unique=True,
        nullable=False
    )

    package = relationship(
        "Package",
        back_populates="waybill"
    )


# ==================================================
# TẠO BẢNG
# ==================================================

Base.metadata.create_all(
    bind=engine
)


# ==================================================
# SCHEMA
# ==================================================

class WarehouseCreate(BaseModel):
    warehouse_name: str
    location: str


class PackageInWarehouse(BaseModel):
    id: int
    package_code: str
    weight: float
    warehouse_id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class WarehouseDetailResponse(BaseModel):
    id: int
    warehouse_name: str
    location: str
    packages: list[PackageInWarehouse] = []

    model_config = ConfigDict(
        from_attributes=True
    )


class PackageUpdate(BaseModel):
    package_code: str | None = None
    weight: float | None = None
    warehouse_id: int | None = None


class PackageResponse(BaseModel):
    id: int
    package_code: str
    weight: float
    warehouse_id: int

    model_config = ConfigDict(
        from_attributes=True
    )


# ==================================================
# FASTAPI
# ==================================================

app = FastAPI(
    title="Hệ thống quản lý chuỗi cung ứng",
    description="Quản lý nhà kho, kiện hàng và vận đơn",
    version="1.0.0"
)


# ==================================================
# TRANG CHỦ
# ==================================================

@app.get("/")
def trang_chu():
    return {
        "message": "Hệ thống quản lý chuỗi cung ứng đang hoạt động"
    }


# ==================================================
# 1. TẠO NHÀ KHO
# POST /warehouses
# ==================================================

@app.post(
    "/warehouses",
    response_model=WarehouseDetailResponse,
    status_code=status.HTTP_201_CREATED
)
def tao_nha_kho(
    data: WarehouseCreate,
    db: Session = Depends(get_db)
):

    try:

        nha_kho = Warehouse(
            **data.model_dump()
        )

        db.add(nha_kho)
        db.commit()
        db.refresh(nha_kho)

        return nha_kho

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tạo nhà kho: {str(e)}"
        )


# ==================================================
# 2. LẤY CHI TIẾT NHÀ KHO
# GET /warehouses/{warehouse_id}
# ==================================================

@app.get(
    "/warehouses/{warehouse_id}",
    response_model=WarehouseDetailResponse
)
def lay_chi_tiet_nha_kho(
    warehouse_id: int,
    db: Session = Depends(get_db)
):

    nha_kho = (
        db.query(Warehouse)
        .filter(
            Warehouse.id == warehouse_id
        )
        .first()
    )

    if nha_kho is None:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà kho"
        )

    return nha_kho


# ==================================================
# 3. CẬP NHẬT KIỆN HÀNG
# PATCH /packages/{package_id}
# ==================================================

@app.patch(
    "/packages/{package_id}",
    response_model=PackageResponse
)
def cap_nhat_kien_hang(
    package_id: int,
    data: PackageUpdate,
    db: Session = Depends(get_db)
):

    kien_hang = (
        db.query(Package)
        .filter(
            Package.id == package_id
        )
        .first()
    )

    if kien_hang is None:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy kiện hàng"
        )

    try:

        # Chỉ lấy những dữ liệu được gửi lên
        du_lieu = data.model_dump(
            exclude_unset=True
        )

        # Cập nhật động
        for ten_truong, gia_tri in du_lieu.items():

            setattr(
                kien_hang,
                ten_truong,
                gia_tri
            )

        db.commit()
        db.refresh(kien_hang)

        return kien_hang

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi cập nhật kiện hàng: {str(e)}"
        )


# ==================================================
# 4. XÓA VẬN ĐƠN
# DELETE /waybills/{waybill_id}
# ==================================================

@app.delete(
    "/waybills/{waybill_id}"
)
def xoa_van_don(
    waybill_id: int,
    db: Session = Depends(get_db)
):

    van_don = (
        db.query(Waybill)
        .filter(
            Waybill.id == waybill_id
        )
        .first()
    )

    if van_don is None:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy vận đơn"
        )

    try:

        db.delete(van_don)
        db.commit()

        return {
            "message": "Xóa vận đơn thành công",
            "waybill_id": waybill_id
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xóa vận đơn: {str(e)}"
        )