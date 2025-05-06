import os
import csv

# Path to your image dataset
base_path = "grass-no-grass-dataset"

# Output CSV path
csv_path = "train.csv"

# Open the CSV file for writing
with open(csv_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["image", "label"])  # header

    # Loop through both class folders
    for label in ["grass", "nograss"]:
        folder = os.path.join(base_path, label)
        for img in os.listdir(folder):
            if img.lower().endswith((".jpg", ".jpeg", ".png")):
                writer.writerow([f"{label}/{img}", label])

print(f"Done! CSV saved to {csv_path}")
