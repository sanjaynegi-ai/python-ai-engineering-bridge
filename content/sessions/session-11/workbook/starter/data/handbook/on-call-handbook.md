# On-Call Handbook

Orbital Logistics (a fictional company) runs a follow-the-sun on-call rotation for IT operations. This handbook explains who is on call, how incidents are classified, and how to escalate.

## Rotations

Each team has a primary and a secondary on-call engineer for one week, from Monday 09:00 to the following Monday 09:00, local time. The teams are platform, database, network and it-support. The rotation calendar is in the operations portal. Swaps must be agreed with the other engineer and recorded in the portal at least 24 hours in advance.

## Priorities

Every incident gets a priority when it is opened:

- **P1**: a critical service is down, or data is at risk, for many users. Example: the shipment tracking website is down for all customers.
- **P2**: a major function is degraded, or works only with a workaround. Example: the Berlin office VPN drops every few minutes.
- **P3**: a minor problem for some users. Example: a label printer prints slightly misaligned labels.
- **P4**: a cosmetic issue or a request. Example: a replacement laptop keyboard.

## Escalation

If the primary on-call engineer does not acknowledge a page within 10 minutes, the paging system escalates to the secondary. If neither acknowledges within 20 minutes, it escalates to the team's engineering manager. A P1 incident always notifies the incident commander on duty, who coordinates communication and decides when the incident is resolved.

## Handover

At the end of a rotation, write a handover note listing open incidents, recent changes and anything the next engineer should watch. Handover notes go in the team channel and in the operations portal.
