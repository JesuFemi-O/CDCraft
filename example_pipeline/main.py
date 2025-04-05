import dlt

from dlt.common.destination import Destination
from dlt.destinations.impl.postgres.configuration import PostgresCredentials

from pg_replication import replication_resource
from pg_replication.helpers import init_replication

slot_name = "sales_slot"
pub_name = "sales_pub"

changes = replication_resource(slot_name, pub_name)

dest_pl = dlt.pipeline(
    pipeline_name="pg_replication_pipeline_v2",
    destination='filesystem',
    dataset_name="replicate_single_table",
    dev_mode=True,
    progress="log"
)


load_info = dest_pl.run(changes)

print(load_info)

print(dest_pl.last_trace.last_normalize_info)