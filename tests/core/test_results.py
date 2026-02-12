import pytest
from supersql.core.results import Results

def test_results_bounds():
    data = [{'id': 1}, {'id': 2}]
    # Results copies list.
    results = Results(data)
    
    # row(1) -> returns first (0th index)
    r1 = results.row(1)
    assert r1.id == 1
    
    r2 = results.row(2)
    assert r2.id == 2
    
    # Test invalid row access
    with pytest.raises(IndexError):
        # 0 is invalid for 1-based index
        results.row(0) 
        
    with pytest.raises(IndexError):
        results.row(3)
        
    # cell(row, col) legacy access (0-based)
    # cell(0, 'id') -> data[0]['id'] -> 1
    val = results.cell(0, 'id')
    assert val == 1
    
    # invalid legacy access
    assert results.cell(2, 'id') is None
    assert results.cell(-1, 'id') is None

def test_results_empty():
    results = Results([])
    assert results.first() is None
    assert results.cell() is None
    
def test_results_iteration():
    data = [{'id': 1}, {'id': 2}]
    results = Results(data)
    
    items = []
    # __iter__ returns Result objects
    for r in results:
        items.append(r.id)
    assert items == [1, 2]
