import psycopg2
from psycopg2 import sql
import random
from typing import List, Dict, Optional
from column_manager import ColumnDefinition
from column_pool import BASE_COLUMN_DEFINITIONS, COLUMN_POOL, PROTECTED_COLUMNS

class SchemaManager:
    def __init__(self, conn, schema="public", table_name="sales"):
        self.conn = conn
        self.schema = schema
        self.table_name = table_name

        self.base_column_defs: List[ColumnDefinition] = BASE_COLUMN_DEFINITIONS
        self.column_pool: List[ColumnDefinition] = COLUMN_POOL.copy()
        random.shuffle(self.column_pool) # Shuffle the column pool for randomness

        # Active column definitions (dict of name: ColumnDefinition)
        self.active_columns: Dict[str, ColumnDefinition] = {
            col.name: col for col in self.base_column_defs
        }

        # History of schema changes
        self.schema_history: List[Dict[str, Optional[str]]] = []
    
    def initialize_table(self):
        with self.conn.cursor() as cur:
            cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
            columns_ddl = ",\n".join(
                col.ddl() for col in self.base_column_defs
            )
            ddl = sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} (\n{}\n);").format(
                sql.Identifier(self.schema),
                sql.Identifier(self.table_name),
                sql.SQL(columns_ddl)
            )
            cur.execute(ddl)
            self.conn.commit()
    
    def get_current_columns(self) -> List[str]:
        return list(self.active_columns.keys())
    
    def add_random_column(self) -> Optional[str]:
        if not self.column_pool:
            return None

        col_def = self.column_pool.pop(0)

        alter_stmt = sql.SQL("ALTER TABLE {}.{} ADD COLUMN {} {} {}").format(
            sql.Identifier(self.schema),
            sql.Identifier(self.table_name),
            sql.Identifier(col_def.name),
            sql.SQL(col_def.sql_type),
            sql.SQL(col_def.constraints or "")
        )

        with self.conn.cursor() as cur:
            cur.execute(alter_stmt)
            self.conn.commit()

        self.active_columns[col_def.name] = col_def
        self.schema_history.append({"action": "add", "column": col_def.name})
        return col_def.name
    
    def drop_random_column(self) -> Optional[str]:
        candidate_columns = [
            name for name in self.active_columns
            if name not in PROTECTED_COLUMNS 
        ]
        if not candidate_columns:
            return None

        random.shuffle(candidate_columns)
        col_name = candidate_columns[0]

        alter_stmt = sql.SQL("ALTER TABLE {}.{} DROP COLUMN {}").format(
            sql.Identifier(self.schema),
            sql.Identifier(self.table_name),
            sql.Identifier(col_name),
        )

        with self.conn.cursor() as cur:
            cur.execute(alter_stmt)
            self.conn.commit()

        self.active_columns.pop(col_name)
        self.schema_history.append({"action": "drop", "column": col_name})
        return col_name
    
    def get_schema_history(self) -> List[Dict[str, str]]:
        return self.schema_history

    def get_active_column_definitions(self) -> Dict[str, str]:
        return {name: col_def.sql_type for name, col_def in self.active_columns.items()}
    

class SchemaEvolutionController:
    def __init__(
        self,
        evolution_interval: int = 25,
        evolution_probability: float = 0.2, # 20% chance of evolution
        add_probability: float = 0.7, # 70% chance of adding a column, 30% of dropping
        max_additions: int = 7,
        max_drops: int = 3
    ):
        self.evolution_interval = evolution_interval
        self.evolution_probability = evolution_probability
        self.add_probability = add_probability
        self.max_additions = max_additions
        self.max_drops = max_drops

        self.num_additions = 0
        self.num_drops = 0
    
    def should_evolve(self, batch_number: int) -> bool:
        if batch_number % self.evolution_interval != 0:
            return False
        return random.random() < self.evolution_probability
    
    def choose_action(self) -> str:
        can_add = self.num_additions < self.max_additions
        can_drop = self.num_drops < self.max_drops

        if not can_add and not can_drop:
            return "none"
        if can_add and not can_drop:
            return "add"
        if not can_add and can_drop:
            return "drop"

        # If both are possible, choose probabilistically
        return "add" if random.random() <= self.add_probability else "drop"
    
    def record_action(self, action: str):
        if action == "add":
            self.num_additions += 1
        elif action == "drop":
            self.num_drops += 1
    
    def summary(self):
        return {
            "total_adds": self.num_additions,
            "total_drops": self.num_drops,
            "max_adds": self.max_additions,
            "max_drops": self.max_drops
        }