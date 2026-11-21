import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

df = pd.read_csv("Phishing_URL_Dataset.csv") 

print("Dataset Shape:", df.shape)
print("\nFirst 5 Records:")
print(df.head())

print("\nDataset Information:")
print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nTotal Missing Values:")
print(df.isnull().sum().sum())

print("\nDuplicate Records:", df.duplicated().sum())
df = df.drop_duplicates()

# Remove records without target labels
df = df.dropna(subset=["label"])

# Convert target into integer
df["label"] = df["label"].astype(int)

#DESCRIPTIVE STATISTICS
print("\nDescriptive Statistics:")
print(df.describe())

#CLASS DISTRIBUTION
print("\nClass Counts:")
print(df["label"].value_counts())
print("\nClass Percentages:")
print(df["label"].value_counts(normalize=True) * 100)
plt.figure(figsize=(7, 5))
sns.countplot(data=df, x="label")
plt.title("Class Distribution of URL Dataset")
plt.xlabel("URL Class (0 = Phishing, 1 = Legitimate)")
plt.ylabel("Number of Records")
plt.savefig("class_distribution.png")
plt.show()

#CHECK CLASS IMBALANCE
counts = df["label"].value_counts()
imbalance_ratio = counts.max() / counts.min()
print("\nClass Imbalance Ratio:", imbalance_ratio)
if imbalance_ratio < 1.5:
    print("Classes are relatively balanced.")
else:
    print("Dataset has class imbalance.")

#FEATURE HISTOGRAMS
features = [
    "URLLength",
    "NoOfSubDomain",
    "NoOfLettersInURL",
    "NoOfExternalRef"
]
for feature in features:
    if feature in df.columns:
        plt.figure(figsize=(8, 5))
        sns.histplot(
            data=df,
            x=feature,
            hue="label",
            bins=30,
            kde=True,
            element="step"
        )
        plt.title("Histogram of " + feature)
        plt.xlabel(feature)
        plt.ylabel("Frequency")
        plt.savefig(feature + "_histogram.png")
        plt.show()

#PEARSON CORRELATION
# Select numerical features only
numeric_df = df.select_dtypes(include="number")
# Remove identifier columns if present
numeric_df = numeric_df.drop(
    columns=["FILENAME"],
    errors="ignore"
)
pearson_corr = numeric_df.corr(method="pearson")
plt.figure(figsize=(16, 12))
sns.heatmap(
    pearson_corr,
    cmap="coolwarm",
    annot=False,
    vmin=-1,
    vmax=1
)
plt.title("Pearson Correlation Heatmap")
plt.tight_layout()
plt.savefig("pearson_heatmap.png")
plt.show()

# Save Pearson values
pearson_corr.to_csv("pearson_correlation.csv")

#SPEARMAN CORRELATION
spearman_corr = numeric_df.corr(method="spearman")
plt.figure(figsize=(16, 12))
sns.heatmap(
    spearman_corr,
    cmap="coolwarm",
    annot=False,
    vmin=-1,
    vmax=1
)
plt.title("Spearman Correlation Heatmap")
plt.tight_layout()
plt.savefig("spearman_heatmap.png")
plt.show()

# Save Spearman values
spearman_corr.to_csv("spearman_correlation.csv")

#CORRELATION WITH TARGET LABEL
print("\nPearson Correlation with Label:")
print(
    pearson_corr["label"]
    .drop("label")
    .sort_values(ascending=False)
)
print("\nSpearman Correlation with Label:")
print(
    spearman_corr["label"]
    .drop("label")
    .sort_values(ascending=False)
)

df.to_csv("cleaned_URL_Dataset.csv", index=False)


