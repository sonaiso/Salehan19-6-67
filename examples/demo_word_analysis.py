"""Demo: Word morphological analysis."""
import sys
sys.path.insert(0, "src")
from mcd.engines.pattern_matcher import PatternMatcher
from mcd.engines.role_inferer import RoleInferer

matcher = PatternMatcher()
inferer = RoleInferer()

for word in ["كاتب", "مكتوب", "كتابة", "يكتب"]:
    matches = matcher.match(word)
    roles = inferer.infer_roles(word)
    print(f"\n{word}:")
    print(f"  Patterns: {[m['pattern'] for m in matches[:2]]}")
    print(f"  Top roles: {[(c, rv.top_role()) for c, rv in roles[:3]]}")
