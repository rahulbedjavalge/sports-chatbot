import os, csv, joblib, random
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATA_PATH = Path("nlp/data/questions.csv")
ART_DIR = Path("nlp/artifacts")
ART_DIR.mkdir(parents=True, exist_ok=True)

# load dataset
X, y = [], []
with open(DATA_PATH, "r", encoding="utf-8") as f:
    rd = csv.DictReader(f)
    for row in rd:
        text = (row["text"] or "").strip()
        intent = (row["intent"] or "").strip()
        if text and intent:
            X.append(text)
            y.append(intent)

if not X:
    raise SystemExit("No training data found in nlp/data/questions.csv")

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# model: TF-IDF + Logistic Regression
model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
    ("clf", LogisticRegression(max_iter=1000, n_jobs=None))
])

model.fit(X_train, y_train)

# evaluate
y_pred = model.predict(X_test)
print("=== Intent Classification Report ===")
print(classification_report(y_test, y_pred, digits=3))

# save
out_path = ART_DIR / "intent_model.pkl"
joblib.dump(model, out_path)
print(f" Saved model  {out_path}")
