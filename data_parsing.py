import csv

def parse_financial_data_from_csv(file_path):
    financial_data = {
        "income": 0,
        "expenses": 0,
        "transactions": []
    }

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            trans_date = row['Trans. Date']
            post_date = row['Post Date']
            description = row['Description']
            amount = float(row['Amount'].replace(',', ''))
            category = row['Category']

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
