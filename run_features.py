import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "src"))

from features.engineering import engineer_features

def main():
    df = pd.read_csv("data/transactions.csv")
    df = engineer_features(df)
    df.to_csv("data/featured_transactions.csv", index=False)
    print("Done. Shape:", df.shape)
    print(df.head())

if __name__ == "__main__":
    main()
