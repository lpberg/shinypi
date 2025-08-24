import pandas as pd
import os

def combine_csvs():
	combined_df = pd.DataFrame()
	for subdir, dirs, files in os.walk('./'):
		for file in files:
			if file.endswith(".csv"):
				df = pd.read_csv(file)
				combined_df = pd.concat([combined_df,df])
	print(f"{os.path.basename(__file__)}: Transaction files read complete.")
	print(f"Min date: {combined_df['Date'].min()}\nMax date: {combined_df['Date'].max()}")
	return(combined_df)

combine_csvs().to_csv("../transactions.csv",index=False)
