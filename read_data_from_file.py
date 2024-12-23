import pandas as pd

def clean_data(df):
	# Make column names lowercase
	df.columns = df.columns.str.lower()
	# Convert the date column to date format
	df["date"] = pd.to_datetime(df["date"])
	# Create month_year column
	df["month_year"] = df["date"].dt.month.astype(str)+"_"+df["date"].dt.year.astype(str)
	# Change account data type to category
#	df['account'] = df["account"].astype('category')
	# Change description data type to category
	df['description'] = df["description"].astype('category')
	# Change account data type to category
	df['category'] = df["category"].astype('category')
	# Change tags data type to category
	df['tags'] = df["tags"].astype('category')
	# Create type column - credit or debit
	df["type"] = ""
	df.loc[df['amount'] < 0, 'type'] = 'debit'
	df.loc[df['amount'] >= 0, 'type'] = 'credit'
	# Convert amount column to abs - after type is cacluated above
	df["amount"] = df["amount"].abs()

def read_data():
	df = pd.read_csv("transactions.csv") 
	clean_data(df)
	return(df)


