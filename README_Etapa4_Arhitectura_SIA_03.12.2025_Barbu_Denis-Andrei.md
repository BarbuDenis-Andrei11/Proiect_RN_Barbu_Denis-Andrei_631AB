# 📘 README – Etapa 4: Arhitectura Completă a Aplicației SIA bazată pe Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** Barbu Denis-Andrei 
**Link Repository GitHub** https://github.com/BarbuDenis-Andrei11/Proiect_RN_Barbu_Denis-Andrei_631AB
**Data:** 09.12.2025 
---

## Scopul Etapei 4

Această etapă marchează dezvoltarea arhitecturii complete a Sistemului cu Inteligență Artificială (SIA). Proiectul integrează un pipeline complet: de la achiziția datelor financiare în timp real, până la predicția prețului prin intermediul unei rețele neuronale de tip LSTM, totul fiind accesibil printr-o interfață mobilă realizată în React Native.

### IMPORTANT - Ce înseamnă "schelet funcțional":

 **CE TREBUIE SĂ FUNCȚIONEZE:**
- Toate modulele pornesc fără erori
- Pipeline-ul complet rulează end-to-end (de la date → până la output UI)
- Modelul RN este definit și compilat (arhitectura există)
- Web Service/UI primește input și returnează output

 **CE NU E NECESAR ÎN ETAPA 4:**
- Model RN antrenat cu performanță bună
- Hiperparametri optimizați
- Acuratețe mare pe test set
- Web Service/UI cu funcționalități avansate

**Scopul anti-plagiat:** Nu puteți copia un notebook + model pre-antrenat de pe internet, pentru că modelul vostru este NEANTRENAT în această etapă. Demonstrați că înțelegeți arhitectura și că ați construit sistemul de la zero.

---

##  Livrabile Obligatorii

### 1. Tabelul Nevoie Reală → Soluție SIA → Modul Software (max ½ pagină)
Completați in acest readme tabelul următor cu **minimum 2-3 rânduri** care leagă nevoia identificată în Etapa 1-2 cu modulele software pe care le construiți (metrici măsurabile obligatoriu):

| **Nevoie reală concretă** | **Cum o rezolvă SIA-ul vostru** | **Modul software responsabil** |
|---------------------------|--------------------------------|--------------------------------|
| Predicția prețului de închidere pentru investitori de tip "Day Trading" | Model de regresie LSTM care analizează ultimele 3 zile → eroare (MAE) minimizată | RN Module (src/neural_network) |
| Acces rapid la date financiare live fără baze de date costisitoare | Integrare API Yahoo Finance pentru descărcare și procesare on-the-fly sub 5 secunde | Data Acquisition (src/data_acquisition) |
| Vizualizarea intuitivă a trendului viitor pe dispozitive mobile | Interfață React Native care afișează graficul comparativ (Real vs. Predicție) | UI Module (src/app) |


**Instrucțiuni:**
- Fiți concreti (nu vagi): "detectare fisuri sudură" ✓, "îmbunătățire proces" ✗
- Specificați metrici măsurabile: "< 2 secunde", "> 95% acuratețe", "reducere 20%"
- Legați fiecare nevoie de modulele software pe care le dezvoltați

---

### 2. Contribuția Voastră Originală la Setul de Date – MINIM 40% din Totalul Observațiilor Finale

Total observații finale: 500 (2 ani de istoric bursier)

Observații originale: 200 (40%)

Tipul contribuției: [x] Date generate prin simulare fizică (Simulare de scenarii "Black Swan" / zgomot Brownian)

[ ] Date achiziționate cu senzori proprii

[ ] Etichetare/adnotare manuală

[x] Date sintetice prin metode avansate (Augmentare prin Feature Engineering original)

Descriere detaliată: Contribuția originală constă în două componente:

Feature Engineering (20%): Calcularea indicatorilor de volatilitate și medii mobile (SMA_7, SMA_30) care nu există în dataset-ul brut. Acești indicatori sunt creați programatic pentru a oferi context modelului.

Generare Sintetică (20%): Pentru a atinge pragul de 40%, am implementat un script care generează 200 de eșantioane sintetice bazate pe mișcarea Browniană geometrică (Geometric Brownian Motion), simulând variații de preț extreme pentru a testa robustețea modelului în condiții de criză financiară.

Locația codului: src/data_acquisition/generate_synthetic.py

Locația datelor: data/generated/synthetic_stock_data.csv

### 3. Diagrama State Machine a Întregului Sistem (OBLIGATORIE)

Locație Diagramă: docs/state_machine.pngJustificarea State Machine-ului ales:Am ales o arhitectură de tip Predictive Batch Processing deoarece piața bursieră funcționează pe intervale discrete (închiderea zilnică). Sistemul trebuie să asigure consistența datelor înainte de a rula modelul greu de IA.

Stările principale sunt:
* IDLE: Aplicația așteaptă introducerea simbolului (ex: TSLA) de către utilizator în React Native.
* ACQUIRE_DATA: Modulul Python apelează Yahoo Finance și descarcă ultimele 500 de rânduri.PREPROCESS: Datele sunt scalate cu MinMaxScaler și transformate în ferestre de timp ($n=3$).
* RN_INFERENCE: Modelul LSTM procesează fereastra curentă și generează valoarea scalară a prețului.DISPLAY_RESULT: Rezultatul este trimis către UI și afișat pe grafic.

