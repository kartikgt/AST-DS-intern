import requests as re
import pandas as pd
from io import StringIO

# add comments
# add skeleton class/module

###########################
# Get APC data (description of certain billing codes that are important)
###########################

apr_drg_url = "https://apps.3mhis.com/docs/Groupers/All_Patient_Refined_DRG/apr400_DRG_descriptions.txt"
response = re.get(apr_drg_url)
if response.status_code != 200:
    raise Exception(f"Error downloading apr-drg table from {apr_drg_url}")
apr_drg_df = pd.read_csv(StringIO(response.text), delimiter="|")
# DRG is a billing code that should be 3 characters wide and be left padded with zeros
apr_drg_df.DRG = apr_drg_df.DRG.astype(str).str.pad(3, fillchar="0")
apr_drg_df.columns = [n.lower() for n in apr_drg_df.columns]



###########################
# get descriptions for certain drg codes
###########################

def get_mdc_drg():
    # Retrieve and format table from the raw html table
    drg_defs = str(re.get(
        "https://www.cms.gov/icd10m/version39.1-fullcode-cms/fullcode_cms/P0377.html").content)
    table_to_end = drg_defs.split(
        """<table class=appnda summary="Appendix A. Table for formatting only">""")[1]
    table = table_to_end.split("</table>")[0]
    raw_rows = table.split("<tr><td>")
    cleaned_rows = map(clean_mdc_drg_row, raw_rows)
    # If the cleaned row is empty, it has zero length, need to drop them.
    rows_with_length = list(filter(lambda s: len(s) > 0, cleaned_rows))
    csved_rows = StringIO("\n".join(rows_with_length))
    df = pd.read_csv(csved_rows, header=None)
    df.columns = ["DRG", "MDC", "Type", "Long Description"]

    mdc_descriptions = get_mdc_descriptions()

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
    return df


def clean_mdc_drg_row(row):
    row = row.strip("\\r\\n")
    parts = row.split(",", 3)
    if len(parts) < 3:
        return ""
    formatted_row = '"' + '","'.join(parts) + '"'
    return formatted_row


def get_mdc_descriptions():
    descriptions = str(re.get(
        "https://resdac.org/sites/datadocumentation.resdac.org/files/Major%20Diagnostic%20Category.txt").content)
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

mdc_drg_df = get_mdc_drg()

# In the future, we want to use a database in the cloud, but we're using sqlite for development
# right now
import sqlite3
con = sqlite3.connect("tutorial.db")

apr_drg_df.to_sql("apr_drg", con, if_exists="replace")
mdc_drg_df.to_sql("drg_mdc", con, if_exists="replace")

merge_query = """
CREATE TABLE enriched_billing_codes AS
SELECT 
    billing_code,
    drg_mdc.mdc as drg_mdc,
    drg_mdc.type as drg_mdc_type,
    drg_mdc.mdc_description as mdc_description,
    apr_drg.mdc as apr_mdc,
    apr_drg.type as apr_type
FROM (
    SELECT DISTINCT billing_code, negotiation_arrangement
    FROM innetwork
    WHERE 
        negotiation_arrangement = 'ffs'
) as in_network_codes
LEFT JOIN (
    SELECT 
        drg, 
        mdc, 
        "type", 
        "long description" as mdc_description
    FROM drg_mdc
) as drg_mdc
ON in_network_codes.billing_code = drg_mdc.drg
LEFT JOIN (
    SELECT drg, mdc, "type"
    FROM apr_drg 
) as apr_drg
ON in_network_codes.billing_code = apr_drg.drg
"""
cur = con.cursor()
cur.executescript(merge_query)

query = "select * from apr_drg"

cur.executescript(query)
