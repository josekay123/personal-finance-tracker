import pandas as pd
import os
import matplotlib.pyplot as plt

# File to store finance data
FINANCE_FILE = "personal_finance.csv"

# Function to load or initialize the finance tracker
def load_finances():
    if os.path.exists(FINANCE_FILE):
        df = pd.read_csv(FINANCE_FILE)
        print("Loaded existing financial data.")
    else:
        df = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Description"])
        print("Initialized new finance tracker.")
    return df

# Function to add a new record (income or expense)
def add_record(df):
    date = input("Enter the date (YYYY-MM-DD): ")
    record_type = input("Enter the type (Income/Expense): ").capitalize()
    if record_type not in ["Income", "Expense"]:
        print("Invalid type. Use 'Income' or 'Expense'.")
        return df

    category = input("Enter the category (e.g., Salary, Food, Rent, Entertainment): ")
    amount = float(input("Enter the amount: "))
    description = input("Enter a short description: ")

    # Append the new record
    new_record = pd.DataFrame({
        "Date": [date],
        "Type": [record_type],
        "Category": [category],
        "Amount": [amount],
        "Description": [description]
    })
    df = pd.concat([df, new_record], ignore_index=True)
    print("\nRecord added successfully!")
    return df

# Function to view all records
def view_records(df):
    print("\nAll Records:")
    print(df)

# Function to get a summary of finances
def summary(df):
    if df.empty:
        print("No records available to summarize.")
        return

    print("\nFinancial Summary:")
    total_income = df.loc[df['Type'] == 'Income', 'Amount'].sum()
    total_expense = df.loc[df['Type'] == 'Expense', 'Amount'].sum()
    balance = total_income - total_expense

    print(f"Total Income: {total_income:.2f}")
    print(f"Total Expenses: {total_expense:.2f}")
    print(f"Balance: {balance:.2f}")

    # Categorized summary
    print("\nExpenses by Category:")
    expense_summary = df.loc[df['Type'] == 'Expense'].groupby("Category")["Amount"].sum()
    print(expense_summary)

    print("\nIncome by Category:")
    income_summary = df.loc[df['Type'] == 'Income'].groupby("Category")["Amount"].sum()
    print(income_summary)

# Function to visualize expenses and income
def plot_finances(df):
    if df.empty:
        print("No records available to plot.")
        return

    # Plot expenses by category
    expense_summary = df.loc[df['Type'] == 'Expense'].groupby("Category")["Amount"].sum()
    income_summary = df.loc[df['Type'] == 'Income'].groupby("Category")["Amount"].sum()

    plt.figure(figsize=(10, 5))

    # Subplot for expenses
    plt.subplot(1, 2, 1)
    if not expense_summary.empty:
        expense_summary.plot(kind='bar', color='tomato')
        plt.title('Expenses by Category')
        plt.ylabel('Amount')
    else:
        plt.title('No Expenses to Show')

    # Subplot for income
    plt.subplot(1, 2, 2)
    if not income_summary.empty:
        income_summary.plot(kind='bar', color='seagreen')
        plt.title('Income by Category')
        plt.ylabel('Amount')
    else:
        plt.title('No Income to Show')

    plt.tight_layout()
    plt.show()

# Function to save finances to a file
def save_finances(df):
    df.to_csv(FINANCE_FILE, index=False)
    print("Financial data saved successfully.")

# Main program
def main():
    print("Welcome to the Personal Finance Tracker!\n")
    finances = load_finances()

    while True:
        print("\nOptions:")
        print("1. Add a new record (Income/Expense)")
        print("2. View all records")
        print("3. Show summary")
        print("4. Visualize finances")
        print("5. Save and exit")

        choice = input("Enter your choice (1/2/3/4/5): ")

        if choice == "1":
            finances = add_record(finances)
        elif choice == "2":
            view_records(finances)
        elif choice == "3":
            summary(finances)
        elif choice == "4":
            plot_finances(finances)
        elif choice == "5":
            save_finances(finances)
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the program
if __name__ == "__main__":
    main()
