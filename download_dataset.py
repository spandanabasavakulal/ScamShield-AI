
import kagglehub
import shutil
import os

# Kaggle dataset identifier
dataset_id = "subhajournal/phishingemails"

# Download dataset directly into project
download_path = kagglehub.dataset_download(
    dataset_id,
    output_dir="./data/raw"
)

print("Dataset downloaded successfully!")
print("Location:", download_path)

print("\nFiles downloaded:")
for root, dirs, files in os.walk(download_path):
    for file in files:
        print(os.path.join(root, file))
