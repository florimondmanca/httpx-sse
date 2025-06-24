# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 0.4.1 - 2025-06-24

### Fixed

* Always close the response async generator in `aiter_sse()`. (Pull #30)

## 0.4.0 - 2023-12-22

### Removed

* Dropped Python 3.7 support, as it has reached EOL. (Pull #21)

### Added

* Add official support for Python 3.12. (Pull #21)

### Fixed

* Allow `Content-Type` that contain but are not strictly `text/event-stream`. (Pull #22 by @dbuades)
* Improve error message when `Content-Type` is missing. (Pull #20 by @jamesbraza)

## 0.3.1 - 2023-06-01

### Added

* Add `__repr__()` for `ServerSentEvent` model, which may help with debugging and other tasks. (Pull #16)

## 0.3.0 - 2023-04-27

### Changed

* Raising an `SSEError` if the response content type is not `text/event-stream` is now performed as part of `iter_sse()` / `aiter_sse()`, instead of `connect_sse()` / `aconnect_sse()`. This allows inspecting the response before iterating on server-sent events, such as checking for error responses. (Pull #12)

## 0.2.0 - 2023-03-27

### Changed

* `connect_sse()` and `aconnect_sse()` now require a `method` argument: `connect_sse(client, "GET", "https://example.org")`. This provides support for SSE requests with HTTP verbs other than `GET`. (Pull #7)

## 0.1.0 - 2023-02-05

_Initial release_

### Added

* Add `connect_sse`, `aconnect_sse()`, `ServerSentEvent` and `SSEError`.
