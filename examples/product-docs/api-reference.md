# Atlas SDK API Reference

This page documents the synthetic Atlas SDK API surface used by the demo docs corpus.

## `createSession(options)`

Creates a new Atlas session.

### Parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `token` | string | Yes | Public API token for the current workspace |
| `appId` | string | Yes | Application identifier used in event metadata |

### Returns

Returns a `Session` object.

## `session.sendEvent(event)`

Sends an event through an active session.

### Parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | Yes | Event name in namespace form |
| `properties` | object | No | Additional event metadata |

## `session.close()`

Closes the current session and flushes pending events.

```javascript
await session.close();
```

