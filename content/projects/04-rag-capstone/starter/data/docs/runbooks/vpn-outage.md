# Runbook: Office VPN Problems

The network team owns the office VPN concentrators, including `vpn-ber` for the Berlin office.

## Symptoms

Users report that the VPN disconnects every few minutes, that video calls drop, or that they cannot connect at all. Intermittent drops for a whole office are usually a P2; a complete outage for an office is a P1.

## Diagnose

1. Check the concentrator's dashboard for CPU above 90 percent, or for many tunnels re-establishing at once.
2. Check the office's internet link. Packet loss above 2 percent on the uplink causes tunnel drops.
3. Check whether a certificate on the concentrator has expired. An expired certificate makes every new connection fail.

## Mitigate

- If the uplink is degraded, switch the office to the backup link from the network console.
- If CPU is the problem, move half of the users to the secondary concentrator by changing their VPN profile.
- If a certificate has expired, install the renewed certificate from the secret manager and restart the VPN service in a maintenance window.

Tell affected users through the office channel, and update them every 30 minutes until the problem is fixed.
