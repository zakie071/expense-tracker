import expenses
expenses.DATA_FILE = "test_data.json"

from expenses import add_expenses, category_summary,monthly_summary


def test_add_expenses():
    expenses = add_expenses(100, "Food")
    assert expenses["amount"] == 100
    assert expenses["category"]== "Food"
    assert "date" in expenses
    
def test_category_summary_empty():
    summary = category_summary()
    assert isinstance(summary, dict)
    
def test_monthly_summary_empty():
    total= monthly_summary("2099-01")
    assert total==0