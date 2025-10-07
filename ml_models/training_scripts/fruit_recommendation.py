# Fruit Recommendation Model
# This is a simple ML pipeline for demonstration. Replace with real data and logic as needed.

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Sample data: Replace with real dataset
# Columns: fruit, disease, recommended (1=yes, 0=no)
data = pd.DataFrame({
    'fruit': ['apple', 'banana', 'blueberry', 'avocado', 'kiwi'],
    'disease': ['diabetes', 'heart', 'memory', 'heart', 'immune'],
    'recommended': [1, 1, 1, 1, 1]
})

# Encode categorical variables
X = pd.get_dummies(data[['fruit', 'disease']])
y = data['recommended']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))

# Save model
joblib.dump(model, '../saved_models/fruit_recommendation.pkl')
