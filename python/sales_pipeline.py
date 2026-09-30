import pandas as pd
from sqlalchemy import create_engine
engine = create_engine(
    "mssql+pyodbc://@localhost\\SQLEXPRESS/AdventureWorksDW2022?driver=ODBC+Driver+17+for+SQL+Server"
)

df = pd.read_sql_table("FactInternetSales", con=engine)
print("Data successfully read from SQL!")
print(df.shape)
print(df.head())
# Missing values
print("\nMissing values per column:")
print(df.isnull().sum()[df.isnull().sum() > 0])

# Duplicates
print("\nDuplicate rows:", df.duplicated().sum())

# Data types
print("\nData types:")
print(df.dtypes)

# Negative/invalid numeric values
print("\nNegative value checks:")
for col in ["SalesAmount", "OrderQuantity", "UnitPrice", "DiscountAmount", "ProductStandardCost"]:
    if col in df.columns:
        print(f"{col}: {(df[col] < 0).sum()} negative values")  
        # Drop columns that are entirely empty (found in Step 3)
df = df.drop(columns=["CarrierTrackingNumber", "CustomerPONumber"])

# Select relevant columns for reporting
keep_cols = [
    "SalesOrderNumber", "SalesOrderLineNumber", "OrderDate", "DueDate", "ShipDate",
    "ProductKey", "CustomerKey", "SalesTerritoryKey",
    "OrderQuantity", "UnitPrice", "SalesAmount", "DiscountAmount",
    "ProductStandardCost", "TaxAmt", "Freight"
]
df = df[keep_cols]

# Rename for clarity
df = df.rename(columns={
    "SalesOrderNumber": "OrderNumber",
    "OrderQuantity": "Quantity",
    "ProductStandardCost": "ProductCost"
})

print("\nColumns after preprocessing:")
print(df.columns.tolist())
print(df.shape)
# Profit
df["Profit"] = df["SalesAmount"] - df["ProductCost"] - df["DiscountAmount"]

# Discount Percentage
df["DiscountPercentage"] = (df["DiscountAmount"] / df["SalesAmount"]).round(4) * 100

# Date parts
df["OrderYear"] = df["OrderDate"].dt.year
df["OrderMonth"] = df["OrderDate"].dt.month
df["OrderQuarter"] = df["OrderDate"].dt.quarter

# Sales Category
df["SalesCategory"] = df["SalesAmount"].apply(lambda x: "High" if x > 1000 else "Low")

# Extra feature: Profit per unit
df["ProfitPerUnit"] = (df["Profit"] / df["Quantity"]).round(2)

# Extra feature: Order lead time (days between order and ship date)
df["LeadTimeDays"] = (df["ShipDate"] - df["OrderDate"]).dt.days

print("\nColumns after feature engineering:")
print(df.columns.tolist())
print(df[["Profit", "DiscountPercentage", "OrderYear", "OrderMonth", "OrderQuarter", "SalesCategory", "ProfitPerUnit", "LeadTimeDays"]].head())
df.to_sql(
    name="PythonSalesReportingTable",
    con=engine,
    if_exists="replace",
    index=False,
)
print("\nData successfully written to SQL table!")
