import yfinance as yfi
import sys
import sqlite3
from time import time, sleep

class DatabaseAPI():

  def __init__(self, db="./StockData.db"):
    self.connection = sqlite3.connect(db)
    self.cursor = connection.cursor()

    self.cursor.execute(
      f"CREATE TABLE IF NOT EXISTS CollectedStockData ("
        f"symbol TEXT, "
        f"time INTEGER, "
        f"price REAL, "
        f"volume REAL, "
        f"open REAL, "
        f"close REAL, "
        f"high REAL, "
        f"low REAL"
      f")"
    )

    self.connection.commit()


def DataStreamConstructor(SymbolFile):
  """ The data stream consists of a steady influx of _new_ stock data for symbols defined
  by the SymbolFile.
  
  The SymbolFile consists of a single stock symbol per line.  To properly read input from
  the file to the constructor each line is stripped of newline characters and given a tailing
  whitespace character.  These formatted strings are then read from the TickerList to the 
  TickerString, which in turn has it's trailing whitespace stripped.
  
  Essentially, we have to take: "MSFT\nGOOG\n" and convert it to "MSFT GOOG" to prepare it for
  use with the yFinance api.
   """
  database = DatabaseAPI()

  while True:

    # 'Acceptable' multi-input for the yfi.Ticker object.
    TickerString = ""

    # 'Pythonic' record of individual inputs to yfi.Ticker.
    TickerList = []

    # Format and keep track of the input. 
    """ This could be altered with the Alpaca API... """
    """ Open an issue and track the changes. """
    with open(SymbolFile, "r") as symbols:
        for symbol in symbols.readlines():
          symbol = str(symbol).strip().upper()
          TickerString += f"{symbol} "
          TickerList.append(symbol)

    # The API call/response object;
    # input formatted as: "MSFT GOOG AAPL"
    ticker = yfi.Ticker(f"{TickerString.strip()}")

    

    # The ticker.tickers object possesses methods related
    # to the ticker symbols passed by TickerString.
    # Ex ticker.tickers.MSFT contains the data returned for
    # the MSFT symbol.

    # In order to be able to use strings to compare against 
    # the ticker objects, we use the dir() function to list
    # the methods of ticker.tickers and call it SYMBOLS.
    SYMBOLS = list(dir(ticker.tickers))

    # Take every tracked stock symbol in the TickerList;.
    for TickerSymbol in TickerList:
      # Compare them to every method of ticker.tickers;
      if TickerSymbol in SYMBOLS:
        # If they match, call the actual object and name it quote.
        # quote = yfi.Ticker.tickers.MSFT.info
        quote = getattr(ticker.tickers, TickerSymbol).info
  
        # Upon definition of a successful quote we can begin
        # collecting datapoints relevant to our query.

        # To keep it simple, for now we'll observe candles.

        # We take the current price along with the high, low,
        # open, close, and volume.

        # Along with the target data, we also track the stock
        # symbol and the unix timestamp plus our source.
        _symbol = str(quote["symbol"])
        _time = round(time() * 1000)
        _price = float(quote["regularMarketPrice"])
        _volume = float(quote["volume"])
        _open = float(quote["open"])
        _close = float(quote["previousClose"])
        _high = float(quote["dayHigh"])
        _low = float(quote["dayLow"])

        database.cursor\
                .execute(
                          f"INSERT INTO CollectedStockData ("
                            f"symbol,time,price,volume,"
                            f"open,close,high,low"
                          f") "
                          f"VALUES( "
                            f"?, ?, ?, ?, ?, ?, ?, ? "
                          f")",
                          ( _symbol, _time, _price, _volume,
                           _open, _close, _high, _low, )
                        ); database.connection.commit()
    sleep(3)


def AddSymbol(SymbolFile, symbol):
  """ Append a new symbol to the SymbolFile. """
  try:

    with open(SymbolFile, "a") as symbols:
      symbols.write(f"\n{symbol.upper()}")

    return True

  except:
    return False


def DelSymbol(SymbolFile, symbol):
  """ Remove a symbol from the SymbolFile. """
  try:

    with open(SymbolFile, "r") as symbols:
      ExistingSymbols = symbols.readlines()

    for ExistingSymbol in ExistingSymbols:
      if symbol.upper() == ExistingSymbol.strip():
        SymbolFile.remove(existingSymbol)

    with open(SymbolFile, "w") as symbols:
      for KeptSymbol in ExistingSymbols:
        symbols.write(f"\n{KeptSymbol.upper().strip()}")

    return True

  except:
    return False
