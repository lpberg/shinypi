import pandas as pd
import os

def read_in_csvs():
	combined_df = pd.DataFrame()
	for subdir, dirs, files in os.walk('./'):
		for csv_file in files:
			if csv_file.endswith(".csv"):
				df = pd.read_csv(csv_file)
				print(df.shape[0])
				combined_df = pd.concat([combined_df,df])
	return(combined_df)

read_in_csvs().to_csv("../transactions.csv",index=False)
