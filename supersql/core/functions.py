from typing import Any, List
from .compiler import PostgresCompiler, MySQLCompiler, SQLiteCompiler

class Function:
    """
    Represents a generic SQL function call.
    e.g. random_func(1, 'a') -> random_func($1, $2)
    """
    def __init__(self, name: str, *args):
        self.name = name
        self.args = args
        self.alias = None

    def AS(self, alias: str):
        self.alias = alias
        return self

    def compile(self, compiler) -> tuple[str, list]:
        params = []
        arg_strs = []
        
        for arg in self.args:
            if hasattr(arg, 'compile'):
                sql, p = arg.compile(compiler)
                arg_strs.append(sql)
                params.extend(p)
            elif hasattr(arg, 'table') or hasattr(arg, 'resolve'):
                # Field or similar object that should be rendered as string
                arg_strs.append(str(arg))
            elif isinstance(arg, str):
                # Inline strings to avoid IndeterminateDatatypeError in polymorphic functions
                # Escape single quotes
                safe_str = arg.replace("'", "''")
                
                # MySQL also requires backslash escaping unless NO_BACKSLASH_ESCAPES is on.
                # To be safe, we escape backslashes for MySQL if the compiler is MySQLCompiler.
                if isinstance(compiler, MySQLCompiler):
                    safe_str = safe_str.replace("\\", "\\\\")
                
                arg_strs.append(f"'{safe_str}'")
            else:
                param = compiler.next_placeholder()
                params.append(arg)
                arg_strs.append(param)
        
        sql = f"{self.name}({', '.join(arg_strs)})"
        
        if self.alias:
            sql = f"{sql} AS {self.alias}"
            
        return sql, params

class JsonObject(Function):
    """
    Smart function for JSON object creation.
    Compiles to json_build_object for Postgres, json_object for others.
    """
    def __init__(self, *args):
        # args are expected to be key, value, key, value...
        super().__init__("json_object", *args)

    def compile(self, compiler) -> tuple[str, list]:
        # Postgres uses json_build_object
        if isinstance(compiler, PostgresCompiler): self.name = "json_build_object"
        else: self.name = "json_object"  # SQLite, MySQL use json_object
        return super().compile(compiler)

class Functions:
    """
    Dynamic function builder namespace (q.FX).
    """
    def __getattr__(self, name: str):
        def _builder(*args): return Function(name, *args)
        return _builder

    def json_object(self, *args):
        return JsonObject(*args)
