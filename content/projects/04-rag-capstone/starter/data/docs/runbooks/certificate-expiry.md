# Runbook: TLS Certificate Expiry

The platform team owns the public TLS certificates, including the certificate for the shipment tracking website `track-web`. The network team owns the certificates on internal devices, such as the VPN concentrators and the warehouse scanner gateway `scan-gw`.

## Alerts

The certificate monitor `cert-watch` checks every certificate once a day. It raises a P4 ticket 30 days before a certificate expires, a P3 at 14 days, and a P2 at 7 days. An expired certificate on a public service is a P1, because every customer connection fails.

## Renew a certificate

1. Find the certificate in the secret manager. Its record names the owning team and the systems that use it.
2. Request a renewal through the certificate portal. Renewals for public certificates take up to one working day.
3. Install the renewed certificate on every system listed in the record, during a maintenance window if the service must restart.
4. Check the new expiry date from outside the network, not only on the server.

## If a certificate has already expired

Install the renewed certificate immediately, without waiting for a maintenance window. If no renewal is available yet, ask the platform team for an emergency certificate. Never disable certificate checks on clients to work around an expired certificate.
