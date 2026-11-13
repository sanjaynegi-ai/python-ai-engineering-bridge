# Runbook: Shipment Tracking Website Errors

The platform team owns the public shipment tracking website, `track-web`, and the public API gateway, `api-gw-01`.

## Symptoms

Customers see error pages or blank pages, or monitoring shows HTTP 5xx responses for more than 1 percent of requests. If the site is down for all customers, it is a P1.

## Check the load balancer first

Most tracking-site outages start at the load balancer. Open the load balancer dashboard and check how many backend instances are healthy. If fewer than two instances are healthy, the site cannot serve its normal traffic.

## Then

1. Check the most recent deployment. If errors started within 30 minutes of a deployment, roll it back from the deployment tool; do not try to fix forward during an outage.
2. Check the API gateway's error rate. The website calls the gateway, so gateway errors appear as website errors.
3. Check the health of the orders database. A database failover also causes errors on the tracking site.

## Communication

For a P1, the incident commander posts on the public status page within 15 minutes and updates it every 30 minutes, as described in the incident communication policy.
