
import pandas as pd

# Load dataset
file_path = "data/raw/Phishing_Email.csv"
df = pd.read_csv(file_path)

# Basic information
print("\n========== DATASET OVERVIEW ==========")
print("Shape:", df.shape)
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# Column names
print("\n========== COLUMN NAMES ==========")
print(df.columns.tolist())

# First five records
print("\n========== FIRST 5 RECORDS ==========")
print(df.head())

# Data types
print("\n========== DATA TYPES ==========")
print(df.dtypes)

# Missing values
print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

# Duplicate records
print("\n========== DUPLICATE RECORDS ==========")
print("Duplicates:", df.duplicated().sum())

# Class distribution
print("\n========== CLASS DISTRIBUTION ==========")

for col in df.select_dtypes(include="object").columns:
    if df[col].nunique() <= 10:
        print(f"\nColumn: {col}")
        print(df[col].value_counts(dropna=False))

