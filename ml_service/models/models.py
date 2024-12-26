from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean

metadata = MetaData()




users = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
    Column("subscription_end", TIMESTAMP, nullable=True),
    Column("payment_id", String, nullable=True),
    Column("payment_auto", Boolean, default=False),
    Column("payment_confirmation", Boolean, default=False),
    Column("payment_method_id", String, default=False),
)

sessions = Table(
    "sessions",
    metadata,
    Column("session_id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(users.c.id)),
    Column("time1", String, nullable=True),
    Column("site1", String, nullable=True),
    Column("time2", String, nullable=True),
    Column("site2", String, nullable=True),
    Column("time3", String, nullable=True),
    Column("site3", String, nullable=True),
    Column("time4", String, nullable=True),
    Column("site4", String, nullable=True),
    Column("time5", String, nullable=True),
    Column("site5", String, nullable=True),
    Column("time6", String, nullable=True),
    Column("site6", String, nullable=True),
    Column("time7", String, nullable=True),
    Column("site7", String, nullable=True),
    Column("time8", String, nullable=True),
    Column("site8", String, nullable=True),
    Column("time9", String, nullable=True),
    Column("site9", String, nullable=True),
    Column("time10", String, nullable=True),
    Column("site10", String, nullable=True),
    Column("email", String, nullable=True),
    Column("target", Integer, nullable=True),
    Column("confirmation", Boolean, nullable=True),
    Column("date", TIMESTAMP, default=datetime.utcnow, nullable=True),
)


start_sessions = Table(
    "start_sessions",
    metadata,
    Column("session_id", Integer, primary_key=True),
    Column("site1", String, nullable=True),
    Column("time1", String, nullable=True),
    Column("site2", String, nullable=True),
    Column("time2", String, nullable=True),
    Column("site3", String, nullable=True),
    Column("time3", String, nullable=True),
    Column("site4", String, nullable=True),
    Column("time4", String, nullable=True),
    Column("site5", String, nullable=True),
    Column("time5", String, nullable=True),
    Column("site6", String, nullable=True),
    Column("time6", String, nullable=True),
    Column("site7", String, nullable=True),
    Column("time7", String, nullable=True),
    Column("site8", String, nullable=True),
    Column("time8", String, nullable=True),
    Column("site9", String, nullable=True),
    Column("time9", String, nullable=True),
    Column("site10", String, nullable=True),
    Column("time10", String, nullable=True),
    Column("target", Integer, nullable=True),
)