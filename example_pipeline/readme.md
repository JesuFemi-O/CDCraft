# Making Sense of pg_replication

This particular source can be overwhelming to dive into. This note is meant to help folks looking to explore dlt as an option for mini batch cdc...

## The snapshot!

When dlt initializes replication for you, it attempts to create a replication slot the helper function used in creating the replication slot returns something like this:

```
{
    'slot_name': 'test_slot', 
    'consistent_point': '0/4625B9F8', 
    'snapshot_name': '00000009-00005077-1', 
    'output_plugin': 'pgoutput'
}
```

while using the init_replication helper, dlt also gives you the option of persisting the snapshot table which is basically a copy of the source table at the point of starting replication, behind the scenes it runs a query like this

```sql
START TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION SNAPSHOT '{slot["snapshot_name"]}';
```

and the snapshot name is retrieved from the metadata dict returned by the slot creation helper function.

This is done to set the snapshot to the snaphost of the newly created replication slot (not yet entirely sure what that means).

after the query above is executed, tables are created in postgres that will contain the snapshot data.

```python
snapshot_tables = [
    (
        table_name,
        persist_snapshot_table(
            snapshot_name=slot["snapshot_name"],
            table_name=table_name,
            schema_name=schema_name,
            cur=cur_snap,
            include_columns=(
                None
                if include_columns is None
                else include_columns.get(table_name)
            ),
        ),
        _get_pk(cur_snap, table_name, schema_name),
    )
    for table_name in table_names
]
```

the `cur_snap` is a cursor from a regular postgres connection object
`snapshot_name` is from the replication slot creation metadata dict

the `persist_snapshot_table` function looks like this:

```python
def persist_snapshot_table(
    snapshot_name: str,
    table_name: str,
    schema_name: str,
    cur: cursor,
    include_columns: Optional[Sequence[str]] = None,
) -> str:
    """Persists exported snapshot table state.

    Reads snapshot table content and copies it into new table.
    """
    col_str = "*"
    if include_columns is not None:
        col_str = ", ".join(map(escape_postgres_identifier, include_columns))
    # make sure to shorten identifier
    naming = NamingConvention(63)
    # name must start with _dlt so we skip this table when replicating
    snapshot_table_name = naming.normalize_table_identifier(
        f"_dlt_{table_name}_s_{snapshot_name}"
    )
    snapshot_qual_name = _make_qualified_table_name(snapshot_table_name, schema_name)
    qual_name = _make_qualified_table_name(table_name, schema_name)
    cur.execute(
        f"""
        CREATE TABLE {snapshot_qual_name} AS SELECT {col_str} FROM {qual_name};
        """
    )
    logger.info(f"Successfully persisted snapshot table state in {snapshot_qual_name}.")
    return snapshot_table_name
```

so basically, we use the snapshot name, original table name and a `_dlt` to create the new table and then data is first of all persisted there.


### Summary

with this tuny dive, now we know that init replication:

- creates the publication adding tables to it to make it ready for CDC usage
- creates the replication slot
- has the ability to create snapshot tables in postgres which persists data in tables we intend to perform CDC against
- can be executed multiple times without an implication

we also get a glimpse into how dlt approaches table snapshots in CDC and a hint at the fact that it may not be advisable to persist snapshot for really large tables


## The replication resource

This is the actual engine powering the log based CDC in dlt.

we start by seeing how it begins

```python
# start where we left off in previous run
start_lsn = dlt.current.resource_state().get("last_commit_lsn", 0)
if flush_slot and start_lsn:
    advance_slot(start_lsn, slot_name, credentials)
```

here we see that dlt first tries to confirm if it has previously been executed and if there's a last_commit_lsn (basically the last point in the wal file it consumed.)

if it finds such an LSN, dlt sends a message to postgres to flush the lsn and advance the slot

Next, dlt tries to see if there are new records in the wal by trying to determine the max_lsn

```python
upto_lsn = get_max_lsn(slot_name, options, credentials)
if upto_lsn is None:
    return
logger.info(
    f"Replicating slot {slot_name} publication {pub_name} from {start_lsn} to {upto_lsn}"
)
```

at his point, dlt continously ingests data until there are no new records to ingest.


```python
while True:
    gen = ItemGenerator(
        credentials=credentials,
        slot_name=slot_name,
        options=options,
        upto_lsn=upto_lsn,
        start_lsn=start_lsn,
        target_batch_size=target_batch_size,
        include_columns=include_columns,
        columns=columns,
    )
    yield from gen
    if gen.generated_all:
        dlt.current.resource_state()["last_commit_lsn"] = gen.last_commit_lsn
        break
    start_lsn = gen.last_commit_lsn
```

### Summary
the replication resource simply connects to the wal file and tries the read off all the logs in a given replication slot


# Getting the example to work

I setup the `secrets.toml` with:

```
[sources.pg_replication.credentials]
drivername = "postgresql"
database = "postgres" 
password = "postgres" 
username = "postgres" 
host = "localhost" 
port = 5432

[destination.filesystem]
bucket_url = "s3://demo/"

[destination.filesystem.credentials]
aws_access_key_id = "minio" 
aws_secret_access_key = "minio123"
endpoint_url="http://localhost:9000/"
```

I setup the `config.toml` as 

```
# put your configuration values here

[runtime]
log_level="WARNING"  # the system log level of dlt
# use the dlthub_telemetry setting to enable/disable anonymous usage data reporting, see https://dlthub.com/docs/reference/telemetry
dlthub_telemetry = true

[normalize]
loader_file_format="parquet"

[normalize.data_writer]
disable_compression=true

```


note that I'm relying on uv so I ran `uv pip install -r requirements.txt` in the `example_pipeline` folder

also note that If I ran into weird envrionment issues I typically ran `uv add <package_name>` for example `uv add "dlt[sql_database]"` so that everything is resolved by UV.


to execute the code I ran:

```
uv run main.py           
```

a common gotcha here is that you need a docker-compose service with your postgres instance and minio running.

also rememeber to add `secrets.toml` to your `.dlt` folder since its in the `.gitignore`, clonning this repo will not suffice

Happy hacking!