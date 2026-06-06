import os
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from django.conf import settings

# Path where the model will be stored
MODEL_DIR = os.path.join(settings.BASE_DIR, 'analytics', 'data')
MODEL_PATH = os.path.join(MODEL_DIR, 'performance_model.pkl')
CSV_PATH = os.path.join(settings.BASE_DIR, 'employee_data.csv')

def train_ai_model():
    """
    Trains the RandomForestClassifier using the dataset in employee_data.csv
    and serializes the trained model to a pickle file.
    """
    # Create the directories if they don't exist
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Load training data
    if not os.path.exists(CSV_PATH):
        # Fallback to write CSV if missing
        with open(CSV_PATH, 'w') as f:
            f.write("attendance,task_completion,rating,performance\n")
            f.write("95,90,4.8,Excellent\n")
            f.write("88,85,4.0,Good\n")
            f.write("70,65,3.2,Average\n")
            f.write("55,50,2.5,Poor\n")

    data = pd.read_csv(CSV_PATH)
    
    X = data[['attendance', 'task_completion', 'rating']]
    y = data['performance']
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
        
    return model

def load_or_train_model():
    """
    Loads the persisted model from disk, or trains it first if it doesn't exist.
    """
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception:
            # If load fails (e.g., version mismatch), retrain
            return train_ai_model()
    else:
        return train_ai_model()

def predict_performance_grade(attendance, task_completion, rating):
    """
    Predicts the performance classification grade ('Excellent', 'Good', 'Average', 'Poor')
    based on the attendance, task completion, and rating features.
    """
    model = load_or_train_model()
    
    # Ensure inputs are floats
    try:
        attendance = float(attendance)
        task_completion = float(task_completion)
        rating = float(rating)
    except (TypeError, ValueError):
        return "Unknown"
        
    # Standard format: [[attendance, task_completion, rating]]
    prediction = model.predict([[attendance, task_completion, rating]])
    return prediction[0]
