# Runbook: Orders Database Failover

This runbook covers the orders database, its primary and its replica `db-03`, owned by the database team.

## When to use it

Use this runbook when the orders database primary stops responding, or when replication lag on the replica `db-03` exceeds 15 minutes and keeps growing.

## Check first

1. Confirm the alert: run the health check from the database dashboard. Two consecutive failed checks, one minute apart, confirm that the primary is down.
2. Check replication lag on `db-03`. Failing over to a replica that is far behind loses recent orders.

## Fail over

1. Page the on-call database engineer if you are not them.
2. Stop writes: put the order service into maintenance mode from the platform console.
3. Promote the replica: run the promotion job `promote-replica db-03` from the database automation tool.
4. Update the connection string in the secret manager, then restart the order service.
5. Take the order service out of maintenance mode, and watch error rates for 15 minutes.

## Afterwards

Open a P2 follow-up ticket to build a new replica. The cluster has no replica until it is rebuilt, so a second failure would cause an outage. Record the failover in the incident timeline.
