from abc import ABC, abstractmethod
from typing import List, Any
from .state import QueryState

class SQLCompiler(ABC):
    """
    Abstract base class for converting QueryState into a SQL string.
    Handles dialect differences like placeholders (%s vs $1).
    """

    def __init__(self):
        self._placeholder_count = 0

    @property
    @abstractmethod
    def parameter_placeholder(self) -> str:
        """Return the placeholder string (e.g., %s, $1, ?)"""
        pass
    
    def reset(self):
        self._placeholder_count = 0

    def next_placeholder(self) -> str:
        """Generate the next parameter placeholder"""
        return self.parameter_placeholder

    def compile(self, state: QueryState) -> tuple[str, list]:
        """
        Main entry point. Orchestrates the generation of SQL parts
        in the correct order.
        """
        self.reset()
        
        compiled_parts = []
        bound_parameters = []
        
        # Compile chained previous states
        for prev_state in state.chain:
            sql, params = self._compile_single(prev_state)
            compiled_parts.append(sql)
            bound_parameters.extend(params)
            
        # Compile current state
        sql, params = self._compile_single(state)
        compiled_parts.append(sql)
        bound_parameters.extend(params)
        
        return "; ".join(compiled_parts), bound_parameters

    def _compile_single(self, state: QueryState) -> tuple[str, list]:
        # 0. Transaction management
        if state.statement_type == 'BEGIN':
            return "BEGIN", []
        if state.statement_type == 'COMMIT':
            return "COMMIT;", []

        # 1. CTEs (WITH clause)
        sql_parts = []
        parameters = []
        
        if state.ctes:
            cte_parts = []
            for alias, query in state.ctes:
                subquery_sql = query if isinstance(query, str) else query.print() 
                cte_parts.append(f"{alias} AS ({subquery_sql})")
            
            sql_parts.append(f"WITH {', '.join(cte_parts)}")

        # 2. Main Statement (SELECT / INSERT / UPDATE / DELETE)
        if state.statement_type == 'SELECT':
            sql, params = self._compile_select(state)
            sql_parts.append(sql)
            parameters.extend(params)
        elif state.statement_type == 'INSERT':
            sql, params = self._compile_insert(state)
            sql_parts.append(sql)
            parameters.extend(params)
        elif state.statement_type == 'UPDATE':
            sql, params = self._compile_update(state)
            sql_parts.append(sql)
            parameters.extend(params)
        elif state.statement_type == 'DELETE':
            sql, params = self._compile_delete(state)
            sql_parts.append(sql)
            parameters.extend(params)
            
        return "\n".join(part for part in sql_parts if part), parameters

    def _compile_select(self, state: QueryState) -> tuple[str, list]:
        parts = []
        
        # SELECT
        selects = state.selects or ['*']
        # Convert list to string, handling objects if necessary
        select_str = ", ".join(str(s) for s in selects)
        parts.append(f"SELECT {select_str}")
        
        # FROM
        if state.from_sources:
            from_str = ", ".join(str(f) for f in state.from_sources)
            parts.append(f"FROM {from_str}")
            
        # JOIN
        if state.joins:
            parts.extend(state.joins)
            
        # WHERE
        if state.wheres:
            where_str = " AND ".join(str(w).strip() for w in state.wheres)
            parts.append(f"WHERE {where_str}")
            
        # GROUP BY
        if state.groups:
            group_str = ", ".join(str(g) for g in state.groups)
            parts.append(f"GROUP BY {group_str}")
            
        # ORDER BY
        if state.orders:
            order_str = ", ".join(str(o) for o in state.orders)
            parts.append(f"ORDER BY {order_str}")
            
        # LIMIT / OFFSET
        if state.limit is not None:
             parts.append(f"LIMIT {state.limit}")
        if state.offset is not None:
             parts.append(f"OFFSET {state.offset}")
        if state.returning:
            parts.append(f"RETURNING {', '.join(state.returning)}")
        return " ".join(parts), []

    def _compile_insert(self, state: QueryState) -> tuple[str, list]:
        parts = []
        parameters = []
        parts.append(f"INSERT INTO {state.insert_table}")
        
        if state.insert_columns:
             parts.append(f"({', '.join(str(c) for c in state.insert_columns)})")
        
        if state.insert_values:
            # Parameterized values
            values_placeholders = []
            for row in state.insert_values:
                row_placeholders = []
                for val in row:
                    row_placeholders.append(self.next_placeholder())
                    parameters.append(val)
                values_placeholders.append(f"({', '.join(row_placeholders)})")
            parts.append(f"VALUES {', '.join(values_placeholders)}")
            
        elif state.values:
             parts.append(f"VALUES {', '.join(state.values)}")
             
        elif state.selects:
             sql, params = self._compile_select(state)
             parts.append(sql)
             parameters.extend(params)
             
        if state.returning:
            parts.append(f"RETURNING {', '.join(state.returning)}")
            
        return " ".join(parts), parameters

    def _compile_update(self, state: QueryState) -> tuple[str, list]:
        parts = []
        parts.append(f"UPDATE {state.update_table}")
        
        if state.updates:
             parts.append(f"SET {', '.join(state.updates)}")
        
        if state.wheres:
             parts.append(f"WHERE {' AND '.join(w.strip() for w in state.wheres)}")
             
        if state.returning:
             parts.append(f"RETURNING {', '.join(state.returning)}")
             
        return " ".join(parts), []

    def _compile_delete(self, state: QueryState) -> tuple[str, list]:
        parts = []
        parameters = []
        parts.append("DELETE FROM")

        if state.from_sources:
             parts.append(str(state.from_sources[0]))
        elif state.delete_table:
             parts.append(state.delete_table)
             
        if state.wheres:
            where_str = " AND ".join(str(w).strip() for w in state.wheres)
            parts.append(f"WHERE {where_str}")
            
        if state.returning:
            ret = ", ".join(state.returning)
            parts.append(f"RETURNING {ret}")
            
        return " ".join(parts), []

class PostgresCompiler(SQLCompiler):
    @property
    def parameter_placeholder(self) -> str:
        self._placeholder_count += 1
        return f"${self._placeholder_count}"

class MySQLCompiler(SQLCompiler):
    @property
    def parameter_placeholder(self) -> str:
        return "%s"

class SQLiteCompiler(SQLCompiler):
    @property
    def parameter_placeholder(self) -> str:
        return "?"
