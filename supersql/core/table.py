
class Condition(object):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def compile(self, compiler):
        # Generate SQL and Params
        # Left is always a Field, so use str(left) -> "table"."column"
        # Right is value.
        placeholder = compiler.next_placeholder()
        sql = f"{self.left} {self.operator} {placeholder}"
        return sql, [self.right]

    def __str__(self):
        # Return string representation with literal value (quoted)
        # Use simple quoting logic since we don't have access to Field._quote easily unless we duplicate
        val = self.right
        if isinstance(val, str): qval = f"'{val}'"
        elif val is None: qval = "NULL"
        elif val is True: qval = "TRUE"
        elif val is False: qval = "FALSE"
        else: qval = str(val)
        return f"{self.left} {self.operator} {qval}"

    def __and__(self, other):
        return BooleanCondition(self, "AND", other)
    
    def __or__(self, other):
        return BooleanCondition(self, "OR", other)


class BooleanCondition(object):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
        
    def compile(self, compiler):
        l_sql, l_params = self.left.compile(compiler) if hasattr(self.left, 'compile') else (str(self.left), [])
        r_sql, r_params = self.right.compile(compiler) if hasattr(self.right, 'compile') else (str(self.right), [])
        
        return f"({l_sql}) {self.operator} ({r_sql})", l_params + r_params

    def __str__(self):
        return f"({self.left}) {self.operator} ({self.right})"


class InCondition(Condition):
    def compile(self, compiler):
        if isinstance(self.right, (list, tuple)):
            placeholders = []
            params = []
            for val in self.right:
                placeholders.append(compiler.next_placeholder())
                params.append(val)
            sql = f"{self.left} {self.operator} ({', '.join(placeholders)})"
            return sql, params
        else:
            p = compiler.next_placeholder()
            return f"{self.left} {self.operator} ({p})", [self.right]

    def __str__(self):
        if isinstance(self.right, (list, tuple)):
            # Join quoted values
            # Need a quote helper? Or just str() and rely on Field._quote logic duplication?
            # Or self.left.table._quote if available? No.
            # Simple manual quoting for string repr:
            values = []
            for x in self.right:
                if isinstance(x, str): values.append(f"'{x}'")
                else: values.append(str(x))
            val_str = ", ".join(values)
            return f"{self.left} {self.operator} ({val_str})"
        return f"{self.left} {self.operator} ({self.right})"


class BetweenCondition(object):
    def __init__(self, field, lower, upper):
        self.field = field
        self.lower = lower
        self.upper = upper
        
    def compile(self, compiler):
        p1 = compiler.next_placeholder()
        p2 = compiler.next_placeholder()
        return f"{self.field} BETWEEN {p1} AND {p2}", [self.lower, self.upper]

    def __str__(self):
        # Quote lower/upper if strings
        l = f"'{self.lower}'" if isinstance(self.lower, str) else str(self.lower)
        u = f"'{self.upper}'" if isinstance(self.upper, str) else str(self.upper)
        return f"{self.field} BETWEEN {l} AND {u}"


class Field(object):
    def __init__(self, name, table=None):
        self.name = name
        self.table = table

    def __str__(self):
        if self.table:
            t_name = self.table._alias or self.table._name
            return f'"{t_name}"."{self.name}"'
        return f'"{self.name}"'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return Condition(self, '=', other)

    def __ne__(self, other):
        return Condition(self, '<>', other)

    def __gt__(self, other):
        return Condition(self, '>', other)

    def __ge__(self, other):
        return Condition(self, '>=', other)

    def __lt__(self, other):
        return Condition(self, '<', other)

    def __le__(self, other):
        return Condition(self, '<=', other)

    # For logical operators on Fields (e.g. boolean fields), we need to be careful.
    # But usually & | are used on Conditions.
    # If used on Field directly (e.g. field1 & field2), it implies boolean columns?
    # Or bitwise? Assuming boolean logic for now as per previous behavior.
    
    def __and__(self, other):
        # This creates a BooleanCondition? Or just string?
        # If we want parameterization, everything must be Condition.
        # But Field & Field is weird unless they are boolean.
        # Let's assume Condition.
        return BooleanCondition(self, "AND", other)

    def __or__(self, other):
        return BooleanCondition(self, "OR", other)

    def __invert__(self):
        # NOT condition
        # Implementation depends on how we handle "NOT Field".
        return f"NOT ({self})"
        
    def IN(self, other):
        # IN takes a list of values.
        # We need a special Condition for IN that takes a list and generates multiple placeholders.
        return InCondition(self, 'IN', other)

    def NOT_IN(self, other):
        return InCondition(self, 'NOT IN', other)

    def LIKE(self, other):
        return Condition(self, 'LIKE', other)

    def ILIKE(self, other):
        return Condition(self, 'ILIKE', other)

    def BETWEEN(self, lower, upper):
        return BetweenCondition(self, lower, upper)

    def IS_NULL(self):
        return f"{self} IS NULL"

    def IS_NOT_NULL(self):
        return f"{self} IS NOT NULL"

    def AS(self, alias):
        return f"{self} AS {alias}"




class Table(object):
    def __init__(self, name, schema=None, alias=None):
        self._name = name
        self._schema = schema
        self._alias = alias

    def __getattr__(self, name):
        return Field(name, table=self)

    def __str__(self):
        name = f'"{self._name}"'
        if self._schema:
            name = f'"{self._schema}".{name}'
        
        if self._alias:
            return f'{name} AS "{self._alias}"'
        return name
    
    def __tn__(self):
        if self._schema:
            return f'"{self._schema}"."{self._name}"'
        return f'"{self._name}"'

    def AS(self, alias):
        return Table(self._name, self._schema, alias)
    
    def alias(self, alias):
        return self.AS(alias)
