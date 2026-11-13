# Runbook: Nightly Backup Failures

The database team owns the nightly backups, which are written to the backup store `db-backup`.

## Symptoms

The backup job reports a failure, or the morning report shows no backup for one or more databases.

## Diagnose

1. Read the job log. The most common error is `disk quota exceeded` on the backup store.
2. Check how many nights in a row the backup has failed. One failure is a P3; three failures in a row are a P2, because the most recent recovery point is then more than three days old.

## Fix

- For `disk quota exceeded`, delete backups older than the retention period (35 days) with the retention job, never by hand, then run the backup again.
- For timeouts, check whether the database has grown unusually, and schedule the backup earlier.

After any fix, run a restore test of the latest backup into the staging environment. A backup that has never been restored is not a backup.
