import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

def generate_plotly_charts(transactions):
    df = pd.DataFrame(transactions)
    df['Trans. Date'] = pd.to_datetime(df['trans_date'])
    df['YearMonth'] = df['Trans. Date'].dt.to_period('M')
    cleaned_data = df[df['amount'] > 0]

    # Monthly Expenditure Trend
    monthly_expenditure = cleaned_data.groupby('YearMonth')['amount'].sum().reset_index()
    monthly_expenditure['YearMonth'] = monthly_expenditure['YearMonth'].astype(str)
    fig_monthly_trend = px.line(monthly_expenditure, x='YearMonth', y='amount', title='Monthly Expenditure Trend', labels={'YearMonth': 'Month', 'amount': 'Total Expenditure'}, line_shape='spline')
    st.plotly_chart(fig_monthly_trend)

    # Category Distribution
    cleaned_category_distribution = cleaned_data.groupby('category')['amount'].sum().reset_index()
    top_colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
    fig_category_distribution = px.pie(cleaned_category_distribution, values='amount', names='category', title='Category Distribution',labels={'category': 'Category', 'amount': 'Total Expenditure'}, color='category', color_discrete_sequence=top_colors)
    st.plotly_chart(fig_category_distribution)

    # Top Spending Categories with custom colors
    top_spending_categories = cleaned_category_distribution.sort_values(by='amount', ascending=False).head(10)
    top_colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
    fig_top_spending_categories = px.bar(top_spending_categories, x='category', y='amount', title='Top Spending Categories', labels={'category': 'Category', 'amount': 'Total Expenditure'}, color='category', color_discrete_sequence=top_colors)
    st.plotly_chart(fig_top_spending_categories)

    # Transaction Frequency by Category with custom colors
    transaction_frequency = cleaned_data['category'].value_counts().reset_index()
    transaction_frequency.columns = ['category', 'Transaction Count']
    freq_colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
    fig_transaction_frequency = px.bar(transaction_frequency, x='category', y='Transaction Count', title='Transaction Frequency by Category', labels={'category': 'Category', 'Transaction Count': 'Number of Transactions'}, color='category', color_discrete_sequence=freq_colors)
    st.plotly_chart(fig_transaction_frequency)

    # Daily Spending Pattern
    cleaned_data['DayOfWeek'] = cleaned_data['Trans. Date'].dt.day_name()
    cleaned_data['DayOfMonth'] = cleaned_data['Trans. Date'].dt.day
    daily_spending_pattern = cleaned_data.groupby(['DayOfWeek', 'DayOfMonth'])['amount'].sum().reset_index()
    daily_spending_pattern_pivot = daily_spending_pattern.pivot(index='DayOfWeek', columns='DayOfMonth', values='amount').fillna(0)

    fig_daily_spending_pattern = go.Figure(data=go.Heatmap(
            z=daily_spending_pattern_pivot.values,
            x=daily_spending_pattern_pivot.columns,
            y=daily_spending_pattern_pivot.index,
            colorscale='YlGnBu'))
    fig_daily_spending_pattern.update_layout(title='Daily Spending Pattern', xaxis_title='Day of Month', yaxis_title='Day of Week')
    st.plotly_chart(fig_daily_spending_pattern)

    # Monthly Spending Breakdown by Category
    monthly_category_spending = cleaned_data.groupby(['YearMonth', 'category'])['amount'].sum().reset_index()
    monthly_category_spending['YearMonth'] = monthly_category_spending['YearMonth'].astype(str)
    fig_monthly_category_spending = px.bar(monthly_category_spending, x='YearMonth', y='amount', color='category', title='Monthly Spending Breakdown by Category', labels={'YearMonth': 'Month', 'amount': 'Total Expenditure', 'category': 'Category'})
    st.plotly_chart(fig_monthly_category_spending)

    # Top Merchants/Vendors
    merchant_spending = df.groupby('description')['amount'].sum().reset_index().sort_values(by='amount', ascending=False).head(10)
    fig_top_merchants = px.bar(merchant_spending, x='description', y='amount', title='Top Merchants/Vendors', labels={'description': 'Merchant/Vendor', 'amount': 'Total Expenditure'})
    st.plotly_chart(fig_top_merchants)

def filter_transactions(transactions, query):
    query = query.lower()
    filtered_transactions = [
        transaction for transaction in transactions
        if query in transaction["trans_date"].lower()
        or query in transaction["post_date"].lower()
        or query in transaction["description"].lower()
        or query in transaction["category"].lower()
    ]
    return filtered_transactions

def main():
    st.set_page_config(layout="wide")
    st.title("AI-Powered Financial Planning Assistant")

    with st.sidebar:
        st.header("Upload your Bank Statement")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            file_path = "uploaded_statement.csv"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

    if uploaded_file is not None:
        try:
            financial_data = parse_financial_data_from_csv(uploaded_file)
            data, analysis, search = st.tabs(["Data :chart_with_upwards_trend:", "Analysis :memo:", "Search :mag:"])

            with data:
                income, null, expense, null2 = st.columns(4)
                with income:
                    st.subheader("Income :money_with_wings:")
                    st.success(f"$ {financial_data['income']*-1:.2f}")
                with expense:
                    st.subheader("Expenses :receipt:")
                    st.error(f"$ {financial_data['expenses']:.2f}")
                st.subheader("Transactions")
                st.write(pd.DataFrame(financial_data["transactions"]))

            with analysis:
                st.subheader("Detailed Charts")
                generate_plotly_charts(financial_data["transactions"])

            with search:
                st.header("Search Transactions")
                query = st.text_input("Enter date, description, or category to search:")
                if query:
                    filtered_transactions = filter_transactions(financial_data["transactions"], query)
                    if filtered_transactions:
                        st.write(pd.DataFrame(filtered_transactions))
                    else:
                        st.write("No transactions found for the given search query.")

        except Exception as e:
            st.error(f"Error processing the file: {e}")
    else:
        st.warning("Please upload a CSV file to proceed.")

if __name__ == "__main__":
    main()
