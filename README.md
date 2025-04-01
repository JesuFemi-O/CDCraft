# CDCraft - Postgresql CDC Simulation Engine

Simulate real-world Change Data Capture (CDC) activity on a PostgreSQL table with evolving schema, inserts, updates, and deletes. This tool is perfect for testing streaming pipelines, Debezium connectors, or building end-to-end CDC systems.

---

## 🚀 Features

- ✅ Generate and insert realistic fake records into a PostgreSQL table
- 🔁 Randomly update and delete existing rows
- 📦 Optionally evolve schema over time (add/drop columns)
- 🧾 Interactive setup for schema, table, publication, and replication slot
- 🔒 Option to disable schema evolution and focus purely on inserts, updates, and deletes
- 💥 Graceful `Ctrl+C` handling with final summary and cleanup prompt

---

## 📂 Project Structure

```
.
├── README.md
├── pyproject.toml
├── uv.lock
└── src
    ├── batch_generator.py
    ├── cli.py
    ├── column_manager.py
    ├── column_pool.py
    ├── main.py
    ├── mutation_engine.py
    ├── prompt_utils.py
    ├── runner.py
    └── schema_manager.py
```

---

## 🔧 Setup with `uv`

This project uses [`uv`](https://github.com/astral-sh/uv) — a fast, modern Python package manager.

### ✅ 1. Install `uv`

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Or with Homebrew:

```bash
brew install astral-sh/uv/uv
```

### ✅ 2. Install dependencies and activate the virtual environment

```bash
uv venv              # Creates a .venv folder
source .venv/bin/activate

uv pip install -r uv.lock   # Install locked dependencies
```

### ✅ 3. Run the simulation

```bash
python src/main.py
```

---

## ⚙️ Configuration Options

You can use environment variables or a `.env` file to customize behavior.

| Env Var             | Description                                      | Default      |
|---------------------|--------------------------------------------------|--------------|
| `PGHOST`            | Hostname for PostgreSQL                         | `localhost`  |
| `PGDATABASE`        | PostgreSQL database name                        | `cdc_test`   |
| `PGUSER`            | PostgreSQL user                                 | `postgres`   |
| `PGPASSWORD`        | PostgreSQL password                             | `postgres`   |
| `PGPORT`            | PostgreSQL port                                 | `5432`       |
| `PGSCHEMA`          | Schema name to use                              | `public`     |
| `SKIP_SETUP`        | If `true`, skips interactive setup              | `false`      |
| `ENABLE_EVOLUTION`  | If `false`, disables schema evolution           | `true`       |

---

## 🧪 Example: CDC with static schema

To simulate just inserts, updates, and deletes without schema changes:

```bash
ENABLE_EVOLUTION=false python src/main.py
```

---

## 📊 Output Example

```
🚀 Starting CDC Simulation: 1000000 records in 2000 batches
📦 [Batch 25] Added column 'promo_code'
🗑️ [Batch 50] Dropped column 'discount_rate'
[Batch 100] Inserts: 50000, Updates: 25000, Deletes: 23000

📊 CDC Simulation Complete!
Original Schema:
 - id: UUID
 - customer_name: TEXT
...

Schema Changes:
 - ADD: promo_code
 - DROP: discount_rate

Final Schema:
 - id: UUID
 - customer_name: TEXT
...

Schema Evolution Summary:
 - Additions: 3
 - Drops: 2
```

---

## 🔄 Future Enhancements

- CLI support with argparse
- JSONL export for batch snapshots
- Integration with Kafka or S3
- Multi-table simulation

---

## 🤝 Contributing

Built with ❤️ by Emmanuel Ogunwede.
Open to ideas, contributions, and improvements!

