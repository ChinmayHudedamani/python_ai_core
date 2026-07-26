from typing import Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

TRAINING_DATA = [
    ("What is the cost of clear aligners invisalign price list package rate discount emi", "PRICING"),
    ("kitna kharcha hoga dam kitne ka hai kitni fees hai discount emi option hai", "PRICING"),
    ("how much does invisalign dental implants cost in koramangala price list", "PRICING"),
    ("how much do traditional metal ceramic braces cost price list package", "PRICING"),
    ("how much for teeth cleaning scaling polishing cost price", "PRICING"),
    ("how much is composite tooth filling cavity treatment cost", "PRICING"),
    ("how much is tooth extraction wisdom tooth removal surgery price", "PRICING"),
    ("how much is laser teeth whitening bleaching price cost", "PRICING"),
    ("how much is initial consultation checkup doctor fee", "PRICING"),
    ("I want to book an appointment for saturday at 11 am confirm my slot schedule visit", "SLOT_BOOKING"),
    ("can i schedule a visit for tomorrow morning slot available lock appointment time", "SLOT_BOOKING"),
    ("appointment book karna hai saturday 11 baje slot milega kya timing fix kardo", "SLOT_BOOKING"),
    ("where is your clinic located in koramangala landmark map link directions to reach", "LOCATION"),
    ("clinic ka address kya hai koramangala me kaha hai landmark battery bus stop empire", "LOCATION"),
    ("what time does clinic open and close in koramangala saturday sunday timings hours", "TIMINGS"),
    ("kab khula rehta hai Sunday ko khula hai kya morning 9 am evening time", "TIMINGS"),
    ("who is the lead dentist doctor qualifications experience BDS MDS degree chinmay hudedamani", "DOCTOR_INFO"),
    ("doctor kaun hai kitna experience hai degree kya hai specialist dentist doctor profile", "DOCTOR_INFO"),
    ("can i take painkillers tooth pain medicine tablet name prescription for toothache", "PRESCRIPTION_ATTEMPT"),
    ("dard ki dawai batao painkiller konsi lu tablet ka naam antibiotic prescribe karo", "PRESCRIPTION_ATTEMPT"),
    ("profuse bleeding from gums accident tooth broken chest pain emergency clinical trauma urgent", "EMERGENCY")
]


class ScikitLearnMLIntentEngine:
    """Enterprise Scikit-Learn TF-IDF + Naive Bayes ML Intent Classifier."""

    def __init__(self):
        texts, labels = zip(*TRAINING_DATA)
        self.model = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 2), stop_words='english'),
            MultinomialNB()
        )
        self.model.fit(texts, labels)

    def classify(self, text: str) -> Tuple[str, float]:
        """Classifies input query and returns (Predicted_Intent, Max_Probability)."""
        probs = self.model.predict_proba([text])[0]
        max_idx = probs.argmax()
        predicted_class = self.model.classes_[max_idx]
        confidence = round(float(probs[max_idx]), 4)
        return (predicted_class if confidence > 0.20 else "GENERAL_INQUIRY", confidence)


if __name__ == "__main__":
    engine = ScikitLearnMLIntentEngine()
    test_queries = [
        "What is the cost of clear aligners?",
        "How much is teeth cleaning?",
        "I want to book a slot for Saturday 11 AM",
        "Where is your clinic located in Koramangala?"
    ]
    for q in test_queries:
        intent, prob = engine.classify(q)
        print(f"Query: '{q}' -> ML Intent: {intent} (Prob: {prob})")
