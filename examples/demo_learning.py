"""Demo: Learning from evidence."""
import sys
sys.path.insert(0, "src")
from mcd.engines.decoder import MinimalCognitiveDecoder
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data

store = PriorKnowledgeStore()
load_seed_data(store)
decoder = MinimalCognitiveDecoder(store=store, allow_learning=True)

result = decoder.decode("النار تحرق", mode="learner")
print(f"Learning actions: {len(result.learning_actions)}")
for action in result.learning_actions:
    print(f"  {action}")
