
Acest director conține codul sursă pentru punctul de intrare (Entry Point) al aplicației. Interfața este construită folosind **Tkinter** și integrează vizualizările **Matplotlib**.

## 1. Cerințe de Sistem

Pentru a rula aplicația, asigurați-vă că aveți instalat:
* **Python:** Versiunea 3.10 sau mai nouă.
* **Sistem de Operare:** Windows, macOS sau Linux (cu suport pentru ferestre X11).
* **Conexiune Internet:** Activă (necesară pentru descărcarea datelor live via `yfinance`).

## 2. Instalare Dependențe

Dacă nu ați instalat deja pachetele din rădăcina proiectului, rulați:

```bash
# Pentru structura modulară:
python src/app/main.py

# SAU, dacă utilizați versiunea într-un singur fișier:
python run.py

