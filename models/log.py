from datetime import datetime
from modules.database import Base
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column


class Log(Base):
    __table_args__ = {"comment": "温湿度数据表"}
    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True, comment="主键ID"
    )
    location: Mapped[str] = mapped_column(String(255), comment="数据所属传感器位置")
    temperature: Mapped[float] = mapped_column(Float, nullable=False, comment="温度")
    humidity: Mapped[float] = mapped_column(Float, nullable=False, comment="湿度")

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, comment="创建时间", default=datetime.now()
    )
