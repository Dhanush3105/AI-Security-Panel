import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# ---- Step 1: Load or create dataset ----
# Example dataset (for demo; replace with real phishing URL dataset like PhishTank, Kaggle)
data = {
    "url": [
        "http://paypal.login.verify-user.com",
        "https://secure.bankofamerica.com/login",
        "http://192.168.0.1/securelogin",
        "https://accounts.google.com/signin",
        "http://free-vouchers.win-amazon-prizes.com",
        "https://github.com/openai/chatgpt"
    ],
    "label": [1, 0, 1, 0, 1, 0]  # 1 = phishing, 0 = legitimate
}
df = pd.DataFrame(data)

# ---- Step 2: Feature extraction ----
# Simple approach: bag-of-words on URLs
vectorizer = CountVectorizer(analyzer="char_wb", ngram_range=(3, 5))
X = vectorizer.fit_transform(df["url"])
y = df["label"]

# ---- Step 3: Train/test split ----
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# ---- Step 4: Train classifier ----
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# ---- Step 5: Evaluate ----
y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# ---- Step 6: Test with new URLs ----
test_urls = [
    "http://update-paypal-account.com",
    "https://microsoft.com/login",
    "http://secure-appleid-support.com"
]

X_new = vectorizer.transform(test_urls)
predictions = clf.predict(X_new)

for url, pred in zip(test_urls, predictions):
    print(f"{url} --> {'Phishing' if pred == 1 else 'Legitimate'}")
