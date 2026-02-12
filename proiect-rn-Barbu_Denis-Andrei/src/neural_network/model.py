import joblib
import os

def save_model(model, filepath="models/optimized_model.h5"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"Model salvat la: {filepath}")

def load_model(filepath="models/optimized_model.h5"):
    if os.path.exists(filepath):
        return joblib.load(filepath)
    else:
        return None