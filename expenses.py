import json

def save_expnses(expenses):
    with open("data.json", "r") as file:
        data = json.load(file)
    data.append(expenses)
    
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4) 
       

def add_expense(amount, category):
    expenses={
        "amount": amount,
        "category": category
    }
    return expenses