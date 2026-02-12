
Acest director conține fișierele serializate (salvate) ale modelelor de Machine Learning antrenate, gata pentru inferență (predicție).

## 1. Fișiere Disponibile

| Fișier | Format | Descriere | Status |
|--------|--------|-----------|--------|
| `optimized_model.joblib` | Joblib (Binary) | Modelul final **Random Forest Regressor**, optimizat prin Grid Search. Conține 200 de estimatori și este antrenat pe tot istoricul disponibil. | **PRODUCȚIE** |
| `scaler.pkl` | Pickle | (Opțional) Obiectul `StandardScaler` dacă s-ar fi folosit normalizarea datelor. | N/A |

## 2. Detalii Tehnice Model

* **Algoritm:** Random Forest Regressor (`sklearn.ensemble`)
* **Librărie Serializare:** `joblib`
* **Mărime Estimată:** ~5-10 MB
* **Input Shape:** `(n_samples, 6)` -> `[Lag_1..3, Market_Lag_1..3]`

## 3. Cum se încarcă modelul în Python?

Dacă doriți să folosiți acest model într-un alt script fără a re-antrena:

```python
import joblib
import os

# Calea către fișier
model_path = os.path.join("models", "optimized_model.joblib")

if os.path.exists(model_path):
    # Încărcare în memorie
    ai_brain = joblib.load(model_path)
    
    # Predicție directă
    prediction = ai_brain.predict([[205.5, 204.0, 203.0, 4500.1, 4490.5, 4480.0]])
    print(f"Preț prezis: {prediction[0]}")
else:
    print("Eroare: Modelul nu a fost găsit. Rulați antrenarea mai întâi.")