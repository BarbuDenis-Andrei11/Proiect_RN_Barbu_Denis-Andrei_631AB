import pandas as pd

def create_features(ticker_df, market_df, n=3):
    market_clean = market_df[['Close']].rename(columns={'Close': 'Market_Close'})
    df = ticker_df[['Close']].join(market_clean, how='inner')
    df_shifts = df.copy()
    feature_cols = []
    
    for i in range(1, n + 1):
        col_name = f'lag_{i}'
        df_shifts[col_name] = df_shifts['Close'].shift(i)
        feature_cols.append(col_name)
    
    for i in range(1, n + 1):
        col_name = f'market_lag_{i}'
        df_shifts[col_name] = df_shifts['Market_Close'].shift(i)
        feature_cols.append(col_name)

    df_shifts.dropna(inplace=True)
    X = df_shifts[feature_cols].values
    y = df_shifts['Close'].values
    dates = df_shifts.index
    return dates, X, y, df_shifts