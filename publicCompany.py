import yfinance as yf
import requests
from bs4 import BeautifulSoup
import re
import time # For sleeping between requests
import math


#Maybe need to sleep for a few seconds to avoid being blocked by Yahoo Finance
def get_ticker_and_public_status(company_name):
    try:
        # 1.  Try a direct yfinance lookup (most reliable for known tickers/names)
        ticker_obj = yf.Ticker(company_name)
        info = ticker_obj.info  # Accessing .info can raise an exception

        # Check for valid info and a reasonable market cap (to avoid penny stocks/weird results)
        if "currentPrice" in info and info.get("marketCap") is not None:
            return True, company_name, None  # Assume input was the ticker

        # 2. Search on Yahoo Finance (handles company names better)
        search_url = f"https://finance.yahoo.com/lookup?s={company_name}"
        response = requests.get(search_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first ticker symbol result.  Yahoo Finance's structure can change,
        # so this needs to be robust.  We look for a table, then rows, then cells.
        table = soup.find('table')
        if not table:
            return False, None, "No results found on Yahoo Finance."

        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells:
                # The ticker is usually in the first cell, company name in the second.
                ticker_text = cells[0].text.strip()
                company_name_text = cells[1].text.strip()

                # Basic validation – check for a ticker-like pattern (mostly letters, maybe some periods/dashes)
                if re.match(r"^[A-Z.\-^]+$", ticker_text):
                  # Double check with yfinance
                  try:
                    ticker_object = yf.Ticker(ticker_text)
                    test_info = ticker_object.info
                    if "currentPrice" in test_info and test_info.get("marketCap") is not None:
                      return True, ticker_text, None
                  except:
                    continue #try next result
        return False, None, "No public ticker found on Yahoo Finance."


    except requests.exceptions.RequestException as e:
        return None, None, f"Network error: {e}"
    except (KeyError, ValueError, TypeError) as e:
        # yfinance sometimes throws KeyErrors if data is missing, or ValueErrors.
        return None, None, f"Error retrieving data from yfinance: {e} (Possibly not a public company or invalid ticker)"
    except Exception as e:
        return None, None, f"An unexpected error occurred: {e}"



def main():
    """Gets company name input from the user and prints the results."""

    while True:
        company_name = input("Enter the company name (or 'quit' to exit): ").strip()
        if company_name.lower() == 'quit':
            break
        
        random = math.floor(1, 5)
        time.sleep(random) # Sleep for a random amount of time (1-5 seconds)
        is_public, ticker, error_message = get_ticker_and_public_status(company_name)

        if is_public is True:
            print(f"'{company_name}' appears to be a public company.")
            print(f"Ticker symbol: {ticker}")
        elif is_public is False:
            if error_message:
                print(error_message)
            else:
                print(f"'{company_name}' does not appear to be a publicly traded company.")
        else:  # is_public is None (error case)
            print(f"Error: {error_message}")
        print("-" * 30)

if __name__ == "__main__":
    main()