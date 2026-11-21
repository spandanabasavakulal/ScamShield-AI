
import pandas as pd
import os

def clean_dataset():

    input_path = "data/raw/Phishing_Email.csv"
    df = pd.read_csv(input_path)

    print("Original shape:", df.shape)

    # Remove unnecessary index column
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")

    # Remove missing and empty email texts
    df = df.dropna(subset=["Email Text"])
    df["Email Text"] = df["Email Text"].astype(str).str.strip()
    df = df[df["Email Text"] != ""]

    # Identify conflicting duplicate email texts
    label_counts = df.groupby("Email Text")["Email Type"].nunique()

    conflicting_texts = label_counts[label_counts > 1].index

    print("\nConflicting email groups:", len(conflicting_texts))

    # Remove all rows belonging to conflicting groups
    df = df[~df["Email Text"].isin(conflicting_texts)].copy()

    # Remove remaining duplicate email texts
    df = df.drop_duplicates(subset=["Email Text"])

    # Encode labels
    label_mapping = {
        "Safe Email": 0,
        "Phishing Email": 1
    }

    df["label"] = df["Email Type"].map(label_mapping)

    # Remove invalid labels
    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)

    # Save processed dataset
    os.makedirs("data/processed", exist_ok=True)

    output_path = "data/processed/cleaned_emails.csv"
    df.to_csv(output_path, index=False)

    print("\nFinal dataset shape:", df.shape)

    print("\nClass distribution:")
    print(df["Email Type"].value_counts())

    print("\nRemaining duplicate texts:",
          df["Email Text"].duplicated().sum())

    print("\nRemaining conflicting groups:",
          (df.groupby("Email Text")["Email Type"].nunique() > 1).sum())

    print("\nDataset saved:", output_path)


if __name__ == "__main__":
    clean_dataset()
