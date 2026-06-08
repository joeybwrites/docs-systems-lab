# Atlas SDK Troubleshooting

## Missing Token

If `createSession()` returns `AUTH_TOKEN_MISSING`, confirm that `ATLAS_TOKEN` is set in your local environment.

```bash
echo "$ATLAS_TOKEN"
```

Do not commit tokens into source control. Use environment variables or a local secret manager.

## Expired Token

If the SDK returns `AUTH_TOKEN_EXPIRED`, create a new token in the Atlas dashboard and restart the local development process.

## Session Closes Too Early

If an event does not appear after shutdown, call `session.close()` and wait for it to complete before ending the process.

```javascript
await session.sendEvent({ type: "document.viewed" });
await session.close();
```

