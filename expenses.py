import json

       

def add_expense(amount, category):
    return {
        "amount": amount,
        "category": category
    }


def save_expenses(expense):
    with open("data.json", "r") as file:
        data = json.load(file)
    data.append(expense)
    
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4) 