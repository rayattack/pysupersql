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
