import os
import sys
import psycopg2
from schema_manager import SchemaManager, SchemaEvolutionController
from mutation_engine import MutationEngine
from prompt_utils import prompt_yes_no
from runner import run_initial_setup, run_cdc_simulation
from cli import handle_interrupt, print_final_report

# ────────── CONFIG ────────── #
TOTAL_RECORDS = 1_000_000
BATCH_SIZE = 500
SNAPSHOT_BATCH_SIZE = 1000
TABLE_NAME = "sales"
SCHEMA_NAME = os.getenv("PGSCHEMA", "internal_demo")
SKIP_SETUP = os.getenv("SKIP_SETUP", "false").lower() == "true"
ENABLE_EVOLUTION = os.getenv("ENABLE_EVOLUTION", "true").lower() == "true"
REPLICA_IDENTITY = True
PUBLICATION_NAME = f"{TABLE_NAME}_pub"
REPLICATION_SLOT = f"{TABLE_NAME}_slot"

# ────────── SETUP CONNECTION ────────── #
conn = psycopg2.connect(
    host=os.getenv("PGHOST", "localhost"),
    dbname=os.getenv("PGDATABASE", "postgres"),
    user=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD", "postgres"),
    port=int(os.getenv("PGPORT", "5432")),
)

schema_mgr = SchemaManager(conn, schema=SCHEMA_NAME, table_name=TABLE_NAME)
mutator = MutationEngine(conn, schema=SCHEMA_NAME, table_name=TABLE_NAME)

SCHEMA_EVOLVER = SchemaEvolutionController(
    evolution_interval=25,
    evolution_probability=0.2,
    add_probability=0.7,
    max_additions=7,
    max_drops=3,
)

original_schema = {}

if __name__ == "__main__":
    try:
        if not SKIP_SETUP:
            original_schema = run_initial_setup(
                schema_mgr=schema_mgr,
                mutator=mutator,
                snapshot_batch_size=SNAPSHOT_BATCH_SIZE,
                replica_identity=REPLICA_IDENTITY,
                publication_name=PUBLICATION_NAME,
                replication_slot=REPLICATION_SLOT,
                conn=conn
            )

            if not prompt_yes_no("▶️  Start CDC simulation now?"):
                print("👋 Exiting without running simulation.")
                conn.close()
                sys.exit(0)

        run_cdc_simulation(
            schema_mgr=schema_mgr,
            mutator=mutator,
            schema_evolver=SCHEMA_EVOLVER,
            total_records=TOTAL_RECORDS,
            batch_size=BATCH_SIZE,
            enable_evolution=ENABLE_EVOLUTION
        )

        print_final_report(schema_mgr, mutator, SCHEMA_EVOLVER, original_schema)

    except KeyboardInterrupt:
        handle_interrupt(schema_mgr, mutator, SCHEMA_EVOLVER, original_schema, conn)

    finally:
        conn.close()
