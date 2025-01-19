import pandas as pd

df = pd.read_csv("Rating_with_history.csv")
aggregated = pd.read_csv("Rating_without_history.csv")

def get_current_credit_category(company_name):
    result = aggregated.loc[aggregated['Name'] == company_name, 'Average_Rating']
    return str(result.iloc[0]) if not result.empty else "Medium Risk"

# Method 2: Query Original DataFrame
def get_ratings_by_company(company_name):
    result = df.loc[df['Name'] == company_name]
    if not result.empty:
        return result.set_index('Date')['Rating'].to_dict()
    return "Company not found"


# print("Current Credit Category (Aggregated):", get_current_credit_category("Blattner Energy LLC"))
# print("Ratings on Specific Date:", get_ratings_by_company("Blattner Energy LLC"))