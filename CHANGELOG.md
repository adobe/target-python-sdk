# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.1.0 - 2023-01-09

### Added

- Additional support for complex domain parsing for on-device-decisioning

### Fixed

- Client custom Mbox parameters now correctly support dot notation
- ODD artifacts are now limited to property-specific activities if the `property_token` is included during initialization

### Changed

- Updated Target OpenAPI specifications and associated tests
