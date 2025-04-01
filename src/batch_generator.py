import random
from typing import Any, Dict, List
from column_manager import ColumnDefinition
from column_pool import BASE_COLUMN_DEFINITIONS, COLUMN_POOL

class BatchGenerator:
    def __init__(self, schema: Dict[str, str]):
        """
        Initialize with a schema mapping of column name to SQL type.
        This assumes schema keys match names in available column definitions.
        """
        self.schema = schema

        # Build a lookup from all known column definitions
        all_columns = BASE_COLUMN_DEFINITIONS + COLUMN_POOL
        self.column_lookup: Dict[str, ColumnDefinition] = {
            col.name: col for col in all_columns
        }

    def update_schema(self, new_schema: Dict[str, str]):
        self.schema = new_schema
    
    def _generate_value(self, column: str) -> Any:
        col_def = self.column_lookup.get(column)
        if not col_def:
            raise ValueError(f"No generator defined for column '{column}'")
        return col_def.generate()

    def generate_batch(self, batch_size: int = 500) -> List[Dict[str, Any]]:
        rows = []
        for _ in range(batch_size):
            row = {
                column: self._generate_value(column)
                for column in self.schema
            }
            rows.append(row)
        return rows