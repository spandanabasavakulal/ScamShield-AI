
import joblib
import os

# Load trained model and vectorizer
MODEL_PATH = "models/saved/linear_svm.pkl"
VECTORIZER_PATH = "models/saved/tfidf_vectorizer.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Trained Linear SVM model not found.")

if not os.path.exists(VECTORIZER_PATH):
    raise FileNotFoundError("TF-IDF vectorizer not found.")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def predict_email(email_text):

    if not isinstance(email_text, str) or not email_text.strip():
        return {
            "prediction": "Invalid Input",
            "message": "Please enter a valid email message."
        }

    # Convert email text into TF-IDF features
    email_features = vectorizer.transform([email_text])

    # Predict email class
    prediction = model.predict(email_features)[0]

    if prediction == 1:
        result = "Phishing Email"
        message = "Warning: This message may be a phishing attempt."
    else:
        result = "Safe Email"
        message = "No phishing pattern detected by the model."

    return {
        "prediction": result,
        "message": message
    }


if __name__ == "__main__":

    sample_email = """
    Congratulations! You have won a cash prize.
    Click this link immediately to claim your reward.
    """

    result = predict_email(sample_email)

    print("Prediction:", result["prediction"])
    print("Analysis:", result["message"])
