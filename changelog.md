## 2026.2.6

- Added `SELECT_DISTINCT` method to `Query` class
- Fixed `Query.sql()` being async (it is now synchronous)
- Fixed race condition in SQLite `Engine.connection()` (Issue 44)
- Fixed `Query` cloning to correctly share `Database` instance (Issue 42)
- Added bounds checking to `Results.row()` and `.cell()` (Issue 41)
- Improved `Database` initialization exception handling (Issue 49)
- Fixed SQLite connection string regex to handle paths correctly (Issue 43)
- Standardized decorator naming in SQLite engine (Issue 46)
- Logic fixes in `Query` class: removed dead code, fixed indentation, cleaned up `WHERE` (Issues 51, 52, 54)
- Added missing tests for `Database` class (Issue 53)
- Fixed generic exception swallowing in SQLite pool close (Issue 45)
- Removed unused imports and empty requirements.txt (Issues 47, 48)

## 2026.2.5

- Added support for fluent aggregate functions (`.FILTER()`, `.DISTINCT()`)
- Added `q.FX` namespace for dialect-agnostic function calls (`q.FX.json_object`, etc.)
- Added `.OFFSET()` support
- Added fluent `.JOIN(...).ON(...)` syntax
- Refactored aggregate functions to not implicitly include `OVER()` (breaking change: use `.OVER()` explicitly for window functions)
- Fixed issue with DSN WHERE it was ignoring dsn values and defaulting to system values
- Fixed `ORDER_BY` bug where unary negation (`-field`) caused syntax errors
- Implemented `Field.__eq__` and `Field.__ne__` to handle `None` values (compiles to `IS NULL` / `IS NOT NULL`)
- Fixed `IndeterminateDatatypeError` in `json_build_object` and other polymorphic functions by inlining string arguments safely (handling MySQL backslash escaping)
- Improved `Results` API developer experience: added `.first()`, `.cell()`, `.cells()`, and `.rows()` (unlimited)


## 2026.2.4

- Added ability to fetch dict from results and result via .data() and fetch all values in a specific column in sql query result set


## 2026.2.3

- Added support for connection pooling


## 2026.2.2

- Added support for window functions


## 2026.2.1

- Added support for dynamic tables and removed datatypes and specialised python descriptor(s)
