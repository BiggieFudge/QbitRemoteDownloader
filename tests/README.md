# Tests Directory

This directory contains essential tests for the QbitRemoteDownloader project.

## Test Files

### Core Functionality Tests
- **`test_basic.py`** - Basic functionality tests (imports, settings, client initialization)
- **`test_tmdb_simple.py`** - Basic TMDB API functionality tests
- **`debug.py`** - General debugging and troubleshooting tests

## Running Tests

To run the basic tests:
```bash
python tests/test_basic.py
```

To run TMDB tests:
```bash
python tests/test_tmdb_simple.py
```

## Test Structure

The tests are organized to verify:
1. **Basic Setup** - Module imports, configuration loading
2. **API Connectivity** - TMDB, Prowlarr, qBittorrent connections
3. **Core Functionality** - Essential bot operations

## Notes

- Only essential tests are kept to maintain project cleanliness
- Debug tests are available for troubleshooting when needed
- Tests focus on core functionality rather than exhaustive coverage
