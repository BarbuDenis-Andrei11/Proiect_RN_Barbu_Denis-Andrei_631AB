import yfinance as yf
import pandas as pd
import sys

def download_data(ticker_symbol, period="2y"):
    """
    Descarca datele pentru ticker-ul specificat si pentru piata (S&P 500).
    """
    market_symbol = "^GSPC"
    print(f"--- [Data Acquisition] Descarcare date pentru {ticker_symbol} si {market_symbol} ---")
    
    try:
        df_ticker = yf.download(ticker_symbol, period=period, progress=False)
        df_market = yf.download(market_symbol, period=period, progress=False)

        if df_ticker.empty:
            raise ValueError(f"Nu s-au gasit date pentru simbolul: {ticker_symbol}")

        return df_ticker, df_market

    except Exception as e:
        print(f"Eroare critica la descarcare: {e}")
        return None, None