import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import datetime
import threading
import os
import json
import sys

# --- IMPORTURI MODULARE ---
# Adaugam calea radacina pentru a gasi modulele src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from src.data_acquisition.generate import download_data
    from src.preprocessing.data_cleaner import clean_dataframe
    from src.preprocessing.feature_engineering import create_features
    from src.preprocessing.data_splitter import split_time_series_data
    from src.neural_network.model import save_model
    # Importam librariile ML direct aici pentru acces complet la obiectul de cautare (pt. rapoarte)
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.metrics import mean_absolute_error
except ImportError as e:
    messagebox.showerror("Eroare Import", f"Nu s-au putut incarca modulele: {e}\n\nRulati 'python fix_project.py' daca lipsesc fisiere.")
    sys.exit(1)

# ==============================================================================
# 1. FUNCTII UTILITARE (SALVARE REZULTATE)
# ==============================================================================
def save_project_results(search_object, y_test, y_pred, dates_test, mae_score):
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    # A. optimization_experiments.csv
    try:
        cv_results = pd.DataFrame(search_object.cv_results_)
        cols = ['params', 'mean_test_score', 'std_test_score', 'rank_test_score']
        final_cols = [c for c in cols if c in cv_results.columns]
        cv_results[final_cols].to_csv(os.path.join(results_dir, "optimization_experiments.csv"), index=False)
    except Exception as e:
        print(f"Eroare CSV: {e}")

    # B. final_metrics.json
    try:
        # Calcul Directie
        directions_pred = [1 if p > y_test[i-1] else 0 for i, p in enumerate(y_pred) if i > 0]
        directions_real = [1 if y > y_test[i-1] else 0 for i, y in enumerate(y_test) if i > 0]
        if len(directions_pred) > 0:
            acc = sum([1 for i in range(len(directions_pred)) if directions_pred[i] == directions_real[i]]) / len(directions_pred)
        else:
            acc = 0.0
        
        metrics = {
            "algorithm": "RandomForestRegressor",
            "MAE_test": float(mae_score),
            "Directional_Accuracy": float(round(acc * 100, 2)),
            "Best_Params": search_object.best_params_
        }
        with open(os.path.join(results_dir, "final_metrics.json"), "w") as f:
            json.dump(metrics, f, indent=4)
    except Exception as e:
        print(f"Eroare JSON Metrics: {e}")

    # C. error_analysis.json
    try:
        df_err = pd.DataFrame({'Date': dates_test, 'Real': y_test, 'Pred': y_pred, 'Err': abs(y_test - y_pred)})
        top_err = df_err.sort_values('Err', ascending=False).head(5)
        err_list = []
        for _, row in top_err.iterrows():
            err_list.append({
                "Date": str(row['Date'].date()),
                "Real": float(row['Real']),
                "Pred": float(row['Pred']),
                "Error": float(row['Err'])
            })
        with open(os.path.join(results_dir, "error_analysis.json"), "w") as f:
            json.dump(err_list, f, indent=4)
    except Exception as e:
        print(f"Eroare JSON Errors: {e}")

