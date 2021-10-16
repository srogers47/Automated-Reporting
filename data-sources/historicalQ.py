#! /usr/bin/env python3 

import pandas as pd 
import asyncio
import aiohttp
import csv
import ujson
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Main:
    """
    Get 10 years historical data from nasdaq.
    Download to excel-csv format.
    Feed desired tickers into program via 'symlist.csv'
    """
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Origin': 'https://www.nasdaq.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nasdaq.com/',
    'TE': 'Trailers',
    }
    today = datetime.today().strftime('%Y-%m-%d')  # String YYYY-MM-DD
    # Calculate date ten years ago from today.
    ten_yrs_ago = (datetime.today() - relativedelta(years=10)).strftime('%Y-%m-%d')  
    params = (
        ('assetclass', 'stocks'),
        ('fromdate', f'{ten_yrs_ago}'), # Request 10 years of financial market data
        ('limit', '9999'),
        ('todate', f'{today}'),  
    )
    symbols = pd.read_csv("symlist.csv", delimiter=",") # Read in NASDAQ 100 symbols. 

    async def get_quotes(self, session, stock_symbol): 
        """
        Get historical stock market data for fortune 100 companies.
        Pass json response to extract_data(). 
        """
        url = f'https://api.nasdaq.com/api/quote/{stock_symbol}/historical' # Use this as base url
        async with session.get(url, headers=self.headers, params=self.params) as response:
            r  = await response.json()
            print(r)
            try:
                await self.extract_data(r, stock_symbol) 
            except TypeError as t:
                print(t)
                await asyncio.sleep(30) 
                await self.extract_data(r, stock_symbol) 



    async def extract_data(self, r, stock_symbol):
        """
        Extract data from json response.
        Call store_data coroutine.
        """
        #Temp storage in memeory 
        total_records = []
        date_rows = [] 
        date = []
        close = []
        volume = []
        open_price = []
        high = []
        low = []
        temp_dict = {}
        # Extract 
        symbol = stock_symbol
        total_records = r['data']['totalRecords'] # Raises innocuous TypeError...
        # Date, Close, volume, open, high, low are located in dict of lists "rows"
        date_rows = r["data"]["tradesTable"]["rows"]   
        for x in date_rows[:]:
            date.append(x["date"])
            close.append(x["close"])
            volume.append(x["volume"])
            open_price.append(x["open"])
            high.append(x["high"])
            low.append(x["low"])
            # Append data to dict
        temp_dict.update(
                {"Symbol": symbol, 
                "Total Records": total_records,
                "Date": date,
                "Close": close,
                "Volume": volume,
                "Open": open_price,
                "High": high,
                "Low": low }
                )
        print(temp_dict) # View the blistering speed of aiohttp.
        return await self.store_data(temp_dict, stock_symbol) 


    async def store_data(self, temp_dict, stock_symbol):
        """
        Write historical market data to a csv named with corresponding stock symbal.
        Downloaded historical quotes located in 'historical/' dir.
        Note: csv local file writing is done syncronoulsy.
        Using async to write locally doesn't improve performance. 
        """
        #column_names = ["Symbol", "Total Records", "Date", "Close", "Volume", "Open", "High", "Low"]
        df = pd.DataFrame(temp_dict)
        df.to_csv(f"historical/{stock_symbol}.csv") 
        print(f"historical/{stock_symbol}.csv successfully written to local storage.") 


    async def fetch(self):
        """
        Initiate aiohttp.ClientSession.
        Generate urls to access real time quotes via nasdaq.com api entry point.
        """
        print(self.symbols) 
        async with aiohttp.ClientSession(loop=loop, json_serialize=ujson.dumps) as session:
            tasks = [self.get_quotes(session, stock_symbol) for stock_symbol in self.symbols['Symbols']]
            results = await asyncio.gather(*tasks)
            return results
        

if __name__=='__main__':
    m = Main() 
    loop = asyncio.get_event_loop() 
    results = loop.run_until_complete(m.fetch()) 
    print("Program complete") 
