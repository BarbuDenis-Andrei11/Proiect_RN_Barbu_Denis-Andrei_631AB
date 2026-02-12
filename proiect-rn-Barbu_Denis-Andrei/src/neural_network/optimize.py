from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV

def find_best_model(X_train, y_train):
    """
    Ruleaza RandomizedSearchCV pentru a gasi cei mai buni hiperparametri.
    """
    print("--- [Neural Network] Start Optimizare Grid Search ---")
    
    # Definim spatiul de cautare
    param_dist = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5]
    }
    
    rf = RandomForestRegressor(random_state=42)
    
    # Configuram cautarea
    random_search = RandomizedSearchCV(
        estimator=rf, 
        param_distributions=param_dist, 
        n_iter=5,      # Numar experimente
        cv=3,          # Cross Validation folds
        verbose=0, 
        random_state=42, 
        n_jobs=1
    )
    
    # Antrenare
    random_search.fit(X_train, y_train)
    
    best_model = random_search.best_estimator_
    print(f"   > Cel mai bun model gasit: {random_search.best_params_}")
    
    return best_model