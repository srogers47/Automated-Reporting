#!/bin/bash 

# ETL Pipeline calls async data sourcing programs. 
# Historical adata aggregation will take a minute or two.  
# Once complete, real time data aggregation will occur every 30 seconds.  


# Set up db with tables with scalars and automatically computed unique id.
sqlcmd -S localhost -U mssql -P password -Q "CREATE DATABASE sql-server 
  CREATE TABLE HistoricalData (ID uniqueidentifier NOT NULL 
	DEFAULT newid(),
	Symbol VARCHAR(10) NOT NULL,
	TotalRecords INT NOT NULL,
	Date DATE,
	Close DECIMAL,
	Volume DECIMAL(5,4), 
	Open DECIMAL,
	High DECIMAL,
	Low DECIMAL); 
  CREATE TABLE RealTimeData (ID uniqueidentifier NOT NULL 
	DEFAULT newid(),
	Time TIMESTAMP, 
	Symbol VARCHAR(10) NOT NULL,
	Company VARCHAR(20) NOT NULL,
	StockType VARCHAR(20) NOT NULL,
	Exchange DECIMAL,
	LastSalePrice DECIMAL,
	NetChange DECIMAL(5,4),
	PercentChange DECIMAL(5,4),
	DeltaIndicator VARCHAR(20) NOT NULL,
	Volume DECIMAL(5,4),
	PreviousClose DECIMAL,
	OpenPrice DECIMAL,
	MarketCap DECIMAL,
	MarketStatus VARCHAR(20) NOT NULL);"
  

# Run 'historicalQ.py' if the dir 'historical/' is empty.  
FILE="" 
DIR="./data-sources/historical"
if [ "$(ls -A $DIR)" ]; then 
  echo "Historical data has already been sourced" 
else 
  echo "The historical/ is empty. Running historicalQ.py..."
  ./data-sources/historicalQ.py 
  # Bulk copy historical
  bcp dbo.HISTORICAL-QUOTES in ./data-sources/historical/* -S localhost -U mssql -P password -d sql-server -c -t','
fi

# Run 'real_timeQ.py' and read csv of realtime quotes.  Then delete file.
while True 
do
  echo "Sourcing real time quotes..."
  ./data-sources/real_timeQ.py &  # Runs in background so sleeptime doesn't add kludge.
  sleep 30 
##### Data storage procedres T-SQL. #####
  # Bulk copy real time quotes csv files  
  bcp dbo.REAL-QUOTES in ./data-sources/real-time/* -S localhost -U mssql -P password -d sql-server -c -t','
# End of data storage procedures 
# Delete temp files or keep as backup? 
done 


 
