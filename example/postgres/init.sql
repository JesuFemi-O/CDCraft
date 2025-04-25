-- Allow replication and logical decoding
ALTER SYSTEM SET wal_level = logical;

-- Reload configuration
SELECT pg_reload_conf();