"""
Database inspection and reflection utilities.

This module provides functionality to inspect database schemas and automatically
create Table objects from existing database tables.
"""

import asyncio
from typing import Dict, List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from supersql.core.database import Database
    from supersql.core.table import Table


class DatabaseInspector:
    """Inspector for database schema reflection."""
    
    def __init__(self, database: 'Database'):
        """
        Initialize the inspector with a database connection.
        
        Args:
            database: The Database instance to inspect
        """
        self.database = database
        self._engine_type = database._engine._query._engine
    
    async def get_all_tables(self) -> Dict[str, 'Table']:
        """
        Get all tables in the database as a dictionary of Table objects.
        
        Returns:
            Dict mapping table names to Table objects
        """
        table_names = await self._get_table_names()
        tables = {}
        
        for table_name in table_names:
            tables[table_name] = await self.reflect_table(table_name)
        
        return tables
    
    async def reflect_table(self, table_name: str) -> 'Table':
        """
        Reflect a single table schema into a Table object.
        
        Args:
            table_name: Name of the table to reflect
            
        Returns:
            Table object with reflected schema
        """
        columns = await self._get_table_columns(table_name)
        return self._create_table_class(table_name, columns)
    
    async def _get_table_names(self) -> List[str]:
        """Get list of all table names in the database."""
        if self._engine_type in ('postgres', 'postgresql'):
            return await self._get_postgres_table_names()
        elif self._engine_type == 'mysql':
            return await self._get_mysql_table_names()
        elif self._engine_type == 'sqlite':
            return await self._get_sqlite_table_names()
        else:
            raise NotImplementedError(f"Table reflection not implemented for {self._engine_type}")
    
    async def _get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a specific table."""
        if self._engine_type in ('postgres', 'postgresql'):
            return await self._get_postgres_columns(table_name)
        elif self._engine_type == 'mysql':
            return await self._get_mysql_columns(table_name)
        elif self._engine_type == 'sqlite':
            return await self._get_sqlite_columns(table_name)
        else:
            raise NotImplementedError(f"Column reflection not implemented for {self._engine_type}")
    
    async def _get_postgres_table_names(self) -> List[str]:
        """Get PostgreSQL table names."""
        sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        
        async with self.database._engine.pool.acquire() as conn:
            rows = await conn.fetch(sql)
            return [row['table_name'] for row in rows]
    
    async def _get_postgres_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get PostgreSQL column information."""
        sql = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            ordinal_position
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = $1
        ORDER BY ordinal_position
        """
        
        async with self.database._engine.pool.acquire() as conn:
            rows = await conn.fetch(sql, table_name)
            return [dict(row) for row in rows]
    
    async def _get_mysql_table_names(self) -> List[str]:
        """Get MySQL table names."""
        sql = "SHOW TABLES"
        
        async with self.database._engine.pool.acquire() as conn:
            rows = await conn.fetch(sql)
            # MySQL returns table names in a column named 'Tables_in_<database>'
            if rows:
                column_name = list(rows[0].keys())[0]
                return [row[column_name] for row in rows]
            return []
    
    async def _get_mysql_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get MySQL column information."""
        sql = f"DESCRIBE {table_name}"
        
        async with self.database._engine.pool.acquire() as conn:
            rows = await conn.fetch(sql)
            columns = []
            for i, row in enumerate(rows):
                columns.append({
                    'column_name': row['Field'],
                    'data_type': row['Type'],
                    'is_nullable': 'YES' if row['Null'] == 'YES' else 'NO',
                    'column_default': row['Default'],
                    'ordinal_position': i + 1
                })
            return columns
    
    async def _get_sqlite_table_names(self) -> List[str]:
        """Get SQLite table names."""
        sql = """
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
        
        async with self.database._engine.pool.acquire() as conn:
            rows = await conn.fetch(sql)
            return [row['name'] for row in rows]
    
    async def _get_sqlite_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get SQLite column information."""
        sql = f"PRAGMA table_info({table_name})"
        
        async with self.database._engine.pool.acquire() as conn:
            rows = await conn.fetch(sql)
            columns = []
            for row in rows:
                columns.append({
                    'column_name': row['name'],
                    'data_type': row['type'],
                    'is_nullable': 'YES' if not row['notnull'] else 'NO',
                    'column_default': row['dflt_value'],
                    'ordinal_position': row['cid'] + 1
                })
            return columns
    
    def _create_table_class(self, table_name: str, columns: List[Dict[str, Any]]) -> 'Table':
        """
        Create a Table class dynamically from column information.
        
        Args:
            table_name: Name of the table
            columns: List of column dictionaries
            
        Returns:
            Table instance with reflected schema
        """
        from supersql.core.table import Table
        from supersql.reflection.types import map_database_type_to_supersql
        
        # Create a dynamic class that inherits from Table
        class_name = f"Reflected{table_name.title().replace('_', '')}"
        
        # Create class attributes for each column
        class_attrs = {
            '__tablename__': table_name,
            '__module__': 'supersql.reflection.dynamic'
        }
        
        # Add column attributes
        for col in columns:
            column_name = col['column_name']
            data_type = col['data_type']
            is_nullable = col['is_nullable'] == 'YES'
            
            # Map database type to SuperSQL type
            supersql_field = map_database_type_to_supersql(
                data_type, 
                nullable=is_nullable,
                default=col.get('column_default'),
                max_length=col.get('character_maximum_length')
            )
            
            class_attrs[column_name] = supersql_field
        
        # Create the dynamic class
        ReflectedTable = type(class_name, (Table,), class_attrs)
        
        # Return an instance of the reflected table
        return ReflectedTable()
    
    async def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        table_names = await self._get_table_names()
        return table_name in table_names
