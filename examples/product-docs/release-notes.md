# Atlas SDK Release Notes

## 0.4.0

Released: 2026-05-15

### Added

- Added `session.close()` to flush pending events before shutdown.
- Added clearer authentication errors for missing and expired tokens.

### Changed

- `createSession()` now validates `appId` before creating a session.
- Quickstart examples now use environment variables for API tokens.

### Fixed

- Fixed an issue where event metadata could be dropped when the session closed immediately after `sendEvent()`.

## 0.3.0

Released: 2026-04-18

### Added

- Added `sendEvent()` support for custom event properties.

