import yfinance as yf
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import mean_absolute_error
import sys

# ==============================================================================
# 0. FUNCTII AJUTATOARE
# ==============================================================================
def prepare_data_with_market(ticker_df, market_df, n=3):
    """ Combina datele actiunii cu datele pietei (S&P 500) """
    market_df = market_df[['Close']].rename(columns={'Close': 'Market_Close'})
    df = ticker_df[['Close']].join(market_df, how='inner')
    
    df_shifts = df.copy()
    feature_cols = []
    
    # Lag-uri Actiune si Piata
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

# ==============================================================================
# 1. DESCARCARE DATE
# ==============================================================================
print("\n=============================================")
print("  ROBOT DE TRADING AI - COMPLET")
print("=============================================")
ticker_symbol = input("Introdu simbolul (ex: TSLA, AAPL, BTC-USD): ").strip().upper()
market_symbol = "^GSPC" 

try:
    print(f"\n1. Se descarca datele pentru {ticker_symbol} si Piata...")
    df_ticker = yf.download(ticker_symbol, period="2y", progress=False)
    df_market = yf.download(market_symbol, period="2y", progress=False)

    if df_ticker.empty:
        print("Eroare: Nu s-au gasit date.")
        sys.exit(1)

    # Curatare
    def clean_df(d):
        d = d[['Close']].copy()
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        d.index = d.index.tz_localize(None)
        d['Close'] = pd.to_numeric(d['Close'], errors='coerce')
        d.dropna(inplace=True)
        return d

    df_ticker = clean_df(df_ticker)
    df_market = clean_df(df_market)
    print(f"   > Date descarcate.")

except Exception as e:
    print(f"Eroare critica: {e}")
    sys.exit(1)

# ==============================================================================
# 2. OPTIMIZARE MODEL
# ==============================================================================
n = 3
dates, X, y, full_df = prepare_data_with_market(df_ticker, df_market, n)

split_idx = int(len(X) * 0.9)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]
dates_test = dates[split_idx:]

print("\n2. Se optimizeaza 'creierul' modelului (Grid Search)...")
param_dist = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5]
}
rf = RandomForestRegressor(random_state=42)
random_search = RandomizedSearchCV(estimator=rf, param_distributions=param_dist, 
                                   n_iter=5, cv=3, verbose=0, random_state=42, n_jobs=1)
random_search.fit(X_train, y_train)
best_model = random_search.best_estimator_

# Predictii pe setul de test
predictions_test = best_model.predict(X_test)
mae = mean_absolute_error(y_test, predictions_test)
print(f"   > Eroare Medie Absoluta (MAE): {mae:.2f} $")

# ==============================================================================
# 3. PREDICTIE "MAINE" SI ANALIZA TREND
# ==============================================================================
ticker_vals = df_ticker['Close'].tail(n).values[::-1]
market_vals = df_market['Close'].tail(n).values[::-1]
current_features = []
for v in ticker_vals: current_features.append(v)
for v in market_vals: current_features.append(v)

predicted_price = best_model.predict([current_features])[0]
last_real_price = df_ticker['Close'].iloc[-1]

# Calcul diferenta si procent
diff = predicted_price - last_real_price
pct_change = (diff / last_real_price) * 100

# Determinare directie
trend_msg = ""
if diff > 0:
    trend_msg = f"CRESTERE 📈 (+{pct_change:.2f}%)"
elif diff < 0:
    trend_msg = f"SCADERE 📉 ({pct_change:.2f}%)"
else:
    trend_msg = "STAGNARE ➖ (0.00%)"

last_date = dates[-1]
next_date = last_date + datetime.timedelta(days=1)
if next_date.weekday() > 4: next_date += datetime.timedelta(days=(7 - next_date.weekday()))

print(f"\n========================================================")
print(f"RAPORT PENTRU URMATOAREA ZI ({next_date.date()})")
print(f"========================================================")
print(f"Ultimul pret inchidere:  {last_real_price:.2f} $")
print(f"Pret PREZIS de AI:       {predicted_price:.2f} $")
print(f"--------------------------------------------------------")
print(f"SEMNAL:  >>>  {trend_msg}  <<<")
print(f"========================================================")

