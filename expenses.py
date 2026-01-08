from datetime import datetime
import json

DATA_FILE = "data.json"

def add_expenses(amount, category):
    return {
        "amount" : amount,
        "category": category,
        "date": datetime.now().strftime("%Y-%m")
    }
    
    
def save_expenses(expense):
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
        
    data.append(expense)

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
        
    
def get_expenses():
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def monthly_summary(month):
    expenses = get_expenses()
    total = 0
    
    for exp in expenses:
        if exp.get("date") == month:
            total += exp["amount"]
    
    return total

def category_suammary():
    expenses = get_expenses()
    summary = {}
    
    for exp in expenses:
        category = exp["category"]
        summary[category]= summary.get(category, 0) + exp["amount"]
        
    
    return summary