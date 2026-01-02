from expenses import add_expense, save_expenses



def main():
    try:
        amount = float(input("Enter expense amount: "))
        category = input("Enter expense category: ")

        expense = add_expense(amount, category)
        save_expenses(expense)
        print(" Expenses saved successfully!")
    
    except ValueError:
        print("Invalid input. Please enter a numeric value for amount.")
    

if __name__ == "__main__":
    main()