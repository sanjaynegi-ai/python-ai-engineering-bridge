# Runbook: Order Queue Backlog

New orders pass through the message queue `mq-orders` on their way from the checkout API to the order service. The platform team owns the queue.

## Symptoms

Customers receive their order confirmation late, or the queue dashboard shows more than 5,000 waiting messages. A backlog that keeps growing for 15 minutes is a P2; if confirmations are delayed by more than one hour, it is a P1.

## Diagnose

1. Check whether the order service consumers are running. If none are running, restart them from the platform console.
2. Check the consumers' error rate. Consumers that fail on every message put it back on the queue, so the backlog grows even though they are busy.
3. Check the dead-letter queue `mq-orders-dlq`. Messages that failed five times are moved there.

## Mitigate

- If the consumers are healthy but too slow, scale the order service from 4 to 8 instances.
- If one malformed message blocks the queue, move it to the dead-letter queue by hand, and record its message ID in the incident ticket.

Never purge `mq-orders`. Every message in it is a customer order.
