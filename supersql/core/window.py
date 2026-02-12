"""
Window functions and specifications for SuperSQL.

This module provides support for SQL window functions with a fluent Python API.
"""

from typing import Union, List, Any, Optional


class WindowSpec:
    """
    Represents a window specification for OVER clause.
    
    Can include PARTITION BY, ORDER BY, and frame specifications.
    """
    
    def __init__(self, partition_by=None, order_by=None, frame=None):
        """
        Initialize window specification.
        
        Args:
            partition_by: List of columns to partition by
            order_by: List of (column, direction) tuples for ordering
            frame: Frame specification string (e.g., "ROWS BETWEEN ...")
        """
        self.partition_by = partition_by or []
        self.order_by = order_by or []
        self.frame = frame
    
    def ORDER_BY(self, *args):
        """
        Add ORDER BY clause to window specification.
        
        Use negative prefix (-column) for descending order.
        Use positive prefix (+column) for explicit ascending order.
        """
        order_parts = []
        for arg in args:
            if isinstance(arg, str):
                if arg.startswith('-'):
                    order_parts.append((arg[1:], 'DESC'))
                else:
                    order_parts.append((arg, 'ASC'))
            elif hasattr(arg, 'direction'):
                # OrderedField object from __neg__ or __pos__
                order_parts.append((str(arg.field), arg.direction))
            else:
                # Regular column/Field object - default to ASC
                order_parts.append((str(arg), 'ASC'))
        
        self.order_by.extend(order_parts)
        return self
    
    def ROWS_BETWEEN(self, start: str, end: str):
        """
        Add frame specification to window.
        
        Args:
            start: Start of frame (e.g., "UNBOUNDED PRECEDING", "1 PRECEDING")
            end: End of frame (e.g., "CURRENT ROW", "1 FOLLOWING")
        """
        self.frame = f"ROWS BETWEEN {start} AND {end}"
        return self
    
    def RANGE_BETWEEN(self, start: str, end: str):
        """
        Add RANGE frame specification to window.
        
        Args:
            start: Start of frame
            end: End of frame
        """
        self.frame = f"RANGE BETWEEN {start} AND {end}"
        return self
    
    def compile(self, compiler) -> tuple[str, list]:
        """
        Compile window specification to SQL.
        
        Returns:
            Tuple of (sql_string, parameters)
        """
        parts = []
        params = []
        
        if self.partition_by:
            partition_cols = []
            for col in self.partition_by:
                # Handle OrderedField objects (shouldn't be in PARTITION BY, but just in case)
                if hasattr(col, 'field'):
                    # Extract just the field part, ignore direction
                    partition_cols.append(str(col.field))
                else:
                    partition_cols.append(str(col))
            parts.append(f"PARTITION BY {', '.join(partition_cols)}")
        
        if self.order_by:
            order_strs = []
            for col, direction in self.order_by:
                order_strs.append(f"{col} {direction}")
            parts.append(f"ORDER BY {', '.join(order_strs)}")
        
        if self.frame:
            parts.append(self.frame)
        
        return " ".join(parts), params


class WindowFunction:
    """
    Base class for window functions.
    
    Represents a SQL window function with OVER clause.
    """
    
    def __init__(self, name: str, *args, over=None):
        """
        Initialize window function.
        
        Args:
            name: Function name (e.g., "ROW_NUMBER", "RANK")
            *args: Function arguments
            over: WindowSpec object or window name (string)
        """
        self.name = name
        self.args = args
        self.over = over
        self.alias = None
        self._filter = None
        self._distinct = False

    def DISTINCT(self):
        """
        Add DISTINCT to the function call.
        e.g. COUNT(DISTINCT col)
        """
        self._distinct = True
        return self

    def FILTER(self, condition):
        """
        Add FILTER (WHERE ...) clause.
        """
        self._filter = condition
        return self

    
    def OVER(self, spec: Union[str, WindowSpec] = None):
        """
        Define window for the function.
        If spec is None, defaults to empty window OVER ().
        """
        self.over = spec if spec is not None else WindowSpec()
        return self
    
    def AS(self, alias: str):
        """
        Set alias for this window function.
        
        Args:
            alias: Column alias
        
        Returns:
            Self for method chaining
        """
        self.alias = alias
        return self
    
    def compile(self, compiler) -> tuple[str, list]:
        """
        Compile window function to SQL.
        
        Returns:
            Tuple of (sql_string, parameters)
        """
        params = []
        
        # Build function call
        distinct_str = "DISTINCT " if self._distinct else ""
        
        if self.args:
            arg_strs = []
            for arg in self.args:
                if hasattr(arg, 'compile'):
                    sql, p = arg.compile(compiler)
                    arg_strs.append(sql)
                    params.extend(p)
                elif arg is None:
                    arg_strs.append('NULL')
                else:
                    arg_strs.append(str(arg))
            func_call = f"{self.name}({distinct_str}{', '.join(arg_strs)})"
        else:
            func_call = f"{self.name}()"
        
        # Build FILTER clause
        filter_clause = ""
        if self._filter:
            # We need to compile the condition. 
            # If the condition object has a compile method (it should), use it.
            # Otherwise treat as string.
            if compiler and hasattr(self._filter, 'compile'):
                f_sql, f_params = self._filter.compile(compiler)
                filter_clause = f" FILTER (WHERE {f_sql})"
                params.extend(f_params)
            else:
                filter_clause = f" FILTER (WHERE {self._filter})"

        # Build OVER clause (Optional now)
        over_clause = ""
        if self.over:
            if isinstance(self.over, str):
                # Named window reference
                over_clause = f" OVER {self.over}"
            elif isinstance(self.over, WindowSpec):
                # Inline window specification
                spec_sql, spec_params = self.over.compile(compiler)
                if spec_sql:
                    over_clause = f" OVER ({spec_sql})"
                else:
                    over_clause = " OVER ()"
                params.extend(spec_params)
            
        sql = f"{func_call}{over_clause}{filter_clause}"
        
        # Add alias if specified
        if self.alias:
            sql = f"{sql} AS {self.alias}"
        
        return sql, params

    
    def __str__(self):
        """String representation for use in SELECT."""
        sql, _ = self.compile(None)
        return sql


