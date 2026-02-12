# Documentație Dataset: Trading AI & S&P 500 Correlation

Acest director conține pipeline-ul de date utilizat pentru antrenarea și validarea modelului `RandomForestRegressor`. Datele sunt serii de timp financiare (Time Series) prelucrate pentru a transforma o problemă de predicție secvențială într-o problemă de învățare supervizată (Supervised Learning).

## 1. Originea Datelor

* **Sursă Primară:** API-ul Public **Yahoo Finance** (via librăria Python `yfinance`).
* **Simboluri:**
    * **Target (Y):** Simbol dinamic introdus de utilizator (ex: `TSLA`, `AAPL`, `BTC-USD`).
    * **Feature Extern (X):** Indicele **S&P 500** (`^GSPC`) folosit pentru a captura contextul macroeconomic ("Market Sentiment").
* **Frecvență:** Zilnică (Daily candles - OHLC).
* **Perioadă:** Ultimii 2 ani (calculat dinamic la momentul rulării).

## 2. Structura Directorului

Datele sunt organizate în următoarele sub-directoare pentru a reflecta etapele de procesare:

| Folder | Descriere | Fișier Tipic |
|--------|-----------|--------------|
| `raw/` | Datele brute descărcate direct de pe Yahoo Finance, fără modificări. | `TSLA_raw.csv`, `SP500_raw.csv` |
| `generated/` | **Contribuția Originală (Feature Engineering).** Datele combinate (Ticker + Market) și augmentate cu coloane de tip "Lag". | `dataset_full_features.csv` |
| `processed/` | Varianta finală curățată (fără valori `NaN` rezultate din shiftare), gata de intrare în model. | `final_clean_data.csv` |
| `train/` | Primele 90% din datele procesate, folosite pentru antrenare și optimizare Grid Search. | `train_set.csv` |
| `test/` | Ultimele 10% din date, folosite strict pentru evaluarea finală (Out-of-sample). | `test_set.csv` |

## 3. Dicționar de Date (Features)

Dataset-ul final (`generated/dataset_full_features.csv`) conține următoarele coloane:

| Nume Coloană | Tip Date | Descriere | Rol în Model |
|--------------|----------|-----------|--------------|
| `Date` | Datetime | Indexul temporal (Zile lucrătoare bursiere). | Index |
| `Close` | Float | Prețul de închidere al acțiunii țintă (ex: Tesla). | **Target (y)** (la momentul t) |
| `Market_Close` | Float | Prețul de închidere al indicelui S&P 500. | Referință |
| `lag_1` | Float | Prețul acțiunii cu **1 zi în urmă** (t-1). | **Feature (X)** |
| `lag_2` | Float | Prețul acțiunii cu **2 zile în urmă** (t-2). | **Feature (X)** |
| `lag_3` | Float | Prețul acțiunii cu **3 zile în urmă** (t-3). | **Feature (X)** |
| `market_lag_1` | Float | Prețul S&P 500 cu **1 zi în urmă**. | **Feature (X)** |
| `market_lag_2` | Float | Prețul S&P 500 cu **2 zile în urmă**. | **Feature (X)** |
| `market_lag_3` | Float | Prețul S&P 500 cu **3 zile în urmă**. | **Feature (X)** |

## 4. Statistici și Procesare

### 4.1 Feature Engineering (Contribuție Proprie)
Algoritmul nu primește data curentă, ci "ferestre" istorice.
* S-a utilizat o fereastră de timp **n=3 zile**.
* S-a realizat un `Inner Join` între Ticker și S&P 500 pentru a alinia datele și a exclude zilele în care bursa a fost închisă (weekend-uri, sărbători legale).

### 4.2 Preprocesare
1.  **Cleaning:** Eliminarea primelor `n=3` rânduri care conțin valori `NaN` (rezultate inevitabil din operația de `shift()`).
2.  **Splitting:**
    * **Train:** 90% (aprox. 450 zile) - Folosit pentru `RandomizedSearchCV`.
    * **Test:** 10% (aprox. 50 zile) - Folosit pentru calculul metricilor finale (MAE, ROI).
3.  **Scalare:** Nu s-a aplicat normalizare (MinMax/StandardScaler) deoarece algoritmul **Random Forest** nu este sensibil la magnitudinea datelor, fiind bazat pe reguli de decizie (arbori).

---
*Acest fișier documentează strict datele utilizate în cadrul Proiectului de Rețele Neuronale.*