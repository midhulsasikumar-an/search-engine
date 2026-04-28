import json
import re
from nltk.stem import WordNetLemmatizer
import nltk

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()

stop_words = {
    "is", "are", "the", "a", "an", "in", "on", "at",
    "to", "for", "of", "and", "or", "they", "this", "that"
}

def tokenize(text):
    text = text.lower()
    words = re.findall(r'\b[a-z]+\b', text)
    lemmatized = [lemmatizer.lemmatize(word) for word in words]
    filtered = [word for word in lemmatized if word not in stop_words]
    return filtered

with open("data/pages.json", "r", encoding="utf-8") as f:
    pages = json.load(f)    

inverted_index = {}

for i, page in enumerate(pages):
    words = tokenize(page.get("text", ""))

    for word in set(words):  # use set to avoid duplicates in same doc
        if len(word) < 3 and word not in {"ai", "ml", "nlp"}:  # keep short tech terms
            continue
        if word not in inverted_index:
            inverted_index[word] = set()

        inverted_index[word].add(i)  # store doc ID

total_docs = len(pages)

filtered_index = {}
for word, doc_set in inverted_index.items():
    if len(doc_set) <= 0.8 * total_docs:
        filtered_index[word] = list(doc_set)

with open("data/inverted_index.json", "w", encoding="utf-8") as f:
    json.dump(filtered_index, f, indent=2)  
    print(f"Completed : Built inverted index with {len(filtered_index)} words.")