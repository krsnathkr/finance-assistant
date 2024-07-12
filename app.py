import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def parse_financial_data_from_csv(file):
    financial_data = {
        "income": 0,
        "expenses": 0,
        "transactions": []
    }

    df = pd.read_csv(file)
    for index, row in df.iterrows():
        trans_date = row['Trans. Date']
        post_date = row['Post Date']
        description = row['Description']
        amount = row['Amount']
        category = row['Category']

        # Ensure amount is a string before replacing commas
        if isinstance(amount, str):
            amount = float(amount.replace(',', ''))
        else:
            amount = float(amount)

        financial_data["transactions"].append({
            "trans_date": trans_date,
            "post_date": post_date,
            "description": description.strip(),
            "amount": amount,
            "category": category.strip()
        })

        if category.lower() in ['payments and credits', 'income']:
            financial_data["income"] += amount
        else:
            financial_data["expenses"] += amount

    return financial_data

def generate_expense_plot(transactions):
    # Summarize expenses by category
    category_totals = {}
    for transaction in transactions:
        category = transaction["category"]
        amount = transaction["amount"]
        if category.lower() not in ['payments and credits', 'income']:
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    plt.figure(figsize=(10, 5))
    plt.bar(categories, amounts)
    plt.xlabel('Category')
    plt.ylabel('Amount ($)')
    plt.title('Expenses by Category')
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(plt)

def main():
    st.title("AI-Powered Financial Planning Assistant")

    st.header("Upload your Bank Statement")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        file_path = "uploaded_statement.csv"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            financial_data = parse_financial_data_from_csv(uploaded_file)
            st.success("CSV parsing successful")
            st.header("Financial Data")
            st.write(f"Total Income: ${financial_data['income']}")
            st.write(f"Total Expenses: ${financial_data['expenses']}")
            st.header("Transactions")
            st.write(pd.DataFrame(financial_data["transactions"]))

            if st.button("View Expense Plot"):
                generate_expense_plot(financial_data["transactions"])
        except Exception as e:
            st.error(f"Error processing the file: {e}")

if __name__ == "__main__":
    main()