# Ranking Functions

class ROW_NUMBER(WindowFunction):
    """ROW_NUMBER() window function."""
    
    def __init__(self, over=None):
        super().__init__("ROW_NUMBER", over=over)


class RANK(WindowFunction):
    """RANK() window function."""
    
    def __init__(self, over=None):
        super().__init__("RANK", over=over)


class DENSE_RANK(WindowFunction):
    """DENSE_RANK() window function."""
    
    def __init__(self, over=None):
        super().__init__("DENSE_RANK", over=over)


class NTILE(WindowFunction):
    """NTILE(n) window function."""
    
    def __init__(self, n: int, over=None):
        super().__init__("NTILE", n, over=over)


class PERCENT_RANK(WindowFunction):
    """PERCENT_RANK() window function."""
    
    def __init__(self, over=None):
        super().__init__("PERCENT_RANK", over=over)


class CUME_DIST(WindowFunction):
    """CUME_DIST() window function."""
    
    def __init__(self, over=None):
        super().__init__("CUME_DIST", over=over)


# Value Functions

class LAG(WindowFunction):
    """LAG(column [, offset [, default]]) window function."""
    
    def __init__(self, column, offset: int = 1, default=None, over=None):
        if default is not None:
            super().__init__("LAG", column, offset, default, over=over)
        else:
            super().__init__("LAG", column, offset, over=over)


class LEAD(WindowFunction):
    """LEAD(column [, offset [, default]]) window function."""
    
    def __init__(self, column, offset: int = 1, default=None, over=None):
        if default is not None:
            super().__init__("LEAD", column, offset, default, over=over)
        else:
            super().__init__("LEAD", column, offset, over=over)


class FIRST_VALUE(WindowFunction):
    """FIRST_VALUE(column) window function."""
    
    def __init__(self, column, over=None):
        super().__init__("FIRST_VALUE", column, over=over)


class LAST_VALUE(WindowFunction):
    """LAST_VALUE(column) window function."""
    
    def __init__(self, column, over=None):
        super().__init__("LAST_VALUE", column, over=over)


class NTH_VALUE(WindowFunction):
    """NTH_VALUE(column, n) window function."""
    
    def __init__(self, column, n: int, over=None):
        super().__init__("NTH_VALUE", column, n, over=over)


# Aggregate Window Functions

class WindowSum(WindowFunction):
    """SUM(column) as window function."""
    
    def __init__(self, column, over=None):
        super().__init__("SUM", column, over=over)


class WindowAvg(WindowFunction):
    """AVG(column) as window function."""
    
    def __init__(self, column, over=None):
        super().__init__("AVG", column, over=over)


class WindowCount(WindowFunction):
    """COUNT(column) as window function."""
    
    def __init__(self, column, over=None):
        super().__init__("COUNT", column, over=over)


class WindowMin(WindowFunction):
    """MIN(column) as window function."""
    
    def __init__(self, column, over=None):
        super().__init__("MIN", column, over=over)


class WindowMax(WindowFunction):
    """MAX(column) as window function."""
    
    def __init__(self, column, over=None):
        super().__init__("MAX", column, over=over)
