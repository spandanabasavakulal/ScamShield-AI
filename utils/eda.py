
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

# Load cleaned dataset
df = pd.read_csv("data/processed/cleaned_emails.csv")

os.makedirs("assets/eda", exist_ok=True)

# Calculate email length
df["email_length"] = df["Email Text"].astype(str).apply(len)

# 1. Class distribution
plt.figure(figsize=(7, 5))
df["Email Type"].value_counts().plot(
    kind="bar",
    title="Email Class Distribution"
)
plt.xlabel("Email Type")
plt.ylabel("Number of Emails")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("assets/eda/class_distribution.png")
plt.close()

# 2. Email length distribution
plt.figure(figsize=(8, 5))

for label in ["Safe Email", "Phishing Email"]:
    df[df["Email Type"] == label]["email_length"].clip(
        upper=df["email_length"].quantile(0.99)
    ).hist(alpha=0.5, bins=40, label=label)

plt.title("Email Length Distribution")
plt.xlabel("Characters per Email")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig("assets/eda/email_length.png")
plt.close()

# 3. Word clouds
for label, filename in [
    ("Phishing Email", "phishing_wordcloud.png"),
    ("Safe Email", "safe_wordcloud.png")
]:
    text = " ".join(
        df[df["Email Type"] == label]["Email Text"].astype(str)
    )

    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        max_words=100
    ).generate(text)

    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(label + " Word Cloud")
    plt.tight_layout()
    plt.savefig(f"assets/eda/{filename}")
    plt.close()

print("EDA completed successfully!")

print("\nGenerated files:")
for file in os.listdir("assets/eda"):
    print(file)
