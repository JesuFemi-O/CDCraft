from typing import Dict, Any, Optional, Sequence, Union, Set
from pydantic import BaseModel
import psycopg2
import os
from psycopg2.extensions import cursor, connection as ConnectionExt
from psycopg2.extras import LogicalReplicationConnection, ReplicationCursor


class DBCredential(BaseModel):
    database: str
    username: str
    password: str
    host: str
    port: int = 5432

def _get_conn(creds: DBCredential, connection_factory: Optional[Any] = None) -> ConnectionExt:
    """Returns a psycopg2 connection with an optional factory for replication support."""
    return psycopg2.connect(
        database=creds.database,
        user=creds.username,
        password=creds.password,
        host=creds.host,
        port=creds.port,
        connection_factory=connection_factory,
    )
    
def _get_rep_conn( creds: DBCredential) -> LogicalReplicationConnection:
    """Returns a LogicalReplicationConnection for PostgreSQL logical replication."""
    return _get_conn(creds, LogicalReplicationConnection)


def create_replication_slot(name: str, cur: ReplicationCursor, output_plugin: str = "pgoutput") -> Optional[Dict[str, str]]:
    """Creates a replication slot if it doesn't exist yet."""
    try:
        cur.create_replication_slot(name, output_plugin=output_plugin)
        print(f'Successfully created replication slot "{name}".')
        result = cur.fetchone()
        return {
            "slot_name": result[0],
            "consistent_point": result[1],
            "snapshot_name": result[2],
            "output_plugin": result[3],
        }
    except psycopg2.errors.DuplicateObject:  # the replication slot already exists
        print(
            f'Replication slot "{name}" cannot be created because it already exists.'
        )


if __name__ == "__main__":
    creds = DBCredential(
        database=os.getenv("PGDATABASE", "postgres"),
        username=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
        host=os.getenv("PGHOST", "localhost"),
    )

    rep_conn = _get_rep_conn(creds)

    slot = create_replication_slot(
        name="test_slot",
        cur=rep_conn.cursor(),
        output_plugin="pgoutput"
    )
    print(slot)