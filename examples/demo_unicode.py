"""Demo: Unicode vectorization of Arabic characters."""
import sys
sys.path.insert(0, "src")
from mcd.engines.unicode_vectorizer import UnicodeVectorizer

vectorizer = UnicodeVectorizer()
for char in "كتب":
    vec = vectorizer.vectorize(char)
    print(f"{char}: arabic={vec.is_arabic}, letter={vec.is_letter}, root_candidate={vec.root_candidate_score:.2f}")
