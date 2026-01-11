from datetime import datetime
import json

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except(FileNotFoundError, FileExistsError, json.JSONDecodeError):
        return[]

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
    

def add_expenses(amount, category):
    return {
        "amount": amount,
        "category": category,
        "date": datetime.now().strftime("%Y-%m")
    }
    
    
def save_expenses(expense):
    data= load_data()
    data.append(expense)
    save_data(data)
        
    
def get_expenses():
   return load_data()

def monthly_summary(month):
    return sum (
        exp["amount"]
        for exp in load_data()
        if exp.get("date")== month
    )

def category_summary():
    summary= {}
    for exp in load_data():
        cat = exp["category"]
        summary[cat]= summary.get(cat, 0) + exp["amount"]
    
    return summary