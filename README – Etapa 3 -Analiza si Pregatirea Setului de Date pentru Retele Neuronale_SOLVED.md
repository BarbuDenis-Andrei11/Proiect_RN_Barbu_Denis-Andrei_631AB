# 📘 README – Etapa 3: Analiza și Pregătirea Setului de Date pentru Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Barbu Denis-Andrei 
**Data:** 25.11.2025 

---

## Introducere

Acest document descrie activitățile realizate în Etapa 3, în care se analizează și se preprocesează setul de date necesar proiectului de predicție a prețurilor bursiere. Scopul acestei etape este transformarea datelor brute descărcate prin API-ul Yahoo Finance într-un format de tip "serie temporală supravegheată", optimizat pentru antrenarea unei rețele neuronale recurente de tip LSTM (Long Short-Term Memory).

---

##  1. Structura Repository-ului Github (versiunea Etapei 3)

```
project-name/
├── README.md              # Documentația etapei curente
├── docs/
│   └── datasets/          # Analiza pieței și diagrame flux date
├── data/
│   ├── raw/               # Date descărcate direct (yfinance)
│   ├── processed/         # Date după feature engineering (SMA, Volatility)
│   ├── train/             # Secvențe de antrenare (80%)
│   ├── validation/        # Secvențe de validare (10%)
│   └── test/              # Secvențe de testare (10%)
├── src/
│   ├── preprocessing/     # Funcții: df_to_windowed_df, windowed_df_to_date_X_y
│   ├── data_acquisition/  # Script descărcare simboluri bursiere
│   └── neural_network/    # Modelul LSTM implementat în Keras
├── config/                # Parametri: n=3, learning_rate=0.001
└── requirements.txt       # yfinance, pandas, numpy, scikit-learn, tensorflow
```

---

##  2. Descrierea Setului de Date

### 2.1 Sursa datelor

* **Origine:** Yahoo Finance API (prin biblioteca Python yfinance).
* **Modul de achiziție:** ☐ Senzori reali / ☐ Simulare / ☒ Fișier extern / ☒ Generare programatică.
* **Perioada / condițiile colectării:** Date istorice zilnice pe o perioadă de 2 ani anterioară momentului rulării, asigurând un volum de aproximativ 500 de înregistrări financiare.

### 2.2 Caracteristicile dataset-ului

* **Număr total de observații:** Aproximativ 500 de rânduri (variabil în funcție de simbol).
* **Număr de caracteristici (features):** 5 coloane principale extrase/generate.
* **Tipuri de date:** ☒ Numerice / ☐ Categoriale / ☒ Temporale / ☐ Imagini.
* **Format fișiere:** ☐ CSV / ☒ Dataframe Pandas (în memorie) / ☐ JSON.

### 2.3 Descrierea fiecărei caracteristici

| **Caracteristică** | **Tip** | **Unitate** | **Descriere** | **Domeniu valori** |
|-------------------|---------|-------------|---------------|--------------------|
| Close | numeric | Valută | [Prețul de închidere al acțiunii] | > 0 |
| SMA_7 | numeric | Valută | [Media mobilă simplă pe 7 zile] | > 0 |
| SMA_30 | numeric | Valută | [Media mobilă simplă pe 30 zile] | > 0 |
| Daily_Return| numeric | Procent | Randamentul zilnic (modificarea %) | [-1, 1] |
| Volatility | numeric | Indice | Deviația standard a prețului pe 7 zile | > 0 |

**Fișier recomandat:**  `data/README.md`

---

##  3. Analiza Exploratorie a Datelor (EDA) – Sintetic

### 3.1 Statistici descriptive aplicate

* **Medie, mediană, deviație standard**: Calculate pentru prețul Close pentru a identifica tendința pieței.
* **Min–max și quartile**: Identificată prin indicatorul standard deviation, esențială pentru a determina riscul.
* **Distribuții pe caracteristici** Monitorizată pentru a observa perioadele de "bull" sau "bear" market.


### 3.2 Analiza calității datelor

* **Detectarea valorilor lipsă** S-au identificat valori NaN în primele 30 de rânduri rezultate în urma calculului mediilor mobile (SMA_30).
* **Detectarea valorilor inconsistente sau eronate**: Eliminarea erorilor API prin filtrarea coloanei Close și transformarea forțată în format numeric.


### 3.3 Probleme identificate

* Lipsa datelor în weekend: Piețele bursiere sunt închise sâmbăta și duminica, generând discontinuități temporale care au fost gestionate prin logica de calcul a datei viitoare.
* Diferențe de magnitudine: Prețul (ex: 200) și randamentul (ex: 0.02) necesită scalare obligatorie pentru convergența rețelei neuronale.


---

##  4. Preprocesarea Datelor

### 4.1 Curățarea datelor

* **Eliminare duplicatelor**: Verificarea indexului de tip Datetime.
* **Tratarea valorilor lipsă:**
  * S-a utilizat funcția df.dropna() pentru a elimina rândurile incomplete rezultate din calculul indicatorilor tehnici.


### 4.2 Transformarea caracteristicilor

* **Normalizare:** S-a aplicat MinMaxScaler (interval 0-1) pe setul de instruire pentru a uniformiza datele de intrare ale LSTM-ului.
* **Windowing/Fereastra de timp** Transformarea seriei în set de date supervizat folosind o fereastră $n=3$ (predicția se face pe baza ultimelor 3 zile).


### 4.3 Structurarea seturilor de date

**Împărțire recomandată:**
* 80% – train Pentru antrenarea ponderilor modelului.
* 10% – validation Pentru monitorizarea supra-antrenării (overfitting).
* 10% – test Pentru evaluarea performanței pe date complet noi.

**Principii respectate:**
* Stratificare pentru clasificare
* Fără scurgere de informație (data leakage)
* Statistici calculate DOAR pe train și aplicate pe celelalte seturi

### 4.4 Salvarea rezultatelor preprocesării

* Parametrii scaler-ului sunt stocați pentru a converti predicția finală din intervalul [0,1] înapoi în preț real (inverse transform).

---

##  5. Fișiere Generate în Această Etapă


* `data/processed/` – Setul de date cu indicatori tehnici (SMA, Volatilitate).
* `src/preprocessing/` – Scriptul conținând funcțiile df_to_windowed_df.
* `Visual_Output` – Graficul generat de script care arată predicția pe ultimele 45 de zile față de realitate.

---

##  6. Stare Etapă (de completat de student)

[x] Structură repository configurată

[x] Dataset analizat (descărcare live prin Yahoo Finance)

[x] Date preprocesate (Windowing n=3 și Scalare Min-Max)

[x] Seturi train/val/test generate

[x] Documentație actualizată în README

---
