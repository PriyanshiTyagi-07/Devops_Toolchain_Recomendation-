import pandas as pd
import warnings  # Import warnings module
import joblib  # Import joblib for saving the model
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import StratifiedKFold, GridSearchCV

# Suppress all warnings
warnings.filterwarnings("ignore")

# Step 1: Load the dataset
df = pd.read_csv('devops_tool_recommendations.csv')

# Step 2: Preprocess the data (Split features and target)
X = df[['Team Size', 'Release Frequency', 'Compliance', 'Scalability', 'Project Size', 'Project Length', 'Security Level']]
y = df['Recommended Tools']

# Step 3: Feature Encoding
label_encoders = {}
for column in X.columns:
    le = LabelEncoder()
    X.loc[:, column] = le.fit_transform(X[column])  # Using .loc to avoid SettingWithCopyWarning
    label_encoders[column] = le  # Save the encoder for later use

# Encode target as well
y_encoder = LabelEncoder()
y = y_encoder.fit_transform(y)

# Step 4: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 5: Define the models and hyperparameters
models = {
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42),
    'SVM': SVC(random_state=42)
}

# Define hyperparameters for each model
param_grids = {
    'Decision Tree': {
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 10, 20],
        'min_samples_leaf': [1, 5, 10]
    },
    'Random Forest': {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 10],
        'min_samples_leaf': [1, 5]
    },
    'SVM': {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto']
    }
}

# Use StratifiedKFold for cross-validation to handle class imbalance
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Step 6: Train models using GridSearchCV and compare results
best_models = {}
for model_name, model in models.items():
    print(f"\nTraining {model_name}...")
    grid_search = GridSearchCV(model, param_grids[model_name], cv=skf, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    best_models[model_name] = best_model

# Step 7: Make predictions and evaluate each model
best_model_name = None
best_accuracy = 0
best_model = None

for model_name, model in best_models.items():
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Check if this model has the best accuracy
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model_name = model_name
        best_model = model
    
    # Calculate precision, recall, and F1-Score
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=1)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=1)
    f1 = f1_score(y_test, y_pred, average='weighted')

    # Print evaluation metrics for each model
    print(f"\n{model_name} Results:")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1-Score: {f1:.2f}")

# After Step 7: Print the best parameters and save the best model
for model_name, model in best_models.items():
    print(f"\n{model_name} Best Parameters: {model.get_params()}")
    
# Save the best model
joblib.dump(best_model, f'best_model.joblib')
print(f"Best model '{best_model_name}' saved.")


# Step 8: Print the best model based on accuracy
print(f"\nBest Model: {best_model_name} with Accuracy: {best_accuracy:.2f}")

# Step 9: Save the best model using joblib
joblib.dump(label_encoders, 'label_encoders.joblib')
joblib.dump(y_encoder, 'y_encoder.joblib')
print("Label encoders and target encoder saved.")

