import yfinance as yf
from fuzzywuzzy import fuzz
import requests
import json

def get_company_ticker(company_name):
    """
    Search for the company's stock ticker using Yahoo Finance API.
    """
    try:
        # Replace spaces with '+' for the search query
        search_query = company_name.replace(" ", "+")
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()

        # Check if there are any results
        if data['quotes']:
            for result in data['quotes']:
                # Use fuzzy matching to compare company name with the result
                if fuzz.ratio(company_name.lower(), result['shortname'].lower()) > 50:  # similarity thresholdFrederick R. Ueland, M.D.
                    return result['symbol']
        return None
    except Exception as e:
        print(f"Error searching for ticker: {e}")
        return None

def is_publicly_traded(company_name):
    """
    Check if the company is publicly traded by fetching stock information.
    """
    try:
        # Get the ticker symbol for the company
        ticker_symbol = get_company_ticker(company_name)
        
        if ticker_symbol:
            # Fetch stock data using yfinance
            stock = yf.Ticker(ticker_symbol)
            stock_info = stock.info

            # Check if the stock info contains valid data
            if stock_info and 'shortName' in stock_info and stock_info['shortName']:
                print(f"\nCompany: {stock_info['shortName']}")
                print(f"Ticker: {ticker_symbol}")
                print(f"Exchange: {stock_info.get('exchange', 'N/A')}")
                print(f"Sector: {stock_info.get('sector', 'N/A')}")
                print(f"Market Cap: {stock_info.get('marketCap', 'N/A')}")
                return True
            else:
                print(f"\nNo valid stock information found for {company_name}.")
                return False
        else:
            print(f"\nCould not find a ticker symbol for {company_name}.")
            return False
    except Exception as e:
        print(f"\nError checking company: {e}")
        return False

def main():
    print("Check if a company is publicly traded")
    print("-------------------------------------")
    
    while True:
        company_name = input("\nEnter the company name (or 'quit' to exit): ").strip()
        
        if company_name.lower() == 'quit':
            print("Exiting...")
            break
        
        if not company_name:
            print("Please enter a valid company name.")
            continue
        
        print(f"\nChecking if {company_name} is publicly traded...")
        
        if is_publicly_traded(company_name):
            print(f"\n{company_name} is a publicly traded company.")
        else:
            print(f"\n{company_name} is not a publicly traded company or could not be found.")

if __name__ == "__main__":
    main()