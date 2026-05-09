"""Demo: Cognitive reasoning."""
import sys
sys.path.insert(0, "src")
from mcd.engines.decoder import MinimalCognitiveDecoder
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data

store = PriorKnowledgeStore()
load_seed_data(store)
decoder = MinimalCognitiveDecoder(store=store)

texts = ["النار تحرق", "كتب الطالب الدرس", "كاتب", "علم"]
for text in texts:
    result = decoder.decode(text)
    print(f"\n{'='*50}")
    print(f"Input: {text}")
    print(f"Normalized: {result.normalized}")
    print(f"Answer: {result.answer}")
    print(f"Claims: {len(result.claims)}, Relations: {len(result.relations)}")
