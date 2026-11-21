
import pandas as pd

raw = pd.read_csv("data/raw/Phishing_Email.csv")
cleaned = pd.read_csv("data/processed/cleaned_emails.csv")

print("Original records:", len(raw))
print("Cleaned records:", len(cleaned))

# Check duplicate email texts
raw = raw.dropna(subset=["Email Text"])

duplicates = raw[
    raw.duplicated(subset=["Email Text"], keep=False)
]

print("\nDuplicate email records:", len(duplicates))

# Check whether identical email texts have conflicting labels
conflicts = (
    duplicates.groupby("Email Text")["Email Type"]
    .nunique()
)

conflicts = conflicts[conflicts > 1]

print("Conflicting duplicate email groups:", len(conflicts))

print("\nCleaned class distribution:")
print(cleaned["Email Type"].value_counts())
