from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Warehouse, Package, Waybill
from schemas import WarehouseCreate, PackageUpdate


# ==================================================
# TẠO NHÀ KHO
# ==================================================

def tao_nha_kho(
    data: WarehouseCreate,
    db: Session
):
    try:
        # Giải nén dữ liệu từ Pydantic
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
# LẤY CHI TIẾT NHÀ KHO
# ==================================================

def lay_chi_tiet_nha_kho(
    warehouse_id: int,
    db: Session
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
# CẬP NHẬT KIỆN HÀNG
# ==================================================

def cap_nhat_kien_hang(
    package_id: int,
    data: PackageUpdate,
    db: Session
):
    # Tìm kiện hàng
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
        # Chỉ lấy những trường được gửi lên
        du_lieu_cap_nhat = data.model_dump(
            exclude_unset=True
        )

        # Cập nhật từng trường
        for ten_truong, gia_tri in du_lieu_cap_nhat.items():
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
# XÓA VẬN ĐƠN
# ==================================================

def xoa_van_don(
    waybill_id: int,
    db: Session
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
        # Xóa vật lý
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