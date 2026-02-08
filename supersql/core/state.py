from dataclasses import dataclass, field
from typing import List, Union, Optional, Any, Set

@dataclass
class QueryState:
    """
    Holds the semantic state of a query (AST-lite).
    This allows us to build the query in any order and compile it
    deterministically later.
    """
    # CTEs (Common Table Expressions)
    ctes: List[Any] = field(default_factory=list)
    
    # Chained statements (previous QueryStates in a chain)
    chain: List['QueryState'] = field(default_factory=list)

    # SELECT
    selects: List[Union[str, Any]] = field(default_factory=list)
    distinct: bool = False
    
    # FROM
    from_sources: List[Union[str, Any]] = field(default_factory=list)
    
    # JOIN
    joins: List[str] = field(default_factory=list)  # Storing pre-formatted strings for now, or objects
    
    # WHERE
    wheres: List[Union[str, Any]] = field(default_factory=list)
    
    # GROUP BY
    groups: List[Union[str, Any]] = field(default_factory=list)
    
    # ORDER BY
    orders: List[str] = field(default_factory=list)
    
    # LIMIT / OFFSET
    limit: Optional[int] = None
    offset: Optional[int] = None

    # INSERT / UPDATE / DELETE
    # We might need to track the "type" of query if it's not a SELECT
    # For now, let's focus on SELECT/DQL, but keep space for DML
    statement_type: str = 'SELECT'
    
    # DML specific
    insert_table: Optional[str] = None
    insert_columns: List[str] = field(default_factory=list)
    update_table: Optional[str] = None
    delete_table: Optional[str] = None
    
    values: List[str] = field(default_factory=list)
    updates: List[str] = field(default_factory=list)
    
    # RETURNING
    returning: List[str] = field(default_factory=list)

    # Metadata
    aliases: dict = field(default_factory=dict)
