from datetime import datetime
from modules.database import Base, SerializerMixin
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column


class Relative_Users(Base, SerializerMixin):
    __table_args__ = {"comment": "通知人员表"}
    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True, comment="主键ID"
    )
    userid: Mapped[str] = mapped_column(String(255), comment="通知人员企业微信id")
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, comment="创建时间", default=datetime.now()
    )
