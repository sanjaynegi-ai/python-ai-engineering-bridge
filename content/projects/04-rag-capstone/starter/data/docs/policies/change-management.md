# Policy: Change Management

This policy covers changes to production systems at Orbital Logistics (a fictional company): deployments, configuration changes and infrastructure work.

## Types of change

- **Standard changes** are routine, low-risk changes with an approved procedure, such as renewing a certificate or adding disk space. They need no approval, but must be recorded in the change calendar.
- **Normal changes** need approval from the owning team's lead and must be recorded in the change calendar at least two working days in advance.
- **Emergency changes** fix an active P1 or P2 incident. The incident commander approves them, and they are recorded in the change calendar within one working day afterwards.

## Every change needs

1. A rollback plan, tested in the staging environment where possible.
2. A named engineer who watches the change for 30 minutes after it goes live.
3. A link to the ticket that explains why the change is needed.

## Change freeze

From 20 November to 31 December, the peak shipping season, only standard and emergency changes are allowed. Normal changes wait until January unless the head of IT operations approves an exception.
