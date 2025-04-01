import psycopg2
from psycopg2 import sql
from batch_generator import BatchGenerator
from prompt_utils import prompt_yes_no


def run_initial_setup(
    schema_mgr,
    mutator,
    snapshot_batch_size,
    replica_identity,
    publication_name,
    replication_slot,
    conn
) -> dict:
    print("\n🛠️  Starting Interactive Setup...\n")

    original_schema = {}

    if prompt_yes_no(f"1️⃣ Create table '{schema_mgr.schema}.{schema_mgr.table_name}'?"):
        with conn.cursor() as cur:
            cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(
                sql.Identifier(schema_mgr.schema)
            ))
            conn.commit()
        print(f"✅ Schema '{schema_mgr.schema}' ensured.")

        schema_mgr.initialize_table()
        print("✅ Table created.")
        original_schema = schema_mgr.get_active_column_definitions()

        if replica_identity and prompt_yes_no("🔁 Set REPLICA IDENTITY FULL?"):
            with conn.cursor() as cur:
                cur.execute(sql.SQL("ALTER TABLE {}.{} REPLICA IDENTITY FULL;").format(
                    sql.Identifier(schema_mgr.schema),
                    sql.Identifier(schema_mgr.table_name)
                ))
                conn.commit()
            print("✅ Replica identity set to FULL.")

    if prompt_yes_no(f"📦 Perform snapshot load (initial {snapshot_batch_size} rows)?"):
        generator = BatchGenerator(schema_mgr.get_active_column_definitions())
        rows = generator.generate_batch(snapshot_batch_size)
        mutator.insert_batch(rows)
        print(f"✅ Inserted {snapshot_batch_size} rows for snapshotting.")

    if prompt_yes_no(f"📣 Create publication '{publication_name}' for table '{schema_mgr.schema}.{schema_mgr.table_name}'?"):
        with conn.cursor() as cur:
            cur.execute(sql.SQL("CREATE PUBLICATION {} FOR TABLE {}.{};").format(
                sql.Identifier(publication_name),
                sql.Identifier(schema_mgr.schema),
                sql.Identifier(schema_mgr.table_name)
            ))
            conn.commit()
        print(f"✅ Publication '{publication_name}' created.")

    if prompt_yes_no(f"🛰️ Create replication slot '{replication_slot}'?"):
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT * FROM pg_create_logical_replication_slot(%s, 'pgoutput');"),
                (replication_slot,)
            )
            result = cur.fetchone()
            print(f"✅ Replication slot created: {result}")
            conn.commit()

    print("\n🧾 Setup Summary:")
    print(f" - Table: {schema_mgr.schema}.{schema_mgr.table_name}")
    if replica_identity:
        print(" - Replica Identity: FULL")
    print(f" - Publication: {publication_name}")
    print(f" - Replication Slot: {replication_slot}\n")

    return original_schema


def run_cdc_simulation(schema_mgr, mutator, schema_evolver, total_records, batch_size, enable_evolution=True):
    generator = BatchGenerator(schema_mgr.get_active_column_definitions())
    total_batches = total_records // batch_size

    print(f"\n🚀 Starting CDC Simulation: {total_records} records in {total_batches} batches\n")

    for batch_no in range(1, total_batches + 1):
        batch = generator.generate_batch(batch_size)
        inserted_ids = mutator.insert_batch(batch)
        mutator.maybe_mutate_batch(generator, inserted_ids)

        if enable_evolution and schema_evolver.should_evolve(batch_no):
            action = schema_evolver.choose_action()
            if action == "add":
                added = schema_mgr.add_random_column()
                if added:
                    schema_evolver.record_action("add")
                    print(f"📦 [Batch {batch_no}] Added column '{added}'")
                    generator.update_schema(schema_mgr.get_active_column_definitions())
            elif action == "drop":
                dropped = schema_mgr.drop_random_column()
                if dropped:
                    schema_evolver.record_action("drop")
                    print(f"🗑️ [Batch {batch_no}] Dropped column '{dropped}'")
                    generator.update_schema(schema_mgr.get_active_column_definitions())

        if batch_no == 1 and not enable_evolution:
            print("🔒 Schema evolution disabled. Only inserts, updates, and deletes will be simulated.")

        if batch_no % 10 == 0:
            counts = mutator.get_counters()
            print(
                f"[Batch {batch_no}] Inserts: {counts['total_inserts']}, "
                f"Updates: {counts['total_updates']}, Deletes: {counts['total_deletes']}"
            )