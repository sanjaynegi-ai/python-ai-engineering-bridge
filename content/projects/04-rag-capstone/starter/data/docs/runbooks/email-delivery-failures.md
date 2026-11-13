# Runbook: Email Delivery Failures

Orbital Logistics sends shipment notifications and internal email through the mail relay `mail-relay-01`, owned by the it-support team.

## Symptoms

Customers report that they no longer receive shipment notifications, or the relay's outgoing queue grows above 1,000 messages. Undelivered customer notifications are a P2. Internal email that is delayed but delivered is a P3.

## Diagnose

1. Check the relay's outgoing queue and its most common error. Errors that mention "blocked" or "rejected" usually mean that a receiving provider has started to refuse our mail.
2. Check whether the company's sending domain has been put on a public blocklist. The relay dashboard shows the blocklist status.
3. Check recent changes to the domain's mail records. A wrong record makes receiving providers treat our mail as forged.

## Mitigate

- Fix any wrong mail record first; changes take up to an hour to spread.
- If the relay itself is down, fail over to the standby relay `mail-relay-02` from the it-support console. Queued messages are sent once it takes over.

Do not resend notifications in bulk after an outage: customers would receive duplicates. The notification service resends only the messages that were never accepted by the relay.
