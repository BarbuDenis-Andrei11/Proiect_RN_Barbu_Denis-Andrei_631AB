import pandas as pd

def clean_dataframe(df):
    d = df[['Close']].copy()
    # Tratare MultiIndex
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    # Eliminare Timezone
    if d.index.tz is not None:
        d.index = d.index.tz_localize(None)
    # Conversie numerica
    d['Close'] = pd.to_numeric(d['Close'], errors='coerce')
    d.dropna(inplace=True)
    return d