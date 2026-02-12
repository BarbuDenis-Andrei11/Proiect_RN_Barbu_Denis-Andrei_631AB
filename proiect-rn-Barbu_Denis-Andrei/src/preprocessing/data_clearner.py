# Fisier: src/preprocessing/data_cleaner.py
import pandas as pd

def clean_dataframe(df):
    d = df[['Close']].copy()
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    if d.index.tz is not None:
        d.index = d.index.tz_localize(None)
    d['Close'] = pd.to_numeric(d['Close'], errors='coerce')
    d.dropna(inplace=True)
    return d