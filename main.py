from expenses import add_expenses, save_expenses

def main():
    try:
        amount = float(input("Please enter expenses amount... "))
        category = input("Please enter category... ")
        
        expense = add_expenses(amount, category)
        save_expenses(expense)
        
        print("Expense saved successfully")
    except ValueError:
        print("Please enter a valid amount")
        
if __name__ == "__main__":
    main()