Tranzițiile critice:
* PREPROCESS → ERROR: Dacă simbolul introdus nu există (ex: "ABCXYZ"), sistemul revine în IDLE cu o alertă.
* INFERENCE → DISPLAY: Tranziția se face doar după ce modelul confirmă calculul valorii scalate în intervalul [0,1].

### 4. Scheletul Complet al celor 3 Module Cerute la Curs (slide 7)

Toate cele 3 module trebuie să **pornească și să ruleze fără erori** la predare. Nu trebuie să fie perfecte, dar trebuie să demonstreze că înțelegeți arhitectura.

| **Modul** | **Python (exemple tehnologii)** | **Cerință minimă funcțională (la predare)** |
|-----------|----------------------------------|-------------|----------------------------------------------|
| **1. Data Logging** | Python / yfinance | Descarcă datele, aplică SMA_7/30 și salvează în data/raw/. |
| **2. Neural Network Module** | TensorFlow / Keras | Arhitectură definită: 1 strat LSTM (82 unități) + 2 straturi Dense (41 unități). |
| **3. Web Service / UI** | React Native / Flask | Ecran de input pentru Ticker și container pentru afișarea prețului prezis. |

#### Detalii per modul:

#### **Modul 1: Data Logging / Acquisition**

Acest modul se ocupă de extragerea datelor financiare în timp real și generarea componentelor de originalitate cerute.
Funcționalități implementate:
[x] Cod funcțional: Scriptul utilizează biblioteca yfinance pentru a descărca istoricul bursier pe ultimii 2 ani.
[x] Generare CSV: Datele sunt procesate și salvate într-un format compatibil cu fereastra de timp $n=3$ definită în Etapa 3.
[x] Contribuție originală (40%): * Feature Engineering: Calcularea indicatorilor SMA_7, SMA_30, Daily_Return și Volatility care adaugă valoare analitică setului brut.
    * Date Sintetice: Scriptul generate_synthetic.py injectează eșantioane bazate pe modelul Geometric Brownian Motion pentru a testa modelul în condiții de volatilitate extremă.
[x] Documentație: Codul include parametrii de configurare pentru intervalul de timp și simbolul ales (Ticker).

#### **Modul 2: Neural Network Module**

Modulul reprezintă "creierul" SIA, având arhitectura complet definită și compilată, pregătită pentru fluxul de date.

Funcționalități implementate:

[x] Arhitectură definită: Modelul este de tip Sequential și utilizează un strat LSTM cu 82 de unități pentru a capta dependențele temporale ale prețurilor.

[x] Configurație straturi: Include două straturi intermediare Dense de 41 de unități cu activare relu și un strat de ieșire liniar pentru regresie.

[x] Compilare: Utilizăm optimizatorul Adam (learning rate 0.001) și funcția de pierdere MSE (Mean Squared Error).

[x] Justificare arhitectură: S-a ales LSTM deoarece prețurile bursiere sunt serii temporale non-liniare; LSTM poate "reține" trendurile pe termen scurt (cele 3 zile din fereastră) mult mai bine decât o rețea neuronală simplă.


#### **Modul 3: Web Service / UI**

Interfața utilizator este realizată în React Native, oferind o experiență mobilă pentru accesarea predicțiilor de IA.

Funcționalități MINIME implementate:

[x] Input utilizator: Ecranul principal conține un câmp de introducere text pentru simbolul companiei (ex: AAPL, TSLA, BTC-USD).

[x] Comunicare: UI-ul trimite simbolul către scriptul de backend, care returnează prețul prezis pentru ziua următoare.

[x] Screenshot demonstrativ: Disponibil în docs/screenshots/ui_demo.png (reprezentând formularul de input și zona de afișare a rezultatului).


## Structura Repository-ului la Finalul Etapei 4 (OBLIGATORIE)

**Verificare consistență cu Etapa 3:**

```
proiect-rn-[nume-prenume]/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── generated/  # Date originale
│   ├── train/
│   ├── validation/
│   └── test/
├── src/
│   ├── data_acquisition/
│   ├── preprocessing/  # Din Etapa 3
│   ├── neural_network/
│   └── app/  # UI schelet
├── docs/
│   ├── state_machine.*           #(state_machine.png sau state_machine.pptx sau state_machine.drawio)
│   └── [alte dovezi]
├── models/  # Untrained model
├── config/
├── README.md
├── README_Etapa3.md              # (deja existent)
├── README_Etapa4_Arhitectura_SIA.md              # ← acest fișier completat (în rădăcină)
└── requirements.txt  # Sau .lvproj
```

**Diferențe față de Etapa 3:**
- Adăugat `data/generated/` pentru contribuția dvs originală
- Adăugat `src/data_acquisition/` - MODUL 1
- Adăugat `src/neural_network/` - MODUL 2
- Adăugat `src/app/` - MODUL 3
- Adăugat `models/` pentru model neantrenat
- Adăugat `docs/state_machine.png` - OBLIGATORIU
- Adăugat `docs/screenshots/` pentru demonstrație UI

---

## Checklist Final – Bifați Totul Înainte de Predare

[x] Tabelul Nevoie → Soluție completat.

[x] Declarație contribuție 40% (20% Feature Engineering + 20% Synthetic).

[x] Diagrama State Machine salvată în docs/.

[x] Modulul 1 (Data Acquisition) produce CSV.

[x] Modulul 2 (Neural Network) are arhitectura LSTM definită.

[x] Modulul 3 (UI) permite introducerea unui simbol bursier.


