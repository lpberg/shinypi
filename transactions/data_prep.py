import pandas as pd
import os

def read_in_csvs():
	combined_df = pd.DataFrame()
	for subdir, dirs, files in os.walk('./'):
		for csv_file in files:
			if csv_file.endswith(".csv"):
				df = pd.read_csv(csv_file)
				combined_df = pd.concat([combined_df,df])
#	combined_df = combined_df.loc[combined_df["Account"].isin(['Visa Signature Rewards - Ending in 2163', 'Fidelity Rewards Visa Signature Card - Ending in 2163'])]
	combined_df = combined_df.loc[combined_df["Account"].isin([account for account in combined_df["Account"].unique() if "Visa" in account])]
	return(combined_df)

read_in_csvs().to_csv("../transactions.csv",index=False)
