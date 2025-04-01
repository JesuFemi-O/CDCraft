from typing import Any, Callable, Optional

class ColumnDefinition:
    """
    Class to define the properties of a column in a dataset.
    """

    def __init__(
        self, name: str, 
        sql_type: str, 
        generator: Callable[[], Any],
        constraints: Optional[str] = None  # e.g., "PRIMARY KEY NOT NULL"
        ):
        self.name = name
        self.sql_type = sql_type
        self.generator = generator
        self.constraints = constraints or ""

    def generate(self) -> Any:
        return self.generator()

    def ddl(self) -> str:
        """
        Generate DDL fragment for this column.
        """
        return f"{self.name} {self.sql_type} {self.constraints}".strip()