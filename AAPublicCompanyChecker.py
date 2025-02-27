import requests
API_KEY = 'OBYVWEM4GDOYNIKI' # API Key for Alpha Vantage
companyName = input("Enter company name: ")
url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={companyName}&apikey={API_KEY}'
data = requests.get(url).json()

if 'bestMatches' in data:
    for match in data['bestMatches']:
        print(f"{match['2. name']} ({match['1. symbol']}))")
else:
    print('No matches found.')