# Postmortem: Internal DNS Overload, June 2026

## Summary

For 1 hour and 20 minutes, internal tools were slow or unusable at every office, because the internal DNS resolvers `dns-int` were overloaded. External websites kept working. The incident was a P2.

## Timeline

- 14:05: support tickets report that the operations portal takes a minute to load.
- 14:20: the network on-call engineer finds that queries to the resolvers have risen tenfold.
- 14:45: the queries are traced to a new version of the inventory sync service, which retried every failed lookup immediately, in a loop.
- 15:10: the resolvers rate-limit the inventory sync service, and lookups recover.
- 15:25: the inventory team rolls back the service, and the incident is resolved.

## Causes

The new version had no delay between retries, and no limit on their number. One unreachable hostname made each of its 40 instances send thousands of lookups per second.

## Actions

- Add retries with backoff and a retry limit to the inventory sync service.
- Add an alert when one client sends more than 10 percent of all DNS queries.
- Add per-client rate limits to the resolvers by default.
