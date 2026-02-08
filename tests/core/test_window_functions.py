"""Tests for window functions."""

import pytest
from supersql import Query, Table

def test_row_number_basic():
    """Test basic ROW_NUMBER() window function."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Build query with ROW_NUMBER
    # Use proper chaining as Query methods return new instances
    row_num = query.ROW_NUMBER().OVER(
        query.PARTITION_BY(sales.product)
    ).AS('row_num')
    
    # The result of SELECT must be used
    sql = query.SELECT(sales.product, sales.amount, row_num).FROM(sales).build()
    
    assert "ROW_NUMBER()" in sql
    assert "OVER (PARTITION BY" in sql
    assert 'AS row_num' in sql


def test_row_number_with_order():
    """Test ROW_NUMBER() with ORDER BY in OVER clause."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Create window spec with ORDER BY
    spec = query.PARTITION_BY(sales.product).ORDER_BY(sales.amount)
    
    row_num = query.ROW_NUMBER().OVER(spec).AS('row_num')
    
    sql = query.SELECT(sales.product, sales.amount, row_num).FROM(sales).build()
    
    assert "ROW_NUMBER()" in sql
    assert "PARTITION BY" in sql
    assert "ORDER BY" in sql
    # Field includes table name in string representation
    assert '"sales"."amount" ASC' in sql


def test_row_number_with_descending_order():
    """Test ROW_NUMBER() with descending ORDER BY."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Use negative prefix for descending order
    spec = query.PARTITION_BY(sales.product).ORDER_BY(-sales.amount)
    
    row_num = query.ROW_NUMBER().OVER(spec).AS('row_num')
    
    sql = query.SELECT(sales.product, sales.amount, row_num).FROM(sales).build()
    
    assert "ORDER BY" in sql
    assert '"sales"."amount" DESC' in sql


def test_rank_functions():
    """Test RANK() and DENSE_RANK() window functions."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    spec = query.PARTITION_BY(sales.product).ORDER_BY(-sales.amount)
    
    rank = query.RANK().OVER(spec).AS('rank')
    dense = query.DENSE_RANK().OVER(spec).AS('dense_rank')
    
    sql = query.SELECT(sales.product, sales.amount, rank, dense).FROM(sales).build()
    
    assert "RANK() OVER" in sql
    assert "DENSE_RANK() OVER" in sql


def test_lag_function():
    """Test LAG() window function."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    spec = query.PARTITION_BY(sales.product).ORDER_BY(sales.date)
    
    prev_amount = query.LAG(sales.amount, 1).OVER(spec).AS('prev_amount')
    
    sql = query.SELECT(sales.date, sales.amount, prev_amount).FROM(sales).build()
    
    assert "LAG(" in sql
    assert "prev_amount" in sql


def test_lead_function():
    """Test LEAD() window function."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    spec = query.PARTITION_BY(sales.product).ORDER_BY(sales.date)
    
    next_amount = query.LEAD(sales.amount, 1).OVER(spec).AS('next_amount')
    
    sql = query.SELECT(sales.date, sales.amount, next_amount).FROM(sales).build()
    
    assert "LEAD(" in sql
    assert "next_amount" in sql


def test_aggregate_window_function():
    """Test SUM() as window function."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Use empty PARTITION_BY() to start a window spec, then add ORDER_BY
    # query.ORDER_BY returns a Query object, not a WindowSpec
    spec = query.PARTITION_BY().ORDER_BY(sales.date).ROWS_BETWEEN('UNBOUNDED PRECEDING', 'CURRENT ROW')
    
    running_total = query.SUM(sales.amount).OVER(spec).AS('running_total')
    
    sql = query.SELECT(sales.date, sales.amount, running_total).FROM(sales).build()
    
    assert "SUM(" in sql
    assert "OVER (" in sql
    assert "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW" in sql


def test_named_window():
    """Test named window specification."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Define window spec
    w = query.PARTITION_BY(sales.product).ORDER_BY(-sales.amount)
    
    # Use named window
    row_num = query.ROW_NUMBER().OVER('w').AS('row_num')
    rank = query.RANK().OVER('w').AS('rank')
    
    # Chain the named window definition
    sql = query.SELECT(
        sales.product, 
        sales.amount, 
        row_num, 
        rank
    ).FROM(sales).WINDOW('w', w).build()
    
    assert "OVER w" in sql
    assert "WINDOW w AS (" in sql
    assert "PARTITION BY" in sql


