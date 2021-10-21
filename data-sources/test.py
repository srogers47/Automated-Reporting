import asyncio
import aiohttp
import bs4 
import pandas as pd 
import json
from datetime import datetime
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
    symbols = pd.read_csv("./symlist.csv", delimiter=",")

    async def get_quotes(self, session, stock_symbol) -> dict: 
        """
        Request JSON response containing from nasdaq api through url endpoint.
        Parse extracted data and format in a dictionary.
        """
        async def write_to_file():
            """
            Write quotes to temp csv file.
            """
            #columns = dict(stock_data).keys() # Columns are keys of stock_data
            # NOTE project/data-sources not needed in PATH if program is run standalone (Not in docker)
            # Use open to append data rather than pandas to_csv to create csv every 30 seonds 
           # with open(f"./real-time/{symbol}.csv", "a") as f: 
           #     writer = csv.writer(f)
           #     writer.writerow(stock_data)
            df = pd.DataFrame(stock_data)   
            df.to_csv(f"./real-time/{symbol}.csv", encoding='utf-8') # Write to csv. NOTE: Can't append



        #print(stock_symbol)
        url = f'https://api.nasdaq.com/api/quote/{stock_symbol}/info' # generate urls with list
        # Temp storage in memeory 
        async with session.get(url, headers=self.headers, params=self.params) as response:  
            r_serialized =  await response.json()
            # Iterate over serialized json.  Insert into dict for index extraction
            r = r_serialized 

            
            print(r) # Debugging 
            #Extract 
            try: # If data cannot be loaded for some reason, this try except clause will enable the program to continue running while logging errors in data extraction. 
                symbol =  r['data']['symbol']
                company =  r['data']['companyName'].split()[0][:-1] # Drop stock type and trailing comma 
                stock_type =  r['data']['stockType']
                exchange = r['data']['exchange']
                last_sale_price = r['data']['primaryData']['lastSalePrice']
                net_change = r['data']['primaryData']['netChange']
                percent_change =  r['data']['primaryData']['percentageChange']
                delta_indicator =  r['data']['primaryData']['deltaIndicator']
                market_status =  r['data']['marketStatus']
                print("STOCKS CAN BE INDEXED", symbol, company, exchange, market_status, "...")
                try:
                    api_dev_message = r['status']['developerMessage'] # Warnings from server side nasdaq api are worth paying attention to if raised.
                    if api_dev_message:
                        print(f"DEVELOPER MESSAGE/WARNING RAISED: {stock_symbol}") # log stock symbol that raised error 
                except TypeError: # Expecting NoneType.
                    print("No server side dev messages/warnings raised.")
                #Format data.
                print('STOCKDATA')
                stock_data = {
                    "Time":[datetime.now()], "Symbol":[symbol],"Company":[company],"Stock Type":[stock_type],"Exchange":[exchange],
                    "Last Sale Price":[last_sale_price], "Net Change":[net_change], "Percent Change":[percent_change],
                    "Delta Indicator":[delta_indicator], "Market Status":[market_status]
                    }
                # print(stock_data) 
                await write_to_file() 
                
            except TypeError as a:
                print(a)
                print(stock_symbol, "is empty. Most likely a networking error...")


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

