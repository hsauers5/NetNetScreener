import requests, json
import time

TICKER = ""


def set_ticker(ticker="AAPL"):
    global TICKER
    TICKER = ticker
    get_balance_sheet()


user_agent = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-en) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4"
headers = {
    'User-Agent': user_agent,
    'Accept': 'application/json',
    'authority': 'seekingalpha.com',
    'referer': 'https://seekingalpha.com/symbol',
    'x-requested-with': 'XMLHttpRequest'
}

api_url = "https://seekingalpha.com/symbol/{TICKER}/financials-data?period_type=annual&statement_type=balance-sheet&order_type=latest_right&is_pro=false"
iex_url = "https://cloud.iexapis.com/stable/stock/{TICKER}/stats/marketcap?token=pk_b2fd87d0a58347e39821f77f9a599b80"

BALANCE_SHEET = {}


def get_balance_sheet():
    global BALANCE_SHEET
    BALANCE_SHEET = get_balance_sheet_keys(TICKER)


def get_balance_sheet_keys(ticker):  # TTPH
    balance_sheet = {}
    url = api_url.replace("{TICKER}", ticker.upper())
    response = ""

    try:
        response = requests.get(url, headers=headers).content.decode("utf-8")
    except:
        time.sleep(0.5)
        response = requests.get(url, headers=headers).content.decode("utf-8")

    bs = json.loads(response)
    try:
        bs = bs['data']
    except:
        print(bs)

    for item in bs:
        for entry in item:
            key = entry[0]['value']
            balance_sheet[key] = float(
                entry[-1]['value'].replace(",", "").replace("-", "0").replace("(", "-").replace(")", "").replace("$",
                                                                                                                 ""))
    return balance_sheet


def get_current_assets():
    if 'Total Current Assets' in BALANCE_SHEET:
        return BALANCE_SHEET['Total Current Assets'] * 1000000
    else:
        return 0


def get_cash():
    if 'Total Cash & ST Investments' in BALANCE_SHEET:
        return BALANCE_SHEET['Total Cash & ST Investments'] * 1000000
    else:
        return 0


def get_recievables():
    if 'Total Receivables' in BALANCE_SHEET:
        return BALANCE_SHEET['Total Receivables'] * 1000000
    else:
        return 0


def get_inventory():
    if 'Inventory' in BALANCE_SHEET:
        return BALANCE_SHEET['Inventory'] * 1000000
    else:
        return 0


def get_total_liabilities():
    if 'Total Liabilities' in BALANCE_SHEET:
        return BALANCE_SHEET['Total Liabilities'] * 1000000
    else:
        return 0


def get_market_cap():
    url = iex_url.replace("{TICKER}", TICKER)
    response = requests.get(url).content.decode("UTF-8")
    return float(response)


def calculate_ncav():
    return get_current_assets() - get_total_liabilities()


def calculate_nnwc():
    return get_cash() + 0.75 * get_recievables() + 0.5 * get_inventory() - get_total_liabilities()


def get_price_to_ncav():
    return get_market_cap() / calculate_ncav()


def get_price_to_nnwc():
    return get_market_cap() / calculate_nnwc()


# tickers = ["ISEE", "NLNK", "NVIV", "TTPH", "OPTT", "SRRA", "ARPO", "NTEC", "TNXP", "PRTO", "CYCC", "RMED", "CSS", "SPRT"]

# tickers = ['TENX', 'NTEC', 'ARPO', 'PRTO', 'MRSN', 'TNXP', 'NVIV', 'APTX', 'ALT', 'NVFY', 'AQXP', 'ISEE', 'CHFS', 'TTPH', 'NLNK', 'SRRA', 'OPTT', 'CYCC', 'RMED']

# tickers = ['RELL', 'ACTG', 'FLXS']


def find_targets(tickers=["NVFY"]):
    net_net_targets = []
    for ticker in tickers:
        try:
            print(ticker + ": ")
            set_ticker(ticker)
            time.sleep(1)
            p_ncav = get_price_to_ncav()
            p_nnwc = get_price_to_nnwc()
            print("P/NCAV: " + str(p_ncav))
            print("P/NNWC: " + str(p_nnwc))
            print()
            if 0 < p_ncav < 0.66 or 0 < p_nnwc < 1:
                net_net_targets.append(ticker)
        except Exception:
            print("Not found \n")

    print("Net-Nets Found: \n" + str(net_net_targets))


def search_from_file(filename="stocks.csv"):
    ticker_list = []
    with open(filename, "r+") as f:
        for line in f:
            ticker_list.append(line.strip())

    find_targets(tickers=ticker_list)


# find_targets(tickers=tickers)
search_from_file(filename="stocks.csv")