def test_multiple_window_functions():
    """Test multiple window functions in same query."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    spec = query.PARTITION_BY(sales.product).ORDER_BY(-sales.amount)
    
    row_num = query.ROW_NUMBER().OVER(spec).AS('row_num')
    rank = query.RANK().OVER(spec).AS('rank')
    dense_rank = query.DENSE_RANK().OVER(spec).AS('dense_rank')
    
    sql = query.SELECT(
        sales.product,
        sales.amount,
        row_num,
        rank,
        dense_rank
    ).FROM(sales).build()
    
    assert "ROW_NUMBER()" in sql
    assert "RANK()" in sql
    assert "DENSE_RANK()" in sql


def test_window_with_rows_between():
    """Test ROWS BETWEEN frame specification."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Moving average over previous 2 rows
    # Use PARTITION_BY() to create spec
    spec = query.PARTITION_BY().ORDER_BY(sales.date).ROWS_BETWEEN('2 PRECEDING', 'CURRENT ROW')
    
    moving_avg = query.AVG(sales.amount).OVER(spec).AS('moving_avg')
    
    sql = query.SELECT(sales.date, sales.amount, moving_avg).FROM(sales).build()
    
    assert "AVG(" in sql
    assert "ROWS BETWEEN 2 PRECEDING AND CURRENT ROW" in sql


def test_window_with_range_between():
    """Test RANGE BETWEEN frame specification."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Use PARTITION_BY() to create spec
    spec = query.PARTITION_BY().ORDER_BY(sales.amount).RANGE_BETWEEN('UNBOUNDED PRECEDING', 'CURRENT ROW')
    
    cumulative = query.SUM(sales.amount).OVER(spec).AS('cumulative')
    
    sql = query.SELECT(sales.amount, cumulative).FROM(sales).build()
    
    assert "RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW" in sql


def test_ntile_function():
    """Test NTILE() window function."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Use PARTITION_BY() to create spec
    spec = query.PARTITION_BY().ORDER_BY(-sales.amount)
    
    quartile = query.NTILE(4).OVER(spec).AS('quartile')
    
    sql = query.SELECT(sales.product, sales.amount, quartile).FROM(sales).build()
    
    assert "NTILE(4)" in sql


def test_first_last_value():
    """Test FIRST_VALUE() and LAST_VALUE() window functions."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    spec = query.PARTITION_BY(sales.product).ORDER_BY(sales.date)
    
    first = query.FIRST_VALUE(sales.amount).OVER(spec).AS('first_amount')
    last = query.LAST_VALUE(sales.amount).OVER(spec).AS('last_amount')
    
    sql = query.SELECT(sales.date, sales.amount, first, last).FROM(sales).build()
    
    assert "FIRST_VALUE(" in sql
    assert "LAST_VALUE(" in sql


def test_window_without_partition():
    """Test window function without PARTITION BY (entire result set)."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Window over entire result set
    # Use PARTITION_BY() to create WindowSpec, effectively empty partition
    spec = query.PARTITION_BY().ORDER_BY(-sales.amount)
    
    row_num = query.ROW_NUMBER().OVER(spec).AS('overall_rank')
    
    sql = query.SELECT(sales.product, sales.amount, row_num).FROM(sales).build()
    
    assert "ROW_NUMBER()" in sql
    assert "OVER (" in sql
    # Should not have PARTITION BY since we didn't add columns
    assert "PARTITION BY" not in sql


def test_empty_over_clause():
    """Test window function with empty OVER clause."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    # Create empty spec
    from supersql.core.window import WindowSpec
    spec = WindowSpec()
    
    row_num = query.ROW_NUMBER().OVER(spec).AS('row_num')
    
    sql = query.SELECT(sales.product, row_num).FROM(sales).build()
    
    assert "ROW_NUMBER() OVER ()" in sql


def test_multiple_aggregate_windows():
    """Test multiple aggregate window functions."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    spec = query.PARTITION_BY(sales.product).ORDER_BY(sales.date)
    
    total = query.SUM(sales.amount).OVER(spec).AS('running_total')
    avg = query.AVG(sales.amount).OVER(spec).AS('running_avg')
    cnt = query.COUNT(sales.amount).OVER(spec).AS('running_count')
    
    sql = query.SELECT(sales.date, sales.amount, total, avg, cnt).FROM(sales).build()
    
    assert "SUM(" in sql
    assert "AVG(" in sql
    assert "COUNT(" in sql


def test_percent_rank_cume_dist():
    """Test PERCENT_RANK() and CUME_DIST() window functions."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    spec = query.PARTITION_BY(sales.product).ORDER_BY(sales.amount)
    
    pct_rank = query.PERCENT_RANK().OVER(spec).AS('pct_rank')
    cume = query.CUME_DIST().OVER(spec).AS('cume_dist')
    
    sql = query.SELECT(sales.amount, pct_rank, cume).FROM(sales).build()
    
    assert "PERCENT_RANK()" in sql
    assert "CUME_DIST()" in sql


def test_nth_value():
    """Test NTH_VALUE() window function."""
    query = Query("postgres", database="test")
    sales = Table("sales")
    
    spec = query.PARTITION_BY(sales.product).ORDER_BY(sales.date)
    
    second = query.NTH_VALUE(sales.amount, 2).OVER(spec).AS('second_value')
    
    sql = query.SELECT(sales.date, sales.amount, second).FROM(sales).build()
    
    assert "NTH_VALUE(" in sql
    assert ", 2)" in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
