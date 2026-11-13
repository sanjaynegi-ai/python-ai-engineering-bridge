# Runbook: Slow or Failing Internal DNS

The network team runs the internal DNS resolvers, `dns-int`.

## Symptoms

Internal tools feel slow or broken, but external websites work. Name lookups for internal hostnames take several seconds, or time out.

## Diagnose

1. Measure lookup time from two different offices. If only one office is slow, the problem is probably that office's network, not DNS.
2. Check the resolver dashboard for query volume. A sudden spike often comes from a misconfigured service retrying lookups in a loop.
3. Check the resolvers' upstream forwarders. If they are unreachable, resolution of external names fails too.

## Mitigate

- If one service is flooding the resolvers, rate-limit it at the resolver and contact its owning team.
- If a resolver is unhealthy, remove it from the pool; clients fall back to the remaining resolvers within a minute.
- Do not lower DNS cache times during an incident: it increases the load on the resolvers.
