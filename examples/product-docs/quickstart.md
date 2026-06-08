# Atlas SDK Quickstart

Atlas SDK is a synthetic example SDK used by this demo. It lets an application create a session, send events, and close the session when work is complete.

## Prerequisites

- Atlas SDK 0.4.0 or later
- A public API token
- A local development environment that can run JavaScript

## Install

```bash
npm install @example/atlas-sdk
```

## Create A Session

```javascript
import { createSession } from "@example/atlas-sdk";

const session = await createSession({
  token: process.env.ATLAS_TOKEN,
  appId: "demo-app"
});
```

## Send An Event

```javascript
await session.sendEvent({
  type: "document.viewed",
  properties: {
    page: "quickstart"
  }
});
```

## Verify Success

A successful session returns a `sessionId` and accepts an event without an error response. If the token is missing or expired, see [Troubleshooting](troubleshooting.md).

