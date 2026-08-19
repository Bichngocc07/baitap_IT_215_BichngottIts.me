from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import (
    Warehouse,
    Package,
    Waybill
)

from schemas import (
    WarehouseCreate,
    PackageUpdate
)


# ==========================================
# CREATE WAREHOUSE
# ==========================================

def create_warehouse(
    data: WarehouseCreate,
    db: Session
):

    try:

        warehouse = Warehouse(
            **data.model_dump()
        )

        db.add(warehouse)

        db.commit()

        db.refresh(warehouse)

        return warehouse

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tạo nhà kho: {str(e)}"
        )


# ==========================================
# GET WAREHOUSE DETAIL
# ==========================================

def get_warehouse_detail(
    warehouse_id: int,
    db: Session
):

    warehouse = (
        db.query(Warehouse)
        .filter(
            Warehouse.id == warehouse_id
        )
        .first()
    )

    if warehouse is None:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà kho"
        )

    return warehouse


# ==========================================
# UPDATE PACKAGE
# ==========================================

def update_package(
    package_id: int,
    data: PackageUpdate,
    db: Session
):

    package = (
        db.query(Package)
        .filter(
            Package.id == package_id
        )
        .first()
    )

    if package is None:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy kiện hàng"
        )

    try:

        # Chỉ lấy những field được gửi lên
        update_data = data.model_dump(
            exclude_unset=True
        )

        # Cập nhật động
        for key, value in update_data.items():

            setattr(
                package,
                key,
                value
            )

        db.commit()

        db.refresh(package)

        return package

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi cập nhật kiện hàng: {str(e)}"
        )


# ==========================================
# DELETE WAYBILL
# ==========================================

def delete_waybill(
    waybill_id: int,
    db: Session
):

    waybill = (
        db.query(Waybill)
        .filter(
            Waybill.id == waybill_id
        )
        .first()
    )

    if waybill is None:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy vận đơn"
        )

    try:

        db.delete(waybill)

        db.commit()

        return {
            "message": "Xóa vận đơn thành công",
            "waybill_id": waybill_id
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xóa vận đơn: {str(e)}"
        )