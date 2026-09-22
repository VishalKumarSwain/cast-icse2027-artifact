import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Function for data exploration
def explore_data(df_renamed):
    print("First 5 rows of the dataset:")
    print(df_renamed.head())
    print("\nSummary of the dataset:")
    print(df_renamed.describe())
    
# Function to clean data
def clean_data(df_renamed):
    df_renamed = df_renamed.dropna()  # Remove missing values
    return df_renamed

# Function to encode categorical variables
def encode_data(df_renamed):
    df_renamed = pd.get_dummies(df_renamed, drop_first=True)
    return df_renamed

# Function to split data into features and target
def split_data(df_renamed, target_column):
    X = df_renamed.drop(target_column, axis=1)
    y = df_renamed[target_column]
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Function to train the model
def train_model(X_train, y_train):
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    return model

# Function to evaluate the model
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    print("\nAccuracy Score:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Main function to execute the workflow
def main():
    # Load the dataset
    df_renamed = pd.read_csv('research_data.csv')  # Ensure the dataset filename is correct

    # Data Exploration
    explore_data(df_renamed)

    # Data Cleaning
    df_renamed = clean_data(df_renamed)

    # Encode Categorical Variables
    df_renamed = encode_data(df_renamed)

    # Split data
    X_train, X_test, y_train, y_test = split_data(df_renamed, target_column='outcome')

    # Train the model
    model = train_model(X_train, y_train)

    # Evaluate the model
    evaluate_model(model, X_test, y_test)

if __name__ == '__main__':
    main()
