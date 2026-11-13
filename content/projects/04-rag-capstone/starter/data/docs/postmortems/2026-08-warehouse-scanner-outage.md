# Postmortem: Warehouse Scanner Outage, August 2026

## Summary

For 2 hours and 10 minutes, handheld scanners in all three warehouses could not upload scans, and parcels stopped appearing on the tracking website. The incident was a P1. No scans were lost: the scanners kept them and uploaded them after the fix.

## Timeline

- 06:02: the first warehouse reports "Upload failed" on every scanner.
- 06:15: the other two warehouses report the same problem; the incident becomes a P1 and the incident commander is notified.
- 06:40: the warehouses switch to the paper fallback.
- 07:30: the network team finds that the certificate on the scanner gateway `scan-gw` expired at 06:00.
- 08:12: a renewed certificate is installed, and the scanners upload their stored scans.

## Causes

The certificate monitor did raise tickets 30, 14 and 7 days before expiry, but they were assigned to the it-support team, which owns the scanners, instead of the network team, which owns `scan-gw`. The tickets were closed as "not ours" without being reassigned.

## Actions

- Correct the owner of the `scan-gw` certificate in the secret manager, so that alerts go to the network team.
- Never close a ticket as "not ours": reassign it to the right team.
- Add the scanner gateway to the certificate expiry dashboard reviewed in the weekly operations meeting.
