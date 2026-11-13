# Policy: Data Retention

This policy says how long Orbital Logistics keeps operational data, and how it is deleted.

## Retention periods

| Data | Kept for |
|---|---|
| Application logs | 90 days |
| Nightly database backups | 35 days |
| Incident tickets and postmortems | 3 years |
| Monitoring metrics | 13 months |
| Shipment tracking events | 2 years after delivery |

## Deletion

Data is deleted by automated retention jobs, never by hand. Each job records what it deleted in the retention log. If a retention job fails, the owning team treats it as a P3.

## Personal data in logs

Application logs must not contain customer names, addresses, phone numbers or document contents. Log identifiers instead, such as an order number or a file name. If personal data is found in a log, report it to the security team as a P3, and fix the code that wrote it.

## Legal holds

The legal team can place a hold on specific data, which stops its deletion until the hold is lifted. Retention jobs skip data under a hold.
