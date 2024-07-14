import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import openai

# def parse_financial_data_from_csv(file):
#     financial_data = {
#         "income": 0,
#         "expenses": 0,
#         "transactions": []
#     }

#     try:
#         df = pd.read_csv(file)
#     except Exception as e:
#         st.error(f"Error reading the CSV file: {e}")
#         return None

#     for index, row in df.iterrows():
#         trans_date = row['Trans. Date']
#         post_date = row['Post Date']
#         description = row['Description']
#         amount = row['Amount']
#         category = row['Category']

#         if isinstance(amount, str):
#             amount = float(amount.replace(',', ''))
#         else:
#             amount = float(amount)

#         financial_data["transactions"].append({
#             "trans_date": trans_date,
#             "post_date": post_date,
#             "description": description.strip(),
#             "amount": amount,
#             "category": category.strip()
#         })

#         if category.lower() in ['payments and credits', 'income']:
#             financial_data["income"] += amount
#         else:
#             financial_data["expenses"] += amount

#     return financial_data

def generate_plotly_charts(transactions):
    df = pd.DataFrame(transactions)
    df['Trans. Date'] = pd.to_datetime(df['trans_date'])
    df['YearMonth'] = df['Trans. Date'].dt.to_period('M')
    cleaned_data = df[df['amount'] > 0]

    # Monthly expenditure trend
    monthly_expenditure = cleaned_data.groupby('YearMonth')['amount'].sum().reset_index()
    monthly_expenditure['YearMonth'] = monthly_expenditure['YearMonth'].astype(str)
    fig_monthly_trend = px.line(monthly_expenditure, x='YearMonth', y='amount', title='Monthly Expenditure Trend', labels={'YearMonth': 'Month', 'amount': 'Total Expenditure'}, line_shape='spline')
    st.plotly_chart(fig_monthly_trend)

    # Category distribution
    cleaned_category_distribution = cleaned_data.groupby('category')['amount'].sum().reset_index()
    fig_category_distribution = px.pie(cleaned_category_distribution, values='amount', names='category', title='Category Distribution', labels={'category': 'Category', 'amount': 'Total Expenditure'}, color='category')
    st.plotly_chart(fig_category_distribution)

    # Top spending categories
    top_spending_categories = cleaned_category_distribution.sort_values(by='amount', ascending=False).head(10)
    fig_top_spending_categories = px.bar(top_spending_categories, x='category', y='amount', title='Top Spending Categories', labels={'category': 'Category', 'amount': 'Total Expenditure'}, color='category')
    st.plotly_chart(fig_top_spending_categories)

    # Transaction frequency by category
    transaction_frequency = cleaned_data['category'].value_counts().reset_index()
    transaction_frequency.columns = ['category', 'Transaction Count']
    fig_transaction_frequency = px.bar(transaction_frequency, x='category', y='Transaction Count', title='Transaction Frequency by Category', labels={'category': 'Category', 'Transaction Count': 'Number of Transactions'}, color='category')
    st.plotly_chart(fig_transaction_frequency)

    # Daily spending pattern
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

    # Monthly spending breakdown by category
    monthly_category_spending = cleaned_data.groupby(['YearMonth', 'category'])['amount'].sum().reset_index()
    monthly_category_spending['YearMonth'] = monthly_category_spending['YearMonth'].astype(str)
    fig_monthly_category_spending = px.bar(monthly_category_spending, x='YearMonth', y='amount', color='category', title='Monthly Spending Breakdown by Category', labels={'YearMonth': 'Month', 'amount': 'Total Expenditure', 'category': 'Category'})
    st.plotly_chart(fig_monthly_category_spending)

    # Top merchants/vendors
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

def ask_chatgpt(api_key, question, document_text):
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial assistant."},
            {"role": "user", "content": f"{question}\n\n{document_text}"}
        ]
    )

    answer = response.choices[0].message['content']
    return answer

def load_test_file():
    return pd.read_csv('test.csv')

def parse_financial_data_from_csv(df):
    financial_data = {
        "income": 0,
        "expenses": 0,
        "transactions": []
    }

    try:
        for index, row in df.iterrows():
            trans_date = row['Trans. Date']
            post_date = row['Post Date']
            description = row['Description']
            amount = row['Amount']
            category = row['Category']

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
    except Exception as e:
        st.error(f"Error parsing the financial data: {e}")
        return None

    return financial_data

def main():
    st.set_page_config(layout="wide")
    st.title("MoneyMentor :male-teacher:")
    st.write("Introducing MoneyMentor, the ultimate financial sidekick! :men-with-bunny-ears-partying:")
    st.write(" Upload your bank statements and let the fun begin. Get a detailed breakdown of your income and expenses —because knowing where your money goes shouldn't be a mystery! Our colorful charts will make you feel like a financial wizard 🧙‍♂️. Want to see your spending habits? We’ve got pie charts that’ll make you hungry for more insights 🥧.")
    st.write("Curious about where all your coffee money went? Ask our AI assistant and get answers faster than your last impulse buy 🛒. Search through your transactions like a detective 🕵️‍♂️ and keep your finances in check. With MoneyMentor, managing your money is as easy as pie—literally! 🍰")

    with st.sidebar:
        st.header("Upload your Bank Statement")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        st.header("Or Use Test Data")
        if st.button("Load Test Data"):
            uploaded_file = "test.csv"
        st.write('---')
        st.header("Enter your OpenAI API Key")
        user_api_key = st.text_input("API Key [not a requirement]", type="password")
        st.write('Developed by Krishna Thakar :heart:')

    if uploaded_file:
        try:
            if uploaded_file == "test.csv":
                df = load_test_file()
            else:
                df = pd.read_csv(uploaded_file)
                # st.write(df.head())  # Display the first few rows to check content

            financial_data = parse_financial_data_from_csv(df)

            if financial_data is None:
                st.error("Failed to parse financial data.")
                return

            data, analysis, assistant, search = st.tabs(["Data :chart_with_upwards_trend:", "Analysis :memo:", "Ask Assistant :robot_face:", "Search :mag:"])

            with data:
                income, null, expense, null2 = st.columns(4)
                with income:
                    st.subheader("Income :heavy_dollar_sign:")
                    st.success(f"$ {financial_data['income']*-1:.2f}")
                with expense:
                    st.subheader("Expenses :credit_card:")
                    st.error(f"$ {financial_data['expenses']:.2f}")
                st.subheader("Transactions :receipt:")
                st.write(pd.DataFrame(financial_data["transactions"]))

            with analysis:
                st.subheader("Detailed Charts")
                generate_plotly_charts(financial_data["transactions"])

            with assistant:
                st.header("Ask Your Financial Assistant")
                if user_api_key:
                    question = st.text_input("Ask a question related to your financial data:")
                    if question:
                        document_text = "\n".join([f"{t['trans_date']} {t['post_date']} {t['description']} {t['amount']} {t['category']}" for t in financial_data["transactions"]])
                        answer = ask_chatgpt(user_api_key, question, document_text)
                        st.write(answer)
                else:
                    st.warning("Please enter your OpenAI API key to use the Ask Assistant tab.")

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
        if not uploaded_file:
            st.warning("Please upload a CSV file to proceed.")
        if not user_api_key:
            st.warning("Please enter your OpenAI API key to proceed.")

if __name__ == "__main__":
    main()
