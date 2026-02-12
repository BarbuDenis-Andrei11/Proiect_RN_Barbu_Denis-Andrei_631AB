import yfinance as yf
import pandas as pd
import os

# 1. Configurare Simboluri
ticker = "TSLA"
market = "^GSPC"

print(f"Generare date pentru structura proiectului ({ticker})...")

# Asiguram ca folderele exista
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/generated", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/train", exist_ok=True)
os.makedirs("data/test", exist_ok=True)

# --- PASUL 1: RAW DATA ---
print("1. Salvare Date Brute (raw)...")
df_ticker = yf.download(ticker, period="2y", progress=False)
df_market = yf.download(market, period="2y", progress=False)

# Curatare header pentru CSV
def clean_cols(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

df_ticker = clean_cols(df_ticker)
df_market = clean_cols(df_market)

df_ticker.to_csv(f"data/raw/{ticker}_raw.csv")
df_market.to_csv("data/raw/SP500_raw.csv")

# --- PASUL 2: GENERATED DATA (Feature Engineering) ---
print("2. Salvare Date Generate (generated)...")
# Combinam datele (Codul tau de Feature Engineering)
market_df_clean = df_market[['Close']].rename(columns={'Close': 'Market_Close'})
df_merged = df_ticker[['Close']].join(market_df_clean, how='inner')

df_shifts = df_merged.copy()
n = 3
# Generam Lags
for i in range(1, n + 1):
    df_shifts[f'lag_{i}'] = df_shifts['Close'].shift(i)
for i in range(1, n + 1):
    df_shifts[f'market_lag_{i}'] = df_shifts['Market_Close'].shift(i)

# Salvam datasetul generat (chiar si cu NaN-uri la inceput, ca sa se vada procesul)
df_shifts.to_csv("data/generated/dataset_full_features.csv")

# --- PASUL 3: PROCESSED DATA (Clean) ---
print("3. Salvare Date Procesate (processed)...")
df_clean = df_shifts.dropna()
df_clean.to_csv("data/processed/final_clean_data.csv")

# --- PASUL 4: SPLIT TRAIN/TEST ---
print("4. Salvare Train/Test split...")
split_idx = int(len(df_clean) * 0.9)

train_df = df_clean.iloc[:split_idx]
test_df = df_clean.iloc[split_idx:]

train_df.to_csv("data/train/train_set.csv")
test_df.to_csv("data/test/test_set.csv")

print("\n[SUCCES] Toate fisierele CSV au fost generate in folderul 'data/'!")