import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
from flask import Flask, request, render_template

# Data Preprocessing and Feature Extraction
def preprocess_data(file_path):
    data_renamed = pd.read_csv(file_path)
    data_renamed['engagement'] = data_renamed['interaction_count'] > data_renamed['interaction_count'].mean()
    features = data_renamed[['feature_1', 'feature_2', 'time_spent']]
    labels = data_renamed['engagement']
    return train_test_split(features, labels, test_size=0.3, random_state=42)

# Model Training
def train_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

# Model Evaluation
def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions)
    return accuracy, report

# Save Model
def save_model(model, model_file):
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)

# Load Model
def load_model(model_file):
    with open(model_file, 'rb') as f:
        return pickle.load(f)

# Web App Setup
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    features = [float(x) for x in request.form.values()]
    model = load_model('user_engagement_model.pkl')
    prediction = model.predict([features])
    return render_template('index.html', prediction=f'Engaged: {prediction[0]}')

if __name__ == '__main__':
    X_train, X_test, y_train, y_test = preprocess_data('user_interaction_data.csv')
    model = train_model(X_train, y_train)
    accuracy, report = evaluate_model(model, X_test, y_test)
    print(f'Model Accuracy: {accuracy}\nClassification Report:\n{report}')
    save_model(model, 'user_engagement_model.pkl')
    app.run(debug=True)
