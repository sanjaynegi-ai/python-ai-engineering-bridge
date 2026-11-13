# Runbook: Disk Space Alerts

The platform team owns the application servers. Every server reports its disk usage to the monitoring system once a minute.

## Thresholds

- **Warning** at 85 percent used: a P3 ticket for the owning team.
- **Critical** at 95 percent used: a P2, and the platform on-call engineer is paged. A full disk stops applications from writing logs and temporary files, and many of them crash.

## Diagnose

1. Find what grew. The disk usage dashboard shows the largest folders and how they changed over the last 24 hours.
2. The usual causes are application logs that are not rotated, core dumps after a crash, and temporary export files that a job forgot to delete.

## Free space safely

- Compress or delete old application logs with the log rotation job, not by hand.
- Move core dumps to the analysis share before deleting them, so that the crash can still be investigated.
- Never delete database files, even when a database server's disk is full. Page the on-call database engineer instead.

## Afterwards

If the same server alerts twice in one month, open a ticket to fix the cause, for example a missing log rotation rule. Adding disk space only hides the problem.
