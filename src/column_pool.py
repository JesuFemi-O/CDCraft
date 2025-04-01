from datetime import datetime, timedelta
import random
import string
import uuid
from column_manager import ColumnDefinition
from faker import Faker

fake = Faker()

# Helper generators
def random_string(n=8):
    return ''.join(random.choices(string.ascii_lowercase, k=n))

def random_float():
    return round(random.uniform(10, 1000), 2)

def random_bool():
    return random.choice([True, False])

def random_timestamp():
    return datetime.utcnow() - timedelta(days=random.randint(0, 1000))

# Pre-defined column pool (we'll track which ones were used)
COLUMN_POOL = [
    ColumnDefinition("promo_code", "text", lambda: random_string(5).upper()),
    ColumnDefinition("discount_rate", "float", random_float),
    ColumnDefinition("is_gift", "boolean", random_bool),
    ColumnDefinition("created_at", "timestamp", random_timestamp),
    ColumnDefinition("sales_channel", "text", lambda: random.choice(["web", "mobile", "store"])),
    ColumnDefinition("region", "text", lambda: random.choice(["NA", "EU", "APAC"])),
]


BASE_COLUMN_DEFINITIONS = [
    ColumnDefinition("id", "UUID", lambda: str(uuid.uuid4()), constraints="PRIMARY KEY DEFAULT uuid_generate_v4()"),
    ColumnDefinition("customer_name", "TEXT", fake.name, constraints="NOT NULL"),
    ColumnDefinition("item_id", "INTEGER", lambda: random.randint(1, 10000), constraints="NOT NULL"),
    ColumnDefinition("quantity", "INTEGER", lambda: random.randint(1, 10), constraints="NOT NULL"),
    ColumnDefinition("total_amount", "FLOAT", lambda: round(random.uniform(5.0, 10000.0), 2), constraints="NOT NULL"),
    ColumnDefinition("purchased_at", "TIMESTAMP WITHOUT TIME ZONE", lambda: fake.date_time_between(start_date='-2y', end_date='now'), constraints="NOT NULL"),
]