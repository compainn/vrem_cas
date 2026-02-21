from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Float, String, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0)

    total_deposited: Mapped[float] = mapped_column(Float, default=0.0)
    total_withdrawn: Mapped[float] = mapped_column(Float, default=0.0)
    total_wagered: Mapped[float] = mapped_column(Float, default=0.0)
    games_played: Mapped[int] = mapped_column(default=0)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    hide_username: Mapped[bool] = mapped_column(Boolean, default=False)

    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    referral_balance: Mapped[float] = mapped_column(Float, default=0.0)
    referrals_count: Mapped[int] = mapped_column(Integer, default=0)


class Invoice(Base):
    __tablename__ = 'invoices'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    invoice_id: Mapped[str] = mapped_column(String(100))
    pay_url: Mapped[str] = mapped_column(String(500))
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class CheckRecord(Base):
    __tablename__ = 'checks'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    check_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    check_url: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
