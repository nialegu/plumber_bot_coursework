import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
        self.model = LinearSVC()

    def train(self, path="intents.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = []
        labels = []

        for intent, phrases in data.items():
            for phrase in phrases:
                texts.append(phrase)
                labels.append(intent)

        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)

    def predict(self, text):
        X = self.vectorizer.transform([text])
        score = self.model.decision_function(X).max()

        if score < 0.3:
            return "unknown"

        return self.model.predict(X)[0]