
import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# 1. Load dataset
df = pd.read_csv("data/processed/cleaned_emails.csv")

X = df["Email Text"].astype(str)
y = df["label"]

# 2. Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# 3. TF-IDF feature extraction
tfidf = TfidfVectorizer(
    max_features=10000,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True
)

X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

print("TF-IDF training shape:", X_train_tfidf.shape)

# 4. Define models
models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ),

    "Multinomial Naive Bayes": MultinomialNB(),

    "Linear SVM": LinearSVC(
        class_weight="balanced",
        random_state=42
    )
}

# 5. Train and evaluate
results = []
os.makedirs("models/saved", exist_ok=True)

for name, model in models.items():

    print("\nTraining:", name)

    model.fit(X_train_tfidf, y_train)
    predictions = model.predict(X_test_tfidf)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    print("Accuracy:", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1 Score:", round(f1, 4))

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions,
        target_names=["Safe Email", "Phishing Email"],
        zero_division=0
    ))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    # Save each trained model
    joblib.dump(
        model,
        f"models/saved/{name.lower().replace(' ', '_')}.pkl"
    )

# 6. Compare models
results_df = pd.DataFrame(results)
print("\nMODEL COMPARISON")
print(results_df.to_string(index=False))

results_df.to_csv(
    "models/saved/model_comparison.csv",
    index=False
)

# Save TF-IDF vectorizer
joblib.dump(tfidf, "models/saved/tfidf_vectorizer.pkl")

print("\nAll models trained and saved successfully!")
