from nltk.metrics.distance import edit_distance

class Generator:
    def __init__(self, path="dialogs.txt"):
        self.pairs = []

        with open(path, encoding="utf-8") as f:
            for line in f:
                q, a = line.strip().split("|")
                self.pairs.append((q, a))

    def get_response(self, text):
        best = None
        best_score = 999

        for q, a in self.pairs:
            dist = edit_distance(text.lower(), q.lower())
            norm = dist / max(len(text), len(q))

            if norm < best_score:
                best_score = norm
                best = a

        if best_score > 0.4:
            return None

        return best