# ==============================================================================
# 4. GRAFIC 1: SIMULATOR INVESTITIE
# ==============================================================================
print("\n--- SIMULATOR DE INVESTITIE (GRAFIC 1) ---")
print(f"Date disponibile intre: {dates[0].date()} si {dates[-1].date()}")

try:
    user_date_str = input("Introdu data start investitie (YYYY-MM-DD): ").strip()
    user_invest_amount = float(input("Suma investita ($): "))
    start_sim_date = pd.to_datetime(user_date_str)
    
    sim_df = full_df[full_df.index >= start_sim_date].copy()
    if len(sim_df) < 5: raise ValueError("Data prea recenta")

    # Calcul Buy & Hold
    initial_p = sim_df['Close'].iloc[0]
    final_p = sim_df['Close'].iloc[-1]
    val_hold = (user_invest_amount / initial_p) * final_p
    
    # Calcul AI Trader
    feat_cols = [c for c in sim_df.columns if 'lag' in c]
    X_sim = sim_df[feat_cols].values
    sim_preds = best_model.predict(X_sim)
    
    cash = user_invest_amount
    shares = 0
    portfolio_vals = []
    prices = sim_df['Close'].values
    
    for i in range(len(prices) - 1):
        curr_p = prices[i]
        prev_close = X_sim[i][0]
        signal_buy = sim_preds[i] > prev_close
        
        if signal_buy and cash > 0:
            shares = cash / curr_p
            cash = 0
        elif not signal_buy and shares > 0:
            cash = shares * curr_p
            shares = 0
        portfolio_vals.append(cash + (shares * curr_p))
    
    val_ai = portfolio_vals[-1]

    print(f"\nREZULTATE FINANCIARE:")
    print(f"1. BUY & HOLD: {val_hold:.2f} $")
    print(f"2. AI TRADER:  {val_ai:.2f} $")

    # --- PLOT SIMULARE ---
    plt.figure(figsize=(10, 5))
    ax1 = plt.gca()
    ax1.plot(sim_df.index, sim_df['Close'], color='blue', alpha=0.3, label='Pret Actiune')
    ax1.set_ylabel('Pret Actiune', color='blue')
    ax2 = ax1.twinx()
    ax2.plot(sim_df.index[:-1], portfolio_vals, color='green', linewidth=2, label='Portofoliu AI')
    ax2.set_ylabel('Banii Tai', color='green')
    plt.title(f"GRAFIC 1: Simulare Trecut ({user_invest_amount}$)")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.show()

except Exception as e:
    print(f"Nu s-a putut genera simularea: {e}")

# ==============================================================================
# 5. GRAFIC 2: PREDICTIE DETALIATA
# ==============================================================================
print("\nSe genereaza Graficul 2 (Detaliu Predictie)...")

ZOOM = 45
if len(dates_test) > ZOOM:
    d_plot = dates_test[-ZOOM:]
    y_plot = y_test[-ZOOM:]
    p_plot = predictions_test[-ZOOM:]
else:
    d_plot = dates_test
    y_plot = y_test
    p_plot = predictions_test

plt.figure(figsize=(10, 6))
plt.plot(d_plot, y_plot, label='Istoric Real', color='blue', marker='o', markersize=4)
plt.plot(d_plot, p_plot, label='Ce credea modelul', color='orange', linestyle='--', alpha=0.7)
plt.plot([d_plot[-1], next_date.date()], 
         [p_plot[-1], predicted_price], 
         color='red', linestyle=':', linewidth=2)
plt.scatter(next_date.date(), predicted_price, 
            color='red', marker='*', s=300, zorder=5, 
            label=f'PREDICTIE: {predicted_price:.2f} ({trend_msg})')

plt.title(f"GRAFIC 2: Predictie {ticker_symbol} - Directie: {trend_msg}")
plt.xlabel("Data")
plt.ylabel("Pret")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()