# Runbook: Warehouse Scanner Outage

Warehouse staff scan every parcel with handheld scanners. The scanners send their scans over the warehouse Wi-Fi to the scanner gateway `scan-gw`, which forwards them to the tracking system. The it-support team owns the scanners, and the network team owns `scan-gw` and the warehouse Wi-Fi.

## Symptoms

Scanners show "No connection" or "Upload failed", or parcels stop appearing on the tracking website after they are scanned. One warehouse unable to scan is a P2. Two or more warehouses unable to scan is a P1, because shipments stop leaving the warehouses.

## Diagnose

1. Find out whether one scanner or every scanner is affected. A single scanner is usually a flat battery or a device fault: swap it for a spare.
2. If every scanner in one warehouse fails, check that warehouse's Wi-Fi from the network console.
3. If several warehouses fail at the same time, check `scan-gw`. Its certificate, its disk and its connection to the tracking system are the common causes.

## Fallback

Warehouses switch to the paper fallback: staff write down parcel numbers on the fallback sheet, and it-support enters them once the scanners work again. Scans are never lost by the scanners themselves; they keep up to 2,000 scans each until they can upload them.
