import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import random

np.random.seed(42)
random.seed(42)

n = 100_000
fraud_rate = 0.015
n_users = 5000

# Merchant catalog
merchants = [
    ("Jollibee", "food"), ("McDonald's", "food"), ("KFC", "food"), ("Chowking", "food"),
    ("Puregold", "grocery"), ("SM Supermarket", "grocery"), ("Robinsons Supermarket", "grocery"),
    ("Shell", "fuel"), ("Petron", "fuel"), ("Caltex", "fuel"), ("Seaoil", "fuel"),
    ("Lazada", "ecommerce"), ("Shopee", "ecommerce"), ("Zalora PH", "ecommerce"),
    ("Mercury Drug", "pharmacy"), ("Watsons", "pharmacy"),
    ("Bench", "retail"), ("Uniqlo", "retail"), ("H&M", "retail"),
    ("Netflix PH", "entertainment"), ("Spotify PH", "entertainment"), ("YouTube Premium", "entertainment"),
    ("Grab", "transport"), ("Angkas", "transport"), ("JoyRide", "transport"),
    ("LBC Remittance", "remittance"), ("Western Union", "remittance"), ("Palawan Pawnshop", "remittance"),
    ("Meralco", "bills"), ("Maynilad", "bills"), ("PLDT", "bills"), ("Globe", "bills"),
]
merchant_names = [m[0] for m in merchants]
merchant_cats = {m[0]: m[1] for m in merchants}

# Create user profiles
users = []
for _ in range(n_users):
    pref_cats = random.sample(["food", "grocery", "fuel", "ecommerce", "pharmacy", "retail", 
                                "entertainment", "transport", "remittance", "bills"], 
                               k=random.randint(2, 5))
    users.append({
        "user_id": f"USR_{uuid.uuid4().hex[:12].upper()}",
        "pref_cats": pref_cats,
        "mean_amt": np.random.lognormal(6, 0.8),  # ~₱400 median
        "amt_std": np.random.lognormal(4.5, 0.5),
        "pref_hours": list(range(random.randint(6, 10), random.randint(18, 23))),
    })

user_df = pd.DataFrame(users)
user_map = user_df.set_index("user_id").to_dict("index")

# Mark ~8% of users as "compromised" (will have fraud)
compromised_users = set(random.sample(list(user_df["user_id"]), k=int(n_users * 0.08)))

records = []
start_date = datetime(2024, 6, 1)

for i in range(n):
    user_id = random.choice(list(user_map.keys()))
    profile = user_map[user_id]
    
    is_compromised = user_id in compromised_users
    # 30% of compromised user's transactions are fraud
    is_fraud = 1 if (is_compromised and random.random() < 0.30) else 0
    
    if is_fraud:
        # FRAUD: unusual patterns vs user's profile
        # Pick merchant - favor high-risk but can be any
        if random.random() < 0.6:
            merchant = random.choice(["LBC Remittance", "Western Union", "Palawan Pawnshop",
                                       "Lazada", "Shopee", "Zalora PH", "Shell", "Petron"])
        else:
            merchant = random.choice(merchant_names)
        
        # Unusual hour: late night
        hour = random.choice([0, 1, 2, 3, 4, 23, 22])
        
        # Amount: 3x to 15x user's normal mean
        multiplier = np.random.uniform(3.0, 15.0)
        amount = profile["mean_amt"] * multiplier + np.random.normal(0, 200)
        amount = max(500, amount)
        
    else:
        # LEGIT: follows user's profile
        if random.random() < 0.85:
            cat = random.choice(profile["pref_cats"])
            merchant = random.choice([m[0] for m in merchants if m[1] == cat])
        else:
            merchant = random.choice(merchant_names)
        
        # Normal hours
        if random.random() < 0.9:
            hour = random.choice(profile["pref_hours"])
        else:
            hour = random.randint(0, 23)
        
        # Normal amount around user's mean
        amount = np.random.normal(profile["mean_amt"], profile["amt_std"])
        amount = max(10, amount)
    
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    day_offset = random.randint(0, 29)
    ts = start_date + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)
    
    records.append({
        "transaction_id": f"TXN_{uuid.uuid4().hex[:8].upper()}",
        "user_id": user_id,
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "amount": round(amount, 2),
        "merchant": merchant,
        "category": merchant_cats[merchant],
        "is_fraud": is_fraud,
    })

df = pd.DataFrame(records)

# Force exact 1.5% fraud rate
current_fraud = df["is_fraud"].sum()
target_fraud = int(n * fraud_rate)

if current_fraud > target_fraud:
    fraud_idx = df[df["is_fraud"] == 1].index.tolist()
    random.shuffle(fraud_idx)
    flip = fraud_idx[:current_fraud - target_fraud]
    df.loc[flip, "is_fraud"] = 0
else:
    non_idx = df[df["is_fraud"] == 0].index.tolist()
    random.shuffle(non_idx)
    flip = non_idx[:target_fraud - current_fraud]
    df.loc[flip, "is_fraud"] = 1

print(f"Generated {n} transactions")
print(f"Fraud count: {df['is_fraud'].sum()} ({df['is_fraud'].mean()*100:.2f}%)")
print("\nFraud by category:")
print(df.groupby("category")["is_fraud"].mean().sort_values(ascending=False))
print("\nFraud by hour:")
print(df.groupby(df["timestamp"].str[11:13].astype(int))["is_fraud"].mean().sort_values(ascending=False).head())
print("\nSample:")
print(df.head())
df.to_csv("data/transactions.csv", index=False)
print("\nSaved to data/transactions.csv")