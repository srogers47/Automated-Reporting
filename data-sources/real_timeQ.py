#! /usr/bin/env python3 
import asyncio
import aiohttp
import bs4 
import pandas as pd 
import json
import datetime
import csv

class Main:
    """
    Get real time quotes on Fortune 100 companies or whatever tickers populate symlist.csv.
    Output data points to MS SQL-Server  
    """
    # Without headers and params the webpage will be unaccessable
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Origin': 'https://www.nasdaq.com',
        'Connection': 'keep-alive',
        'Referer': 'https://www.nasdaq.com/',
        'TE': 'Trailers',
    }
    params = (
        ('assetclass', 'stocks'),
    )
    #NOTE if not running in docker-container, remove project/ from path to symlist.
    symbols = pd.read_csv("project/symlist.csv", delimiter=",")

    async def get_quotes(self, session, stock_symbol) -> dict: 
        """
        Request JSON response containing from nasdaq api through url endpoint.
        Parse extracted data and format in a dictionary.
        """
        async def write_to_file():
            """
            Write quotes to temp csv file.
            """
            columns = [k for k,v in stock_data.items()] # Columns are keys of stock_data
            # NOTE project/data-sources not needed in PATH if program is run standalone (Not in docker)
            with open(f"project/data-sources/real-time/{symbol}.csv", "ab") as f: 
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                for data in stock_data:
                    writer.writerow(data)

        #print(stock_symbol)
        url = f'https://api.nasdaq.com/api/quote/{stock_symbol}/info' # generate urls with list
        # Temp storage in memeory 
        async with session.get(url, headers=self.headers, params=self.params) as response:  
            r  = await response.json()
            #Extract 
            try: # If data cannot be loaded for some reason, this try except clause will enable the program to continue running while logging errors in data extraction. 
                symbol = r['data'].get('symbol')
                company = r['data'].get('companyName')
                stock_type = r['data'].get('stockType')
                exchange = r['data'].get('exchange')
                last_sale_price = r['data']['primaryData'].get('lastSalePrice')
                net_change = r['data']['primaryData'].get('netChange')
                percent_change = r['data']['primaryData'].get('percentageChange')
                delta_indicator = r['data']['primaryData'].get('deltaIndicator')
                volume = r['data']['keyStats']['Volume'].get('value')
                prev_close = r['data']['keyStats']['PreviousClose'].get('value')
                open_price = r['data']['keyStats']['OpenPrice'].get('value')
                market_cap = r['data']['keyStats']['OpenPrice'].get('value')
                market_status = r['data'].get('marketStatus')
                try:
                    api_dev_message = r['status'].get('developerMessage') # Warnings from server side nasdaq api are worth paying attention to if raised.
                    if api_dev_message:
                        print(f"DEVELOPER MESSAGE/WARNING RAISED: {stock_symbol}") # log stock symbol that raised error 
                except TypeError: # Expecting NoneType.
                    print("No server side dev messages/warnings raised.")
                #Format data.
                stock_data = {
                    "Time":datetime.now(), "Symbol":symbol,"Company":company,"Stock Type":stock_type,"Exchange":exchange,
                    "Last Sale Price":last_sale_price, "Net Change":net_change, "Percent Change":percent_change,
                    "Delta Indicator":delta_indicator, "Volume":volume, "Previous Close":prev_close,
                    "Open Price":open_price, "Market Cap":market_cap, "Market Status":market_status
                    }
                # print(stock_data) 
                await write_to_file() 
                
            except AttributeError as a:
                print(a)
                print(stock_symbol, "Raised AttributeError...")


    async def fetch(self, loop):
        """
        Initiate aiohttp.ClientSession.
        Generate urls to access real time quotes via nasdaq.com
        """
        #print(self.symbols) 
        async with aiohttp.ClientSession(loop=loop) as session:
            tasks = [self.get_quotes(session, stock_symbol) for stock_symbol in self.symbols['Symbols']]
            results = await asyncio.gather(*tasks)
            return results


if __name__=='__main__':
    m = Main() 
    loop = asyncio.get_event_loop() 
    results = loop.run_until_complete(m.fetch(loop)) 
