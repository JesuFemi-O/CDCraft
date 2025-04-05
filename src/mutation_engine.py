import random
from typing import List, Dict, Tuple
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from batch_generator import BatchGenerator


class MutationEngine:
    def __init__(self, conn, schema="public", table_name="sales"):
        self.conn = conn
        self.schema = schema
        self.table_name = table_name
        self.total_inserts = 0
        self.total_updates = 0
        self.total_deletes = 0


    def insert_batch(self, rows: List[Dict]) -> List[str]:
        if not rows:
            return []
        

        # keep track of the inserted IDs for possible mutations
        inserted_ids = [row["id"] for row in rows]
        self.total_inserts += len(rows)

        with self.conn.cursor() as cur:
            # Generate the SQL insert statement
            columns = rows[0].keys()
            query = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(
                sql.Identifier(self.schema),
                sql.Identifier(self.table_name),
                sql.SQL(", ").join(map(sql.Identifier, columns))
            )
            values = [[row[col] for col in columns] for row in rows]
            execute_values(cur, query, values)
            self.conn.commit()
        
        return inserted_ids
    

    def maybe_mutate_batch(
        self, generator: BatchGenerator, inserted_ids: List[str]
    ) -> Tuple[int, int]:
        if not inserted_ids or random.choice([True, False]) is False:
            return 0, 0  # skip mutation
        
        mutation_type = random.choice(["update", "delete"])
        num_to_change = random.randint(1, max(1, len(inserted_ids) // 2))
        chosen_ids = random.sample(inserted_ids, num_to_change)

        if mutation_type == "update":
            updated_count = self._update_records(generator, chosen_ids)
            self.total_updates += updated_count
            return updated_count, 0
        else:
            deleted_count = self._delete_records(chosen_ids)
            self.total_deletes += deleted_count
            return 0, deleted_count
    
    def _update_records(self, generator: BatchGenerator, ids: List[str]) -> int:
        modifiable_columns = [col for col in generator.schema if col not in ("id", "created_at", "updated_at")]

        with self.conn.cursor() as cur:
            for row_id in ids:
                col = random.choice(modifiable_columns)
                val = generator._generate_value(col)
                query = sql.SQL("UPDATE {}.{} SET {} = %s, updated_at = now() WHERE id = %s").format(
                    sql.Identifier(self.schema),
                    sql.Identifier(self.table_name),
                    sql.Identifier(col)
                )
                cur.execute(query, (val, row_id))
            self.conn.commit()

        return len(ids)
    
    def _delete_records(self, ids: List[str]) -> int:
        with self.conn.cursor() as cur:
            query = sql.SQL("DELETE FROM {}.{} WHERE id = ANY(%s::uuid[])").format(
                sql.Identifier(self.schema),
                sql.Identifier(self.table_name)
            )
            cur.execute(query, (ids,))
            self.conn.commit()

        return len(ids)

    def get_counters(self) -> Dict[str, int]:
        return {
            "total_inserts": self.total_inserts,
            "total_updates": self.total_updates,
            "total_deletes": self.total_deletes,
        }