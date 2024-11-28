from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean

metadata = MetaData()

# database models
users = Table(
    "users",
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
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(users.c.id)),
    Column("time1", String, nullable=False),
    Column("site1", String, nullable=False),
    Column("time2", String, nullable=False),
    Column("site2", String, nullable=False),
    Column("time3", String, nullable=False),
    Column("site3", String, nullable=False),
    Column("time4", String, nullable=False),
    Column("site4", String, nullable=False),
    Column("time5", String, nullable=False),
    Column("site5", String, nullable=False),
    Column("time6", String, nullable=False),
    Column("site6", String, nullable=False),
    Column("time7", String, nullable=False),
    Column("site7", String, nullable=False),
    Column("time8", String, nullable=False),
    Column("site8", String, nullable=False),
    Column("time9", String, nullable=False),
    Column("site9", String, nullable=False),
    Column("time10", String, nullable=False),
    Column("site10", String, nullable=False),
)

