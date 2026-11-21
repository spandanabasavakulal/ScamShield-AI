
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.metrics import confusion_matrix

# Load results
results = pd.read_csv("models/saved/model_comparison.csv")

os.makedirs("assets/evaluation", exist_ok=True)

# 1. Model comparison
metrics = ["Accuracy", "Precision", "Recall", "F1 Score"]

for metric in metrics:
    plt.figure(figsize=(8, 5))
    plt.bar(results["Model"], results[metric])
    plt.title(f"Model Comparison - {metric}")
    plt.ylabel(metric)
    plt.ylim(0, 1.05)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(f"assets/evaluation/{metric.lower().replace(' ', '_')}.png")
    plt.close()

# 2. Linear SVM confusion matrix
df = pd.read_csv("data/processed/cleaned_emails.csv")

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import joblib

X = df["Email Text"].astype(str)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

tfidf = joblib.load("models/saved/tfidf_vectorizer.pkl")
model = joblib.load("models/saved/linear_svm.pkl")

X_test_tfidf = tfidf.transform(X_test)
predictions = model.predict(X_test_tfidf)

cm = confusion_matrix(y_test, predictions)

plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Safe", "Phishing"],
    yticklabels=["Safe", "Phishing"]
)
plt.title("Linear SVM Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")
plt.tight_layout()
plt.savefig("assets/evaluation/linear_svm_confusion_matrix.png")
plt.close()

print("Evaluation graphs generated successfully!")
