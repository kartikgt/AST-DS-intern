import requests as re
import pandas as pd
from io import StringIO
import sqlite3
import utils


class SourceDataJob:
    # This class fetches the apr_drg and mdc_drg data from urls and creates dataframes from them
    def __init__(self, apr_drg_url, mdc_url, mdc_descriptors_url):
        self.apr_drg_url = apr_drg_url
        self.mdc_url = mdc_url
        self.mdc_descriptors_url = mdc_descriptors_url
        self.apr_drg_df = None
        self.mdc_drg_df = None

    def get_apr_response(self):
        """Creating the apr_drg dataframe"""
        response = re.get(self.apr_drg_url)
        if response.status_code != 200:
            raise Exception(f"Error downloading apr-drg table from {self.apr_drg_url}")
        self.apr_drg_df = pd.read_csv(StringIO(response.text), delimiter="|")
        # DRG is a billing code that should be 3 characters wide and be left padded with zeros
        self.apr_drg_df.DRG = self.apr_drg_df.DRG.astype(str).str.pad(3, fillchar="0")
        self.apr_drg_df.columns = [n.lower() for n in self.apr_drg_df.columns]

    def clean_mdc_drg_row(self, row):
        """cleaning the html text to make a list of values

        Args:
            row (_type_): _description_

        Returns:
            _type_: _description_
        """
        row = row.strip("\\r\\n")
        parts = row.split(",", 3)
        if len(parts) < 3:
            return ""
        formatted_row = '"' + '","'.join(parts) + '"'
        return formatted_row

    def get_mdc_descriptions(self):
        """Fetching the mdc descriptions"""
        descriptions = str(re.get(self.mdc_descriptors_url).content)
        # reformat descriptions into csv
        csved_descriptions = "\n".join(
            [
                '"' + '","'.join(d.strip().split(" = ")) + '"'
                for d in descriptions.split("\\r\\n") if "=" in d]
        )
        csved_descriptions = '"MDC","description"\n' + csved_descriptions
        descrption_io = StringIO(csved_descriptions)
        df = pd.read_csv(descrption_io)
        return df

    def get_mdc_drg(self):
        """Creating the mdc_drg dataframe"""
        # Retrieve and format table from the raw html table
        drg_defs = str(re.get(self.mdc_url).content)
        table_to_end = drg_defs.split(
            """<table class=appnda summary="Appendix A. Table for formatting only">""")[1]
        table = table_to_end.split("</table>")[0]
        raw_rows = table.split("<tr><td>")
        cleaned_rows = map(self.clean_mdc_drg_row, raw_rows)
        # If the cleaned row is empty, result of clean_row has zero length. Drop them.
        rows_with_length = list(filter(lambda s: len(s) > 0, cleaned_rows))
        csved_rows = StringIO("\n".join(rows_with_length))
        df = pd.read_csv(csved_rows, header=None)

        # These column headers were provided by the researcher.
        df.columns = ["DRG", "MDC", "Type", "Long Description"]

        mdc_descriptions = self.get_mdc_descriptions()

        # MDC should be 3 characters wide left padded with zeros
        # If it is null, then it needs to be blank
        df["mdc_key"] = df["MDC"].map(
            lambda c: "" if len(c.strip()) == 0 else "0" + c[-2:])

        # Adding the descriptions to the table
        df = df.merge(mdc_descriptions, left_on=[
            "mdc_key"], right_on=["MDC"], how="left")
        df.drop(columns=["mdc_key", "MDC_y"], inplace=True)
        df.rename(columns={"MDC_x": "MDC"}, inplace=True)
        df.columns = [n.lower() for n in df.columns]
        self.mdc_drg_df = df


class SQLCon:
    """Class to connect to database and send query"""
    def __init__(self, db):
        self.con = sqlite3.connect(db)

    def make_df(self, apr_drg_df, mdc_drg_df):
        apr_drg_df.to_sql("apr_drg", self.con, if_exists="replace")
        mdc_drg_df.to_sql("drg_mdc", self.con, if_exists="replace")

    def send_query(self):
        path = 'src/merge_query.sql'
        fd = open(path, 'r')
        sql_file = fd.read()
        fd.close()
        cur = self.con.cursor()
        cur.executescript(sql_file)

config = utils.load_config(config_file_name="config.yaml") # Loading config file

# Creating apr and drg dataframes by instantiating the SourceDataJob class
drg_df = SourceDataJob(config['apr_drg_url'], config['mdc_url'], config['mdc_descriptors_url'])
drg_df.get_apr_response()
drg_df.get_mdc_drg()

# Connecting to db and executing query
sqlcon = SQLCon(config['db'])
sqlcon.make_df(drg_df.apr_drg_df, drg_df.mdc_drg_df)
sqlcon.send_query()

