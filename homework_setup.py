# You can ignore this file. It is just for Mathematica employees to build the sample database.

import sqlite3
import pandas as pd

def load_rates_data(conn, rates_csv_path:str):
        df = pd.read_csv(rates_csv_path)
        df = df[["negotiation_arrangement","data_source_id","billing_code"]]
        df.to_sql('innetwork', conn, if_exists='replace', index=False)

if __name__ == '__main__':
    conn = sqlite3.connect('tutorial.db')
    load_rates_data(conn, r"C:\Users\mrufsvold\Downloads\9c095702-1901-455a-9f02-716134cb4963.csv")
