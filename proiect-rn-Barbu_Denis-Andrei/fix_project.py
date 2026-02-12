import os

# Definim structura si continutul fisierelor lipsa
files = {
    "src/preprocessing/__init__.py": "",
    
    "src/preprocessing/data_cleaner.py": """
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
""",

    "src/preprocessing/feature_engineering.py": """
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
""",

    "src/preprocessing/data_splitter.py": """
def split_time_series_data(X, y, dates, train_ratio=0.9):
    split_idx = int(len(X) * train_ratio)
    return X[:split_idx], X[split_idx:], y[:split_idx], y[split_idx:], dates[split_idx:]
""",

    "src/data_acquisition/__init__.py": "",
    "src/neural_network/__init__.py": "",
    "src/app/__init__.py": "",
}

def create_structure():
    print(">>> REPARARE STRUCTURA PROIECT...")
    base_dir = os.getcwd()
    
    for path, content in files.items():
        full_path = os.path.join(base_dir, path)
        directory = os.path.dirname(full_path)
        
        # 1. Cream folderul daca nu exista
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   [+] Creat folder: {directory}")
            
        # 2. Cream fisierul (suprascriem pentru a fi siguri)
        with open(full_path, "w", encoding='utf-8') as f:
            f.write(content.strip())
        print(f"   [OK] Generat fisier: {path}")

    print("\n>>> GATA! Structura este corecta.")
    print(">>> Acum poti rula 'python start.py'")

if __name__ == "__main__":
    create_structure()