# ==============================================================================
# 2. CLASA PRINCIPALA GUI (PREMIUM LOOK)
# ==============================================================================
class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading AI System - Proiect Licență")
        self.root.geometry("1280x800")
        
        # --- STYLING ---
        self.style = ttk.Style()
        self.style.theme_use('clam') # Tema mai curata
        
        # Culori si Fonturi
        bg_color = "#f0f0f0"
        self.root.configure(bg=bg_color)
        
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#333")
        self.style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#666", background="#e0e0e0")
        
        # Variabile State
        self.df_ticker = None
        self.df_market = None
        self.best_model = None
        self.full_df = None
        self.search_object = None
        self.X_test = None
        self.y_test = None
        self.dates_test = None
        self.predictions_test = None
        self.predicted_price = 0.0
        self.next_date = None
        self.trend_msg = ""
        
        self.setup_ui()

    def setup_ui(self):
        # --- LAYOUT PRINCIPAL ---
        # Stanga: Control | Dreapta: Grafice
        
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === STANGA: PANOU CONTROL ===
        left_panel = ttk.Frame(main_container, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Titlu Sectiune
        ttk.Label(left_panel, text="🎛️ Panou de Control", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        
        # 1. Input Simbol
        control_group = ttk.LabelFrame(left_panel, text="Configurare Date", padding=10)
        control_group.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_group, text="Simbol Bursier (Yahoo Finance):").pack(anchor="w")
        self.entry_symbol = ttk.Entry(control_group, font=("Consolas", 11))
        self.entry_symbol.pack(fill=tk.X, pady=5)
        self.entry_symbol.insert(0, "TSLA")
        
        # Buton Analiza
        self.btn_analyze = ttk.Button(control_group, text="🚀 1. Start Analiză & Optimizare", command=self.start_analysis_thread)
        self.btn_analyze.pack(fill=tk.X, pady=10)
        
        # Progress Bar
        self.progress = ttk.Progressbar(control_group, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # 2. Input Simulare
        sim_group = ttk.LabelFrame(left_panel, text="Simulator Investiție", padding=10)
        sim_group.pack(fill=tk.X, pady=10)
        
        ttk.Label(sim_group, text="Data Start (YYYY-MM-DD):").pack(anchor="w")
        self.entry_date = ttk.Entry(sim_group)
        self.entry_date.pack(fill=tk.X, pady=5)
        self.entry_date.insert(0, "2024-01-01")
        
        ttk.Label(sim_group, text="Suma Investită ($):").pack(anchor="w")
        self.entry_amount = ttk.Entry(sim_group)
        self.entry_amount.pack(fill=tk.X, pady=5)
        self.entry_amount.insert(0, "1000")
        
        self.btn_simulate = ttk.Button(sim_group, text="📈 2. Rulează Simulare", command=self.run_simulation, state=tk.DISABLED)
        self.btn_simulate.pack(fill=tk.X, pady=10)
        
        # 3. Jurnal Log
        log_group = ttk.LabelFrame(left_panel, text="Jurnal Sistem", padding=5)
        log_group.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_group, height=15, state='disabled', font=("Consolas", 9), bg="#1e1e1e", fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Tag-uri pentru culori in log
        self.log_text.tag_config("INFO", foreground="#00bfff")   # Albastru deschis
        self.log_text.tag_config("SUCCESS", foreground="#00ff00") # Verde neon
        self.log_text.tag_config("ERROR", foreground="#ff4d4d")   # Rosu
        self.log_text.tag_config("WARNING", foreground="orange")
        
        # === DREAPTA: ZONA GRAFICE ===
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1
        self.tab_predict = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_predict, text="📊 Predicție Viitor")
        
        # Tab 2
        self.tab_sim = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sim, text="💰 Performanță Financiară")
        
        # Init Figuri Matplotlib
        self.fig_predict = Figure(figsize=(5, 4), dpi=100)
        self.ax_predict = self.fig_predict.add_subplot(111)
        self.canvas_predict = FigureCanvasTkAgg(self.fig_predict, master=self.tab_predict)
        self.canvas_predict.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig_sim = Figure(figsize=(5, 4), dpi=100)
        self.ax_sim = self.fig_sim.add_subplot(111)
        self.canvas_sim = FigureCanvasTkAgg(self.fig_sim, master=self.tab_sim)
        self.canvas_sim.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status Bar Jos
        self.status_var = tk.StringVar()
        self.status_var.set("Gata de start.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel", padding=5, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # --- LOGGING HELPER ---
    def log(self, msg, tag="INFO"):
        self.log_text.config(state='normal')
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        # Update status bar
        if len(msg) < 50:
            self.status_var.set(msg)

    # --- LOGICA DE BUSINESS ---
    def start_analysis_thread(self):
        self.btn_analyze.config(state=tk.DISABLED)
        self.progress.start(10) # Porneste animatia
        self.log(">>> START PROCES DE ANALIZĂ", "INFO")
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def run_analysis(self):
        try:
            symbol = self.entry_symbol.get().strip().upper()
            
            # 1. DESCARCARE
            self.log(f"1. Se descarcă datele pentru: {symbol}...", "INFO")
            df_t, df_m = download_data(symbol)
            if df_t is None: raise ValueError("Eroare la descărcarea datelor.")
            self.log("   [OK] Date descărcate.", "SUCCESS")
            
            # 2. PROCESARE
            self.log("2. Preprocesare și Feature Engineering...", "INFO")
            self.df_ticker = clean_dataframe(df_t)
            self.df_market = clean_dataframe(df_m)
            
            dates, X, y, full_df = create_features(self.df_ticker, self.df_market)
            self.full_df = full_df
            
            X_train, self.X_test, y_train, self.y_test, self.dates_test = split_time_series_data(X, y, dates)
            self.log(f"   [OK] Dataset pregătit: {len(X)} zile.", "SUCCESS")
            
            # 3. OPTIMIZARE (AI)
            self.log("3. Optimizare Model (Grid Search)... Așteptați.", "WARNING")
            
            # Definim algoritmul si parametrii
            rf = RandomForestRegressor(random_state=42)
            param_dist = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5]
            }
            
            # Rulam Grid Search
            self.search_object = RandomizedSearchCV(rf, param_dist, n_iter=5, cv=3, verbose=0, random_state=42, n_jobs=1)
            self.search_object.fit(X_train, y_train)
            self.best_model = self.search_object.best_estimator_
            
            self.log(f"   [OK] Cel mai bun model găsit: {self.search_object.best_params_}", "SUCCESS")
            
            # 4. SALVARE
            save_model(self.best_model)
            self.log("   [OK] Model salvat în 'models/'", "SUCCESS")
            
            # 5. PREDICTIE TEST
            self.predictions_test = self.best_model.predict(self.X_test)
            mae = mean_absolute_error(self.y_test, self.predictions_test)
            self.log(f"   > MAE (Eroare Medie) pe Test: {mae:.2f} $", "INFO")
            
            # Salvare rezultate
            save_project_results(self.search_object, self.y_test, self.predictions_test, self.dates_test, mae)
            self.log("   [OK] Rapoarte generate în 'results/'", "SUCCESS")
            
            # 6. PREDICTIE VIITOR
            t_vals = self.df_ticker['Close'].iloc[-3:].values[::-1]
            m_vals = self.df_market['Close'].iloc[-3:].values[::-1]
            last_feats = np.concatenate([t_vals, m_vals])
            
            self.predicted_price = self.best_model.predict([last_feats])[0]
            last_real = self.df_ticker['Close'].iloc[-1]
            diff = self.predicted_price - last_real
            pct = (diff / last_real) * 100
            
            msg = "CREȘTERE 📈" if diff > 0 else "SCĂDERE 📉"
            self.trend_msg = f"{msg} ({pct:+.2f}%)"
            
            self.next_date = dates[-1] + datetime.timedelta(days=1)
            if self.next_date.weekday() > 4: self.next_date += datetime.timedelta(days=(7 - self.next_date.weekday()))
            
            self.log("="*30, "INFO")
            self.log(f"PREDICȚIE PENTRU: {self.next_date.date()}", "WARNING")
            self.log(f"PREȚ ESTIMAT: {self.predicted_price:.2f} $", "SUCCESS")
            self.log(f"SEMNAL: {self.trend_msg}", "SUCCESS")
            self.log("="*30, "INFO")
            
            # Update UI din thread principal
            self.root.after(0, self.finish_analysis_ui)
            
        except Exception as e:
            self.log(f"EROARE CRITICA: {e}", "ERROR")
            self.root.after(0, lambda: self.btn_analyze.config(state=tk.NORMAL))
            self.root.after(0, self.progress.stop)

    def finish_analysis_ui(self):
        self.progress.stop()
        self.btn_analyze.config(state=tk.NORMAL)
        self.btn_simulate.config(state=tk.NORMAL)
        self.status_var.set("Analiză completă. Pregătit pentru simulare.")
        self.plot_prediction_graph()
        self.notebook.select(self.tab_predict)

    def run_simulation(self):
        try:
            date_str = self.entry_date.get()
            amount = float(self.entry_amount.get())
            start_date = pd.to_datetime(date_str)
            
            self.log(f"--- Rulare Simulare ({amount}$) ---", "INFO")
            
            sim_df = self.full_df[self.full_df.index >= start_date].copy()
            if len(sim_df) < 5:
                self.log("Dată prea recentă. Alegeți o dată mai veche.", "ERROR")
                return
            
            # Logica Simulare
            feat_cols = [c for c in sim_df.columns if 'lag' in c]
            X_sim = sim_df[feat_cols].values
            preds = self.best_model.predict(X_sim)
            
            cash = amount
            shares = 0
            vals = []
            prices = sim_df['Close'].values
            
            for i in range(len(prices)-1):
                curr = prices[i]
                prev_close = X_sim[i][0]
                
                # Strategie
                if preds[i] > prev_close and cash > 0:
                    shares = cash / curr
                    cash = 0
                elif preds[i] <= prev_close and shares > 0:
                    cash = shares * curr
                    shares = 0
                vals.append(cash + (shares * curr))
            
            final_ai = vals[-1]
            
            # Buy & Hold Correct Calculation
            init_price = sim_df['Close'].iloc[0]
            final_price = sim_df['Close'].iloc[-2]
            final_bh = (amount / init_price) * final_price
            
            roi_ai = ((final_ai - amount) / amount) * 100
            roi_bh = ((final_bh - amount) / amount) * 100
            
            self.log(f"Rezultat Buy & Hold: {final_bh:.2f} $ ({roi_bh:+.2f}%)", "INFO")
            self.log(f"Rezultat AI Trader:  {final_ai:.2f} $ ({roi_ai:+.2f}%)", "SUCCESS" if final_ai > final_bh else "WARNING")
            
            self.plot_simulation_graph(sim_df, vals, amount)
            self.notebook.select(self.tab_sim)
            
        except Exception as e:
            self.log(f"Eroare Simulare: {e}", "ERROR")

    # --- GRAFICE ---
    def plot_prediction_graph(self):
        self.ax_predict.clear()
        
        # Plot last 45 days
        zoom = 45
        d = self.dates_test[-zoom:]
        y = self.y_test[-zoom:]
        p = self.predictions_test[-zoom:]
        
        self.ax_predict.plot(d, y, label='Istoric Real', color='#1f77b4', linewidth=2)
        self.ax_predict.plot(d, p, label='Model AI', color='#ff7f0e', linestyle='--', alpha=0.8)
        
        # Linie viitor
        self.ax_predict.plot([d[-1], self.next_date.date()], [p[-1], self.predicted_price], 'r:', linewidth=2)
        self.ax_predict.scatter(self.next_date.date(), self.predicted_price, color='red', s=150, zorder=5, marker='*', label='Predicție')
        
        self.ax_predict.set_title(f"Predicție: {self.predicted_price:.2f}$ | {self.trend_msg}", fontsize=10, fontweight='bold')
        self.ax_predict.legend()
        self.ax_predict.grid(True, alpha=0.3, linestyle='--')
        self.fig_predict.autofmt_xdate()
        self.canvas_predict.draw()

    def plot_simulation_graph(self, sim_df, portfolio_vals, initial_invest):
        self.ax_sim.clear()
        
        dates = sim_df.index[:-1]
        prices = sim_df['Close'].iloc[:-1]
        
        # Calcul Buy & Hold curve ($)
        bh_vals = (prices / prices.iloc[0]) * initial_invest
        
        self.ax_sim.plot(dates, bh_vals, color='gray', alpha=0.6, linewidth=2, label='Buy & Hold ($)')
        self.ax_sim.plot(dates, portfolio_vals, color='#2ca02c', linewidth=2.5, label='AI Trader ($)') # Verde puternic
        
        self.ax_sim.axhline(initial_invest, color='red', linestyle='--', alpha=0.5, label='Investiție Inițială')
        
        self.ax_sim.fill_between(dates, portfolio_vals, initial_invest, where=(np.array(portfolio_vals) >= initial_invest), interpolate=True, color='green', alpha=0.1)
        
        self.ax_sim.set_ylabel("Valoare Portofoliu ($)")
        self.ax_sim.set_title("Validare Financiară: AI vs Strategie Pasivă", fontsize=10, fontweight='bold')
        self.ax_sim.legend()
        self.ax_sim.grid(True, alpha=0.3, linestyle='--')
        self.fig_sim.autofmt_xdate()
        self.canvas_sim.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()