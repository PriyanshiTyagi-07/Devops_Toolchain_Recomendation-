import joblib
import pandas as pd

# Load the saved model and encoders
best_model = joblib.load('best_model.joblib')
label_encoders = joblib.load('label_encoders.joblib')
y_encoder = joblib.load('y_encoder.joblib')

print("Loaded the best model.")

def preprocess_input(data):
    """
    This function encodes the input data using the pre-saved label encoders.
    It will handle unseen labels by assigning them to the nearest known label.
    """
    for column in data.columns:
        le = label_encoders[column]
        try:
            # Attempt to transform the data using the LabelEncoder
            data[column] = le.transform(data[column])
        except ValueError as e:
            unseen_labels = set(data[column]) - set(le.classes_)
            if unseen_labels:
                print(f"Warning: Unseen labels {unseen_labels} in column '{column}'. Assigning default value.")
                # Assign default value or any known label (e.g., most frequent or first class)
                data[column] = data[column].apply(lambda x: le.transform([x])[0] if x in le.classes_ else le.transform([le.classes_[0]])[0])
    return data

def make_prediction(input_data):
    input_df = pd.DataFrame([input_data], columns=['Team Size', 'Release Frequency', 'Compliance', 'Scalability', 'Project Size', 'Project Length', 'Security Level'])
    input_df = preprocess_input(input_df)  # Preprocess the input
    prediction = best_model.predict(input_df)
    return y_encoder.inverse_transform(prediction)[0]

# Example input data (modify this as per your use case)
input_data = {
    'Team Size': 'Medium',
    'Release Frequency': 'Daily',
    'Compliance': 'High',
    'Scalability': 'Auto-scaling',
    'Project Size': 'Small',
    'Project Length': 'Short',
    'Security Level': 'Strict'
}

# Make prediction
predicted_tool = make_prediction(input_data)
print(f"Predicted DevOps Tool: {predicted_tool}")
