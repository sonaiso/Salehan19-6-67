"""Demo: Thing knowledge base."""
import sys
sys.path.insert(0, "src")
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data

store = PriorKnowledgeStore()
load_seed_data(store)

for thing in store.things.all():
    ar_name = thing.names.get("ar", "?")
    print(f"{ar_name}: {thing.haqiqa} (certainty={thing.certainty.score:.2f})")
