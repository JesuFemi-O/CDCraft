from prompt_utils import prompt_yes_no

def handle_interrupt(schema_mgr, mutator, SCHEMA_EVOLVER, original_schema, conn):
    print("\n\U0001F6D1 Simulation interrupted!")
    print_final_report(schema_mgr, mutator, SCHEMA_EVOLVER, original_schema)

    if prompt_yes_no(f"\n\u26A0\uFE0F  Drop table '{schema_mgr.schema}.{schema_mgr.table_name}'?", default=False):
        from psycopg2 import sql
        with conn.cursor() as cur:
            cur.execute(sql.SQL("DROP TABLE IF EXISTS {}.{}").format(
                sql.Identifier(schema_mgr.schema),
                sql.Identifier(schema_mgr.table_name)
            ))
            conn.commit()
        print("\U0001F9F9 Table dropped.")
    conn.close()


def print_final_report(schema_mgr, mutator, SCHEMA_EVOLVER, original_schema):
    print("\n\U0001F4CA CDC Simulation Complete!\n")
    print("Totals:")
    print(mutator.get_counters())

    print("\nOriginal Schema:")
    for col, dtype in original_schema.items():
        print(f" - {col}: {dtype}")

    print("\nSchema Changes:")
    for entry in schema_mgr.get_schema_history():
        print(f" - {entry['action'].upper()}: {entry['column']}")

    print("\nFinal Schema:")
    for col, dtype in schema_mgr.get_active_column_definitions().items():
        print(f" - {col}: {dtype}")

    print("\nSchema Evolution Summary:")
    print(SCHEMA_EVOLVER.summary())