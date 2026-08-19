from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)

from sqlalchemy.orm import relationship

from database import Base


# ==========================================
# WAREHOUSE
# ==========================================

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

    # 1 Warehouse - N Package
    packages = relationship(
        "Package",
        back_populates="warehouse"
    )


# ==========================================
# PACKAGE
# ==========================================

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

    # Package thuộc 1 Warehouse
    warehouse = relationship(
        "Warehouse",
        back_populates="packages"
    )

    # 1 Package - 1 Waybill
    waybill = relationship(
        "Waybill",
        back_populates="package",
        uselist=False
    )


# ==========================================
# WAYBILL
# ==========================================

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

    # Waybill thuộc 1 Package
    package = relationship(
        "Package",
        back_populates="waybill"
    )