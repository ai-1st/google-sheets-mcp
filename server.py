"""GCP utils to write data out to gsheets"""
import gspread
import time

# Authenticate and access the Google Sheets API
client = gspread.service_account(filename="google_creds.json")

def get_column_name(n):
    """A is 1, B is 2, AA is 27 etc."""
    return (
        "" if n == 0 else get_column_name((n - 1) // 26) + chr((n - 1) % 26 + ord("A"))
    )


def backoff(foo):
    def bar(*args, **kwargs):
        last_exception = None
        for i in range(6):
            try:
                return foo(*args, **kwargs)
            except gspread.exceptions.APIError as e:
                last_exception = e
                time.sleep(2**i)
        raise Exception("Tried google 6 times.", last_exception)

    return bar


@backoff
def create_spreadsheet(ss_name):
    """Creates a new spreadsheet with the specified name.
    Parameters:
    ss_name: the name of the spreadsheet to be created
    """
    spreadsheet = client.create(title=ss_name)
    return spreadsheet.id


@backoff
def write_list_to_spreadsheet(ls, ws):
    """Writes a list to the specified worksheet of the specified spreadsheet.
    Assumes that the spreadsheet and worksheet already exist. Existing data is cleared.
    Parameters:
    ls: the list to be written
    ws: the worksheet object
    """
    if not ls:
        return
    a1_notation = f"A:{get_column_name(len(ls[0]))}"
    ws.batch_clear([a1_notation])
    # print(f"Writing {a1_notation} for {len(ls[0])} columns and {len(ls)} rows")
    ws.update(values=ls, range_name=a1_notation, value_input_option="USER_ENTERED")


