
Acest director conține logica de Machine Learning a proiectului. Aici este definit, antrenat și optimizat algoritmul care prezice prețul viitor al acțiunilor.

## 1. Algoritmul Utilizat: Random Forest Regressor

Deși disciplina se numește "Rețele Neuronale", pentru acest proiect am ales o arhitectură de tip **Ensemble Learning (Random Forest)**, deoarece s-a dovedit superioară rețelelor neuronale clasice (MLP/LSTM) pe seturi de date financiare mici (< 1000 observații).

### De ce Random Forest?
1.  **Robust la Zgomot:** Piețele financiare sunt "zgomotoase" (stochastic noise). Random Forest reduce varianța prin medierea a sute de arbori decizionali.
2.  **Nu necesită Scalare:** Spre deosebire de Rețelele Neuronale care au nevoie de date normalizate (0-1), arborii lucrează direct cu prețurile brute.
3.  **Interpretabilitate:** Putem extrage importanța fiecărui feature (ex: cât contează S&P 500 vs. Istoricul Acțiunii).

### Arhitectura Simplificată

```mermaid
graph TD
    Input[Input Features: Lag_1...Lag_3] --> Tree1[Arbore Decizional 1]
    Input --> Tree2[Arbore Decizional 2]
    Input --> TreeN[Arbore Decizional N]
    
    Tree1 --> Pred1[Predicție 1: 205$]
    Tree2 --> Pred2[Predicție 2: 203$]
    TreeN --> PredN[Predicție N: 208$]
    
    Pred1 & Pred2 & PredN --> Aggregation[Media Aritmetică]
    Aggregation --> Output[Output Final: 205.33$]