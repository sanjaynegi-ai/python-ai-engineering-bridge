# Postmortem: Checkout API Outage, September 2026

## Summary

For 47 minutes, the checkout API returned HTTP 502 errors for all customers, and no orders could be placed on the website. The incident was a P1.

## Timeline

- 09:40: error rates on the checkout API rise above 50 percent; the platform on-call engineer is paged.
- 09:52: the page escalates to the secondary, because the primary did not acknowledge it.
- 10:05: the incident commander posts on the status page.
- 10:15: the team finds that a deployment at 09:35 changed the gateway timeout from 30 seconds to 3 seconds.
- 10:27: the deployment is rolled back, and the errors stop.

## Causes

A configuration change shortened the API gateway timeout below the time the payment provider sometimes needs. No test covered the change, and the deployment had no automatic rollback on error rate.

## Actions

- Add a test that checks gateway timeouts against the slowest dependency.
- Roll back deployments automatically when the error rate exceeds 5 percent for five minutes.
- Remind on-call engineers to acknowledge pages within 10 minutes.
