"""
Live end-to-end test — Bayani Knowledge System
Run: PYTHONPATH=src python3 Salehan19-6-67/live_test.py
"""
import sys, os

# Allow get_wazn / match_wazn to be imported from the Salehan19-6-67 directory
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)

from mcd.nabhani.nabhani_decoder import NabhaniDecoder
from mcd.fractal_kernel.answer_scorer import AnswerScorer, AnswerVerdict
from mcd.nabhani.pipeline_registry import PipelineRegistry, LayerGroup, LayerResult
from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker
from mcd.knowledge.mishkat_root_lookup import lookup_root

# get_wazn lives alongside live_test.py (not inside src/)
try:
    from get_wazn import get_wazn, load_db
    _AWZAN_DB = load_db(os.path.join(_THIS_DIR, "data", "awzan_cleaned.csv"))
    _WAZN_OK  = True
except Exception as _e:
    _WAZN_OK  = False
    _WAZN_ERR = str(_e)


def wazn_line(word: str) -> str:
    """Return a compact wazn+root string for one vowelized word."""
    if not _WAZN_OK:
        return f"[get_wazn unavailable: {_WAZN_ERR}]"
    result = get_wazn(word)
    if not result:
        return f"{word} → (لا يوجد وزن)"
    root_str = "-".join(result["root"]) if result["root"] else "؟"
    return f"{word} → وزن: {result['wazn']}  جذر: ({root_str})"

SEP  = "─" * 64
SEP2 = "═" * 64

def verdict_label(v):
    return {"certificate": "✅ CERTIFICATE", "hypothesis": "⚠️  HYPOTHESIS",
            "zero": "❌ ZERO"}.get(v, v)

# Each entry: (arabic_text, gloss, [vowelized_key_words_for_wazn_analysis])
SENTENCES = [
    ("العلم نور",
     "Knowledge is light",
     ["عِلْم", "نُور"]),

    ("الكاتب يكتب الكتاب",
     "The writer writes the book",
     ["كَاتِب", "يَكْتُب", "كِتَاب"]),

    ("استخرج المعدن من الأرض",
     "He extracted the mineral from the earth",
     ["اسْتَخْرَجَ", "مَعْدَن"]),

    ("الفاعل مرفوع",
     "The subject is nominative (irab claim)",
     ["فَاعِل", "مَرْفُوع"]),

    ("هذا حرام بالتأكيد",
     "This is definitely forbidden (shari claim without evidence)",
     ["حَرَام"]),
]

decoder = NabhaniDecoder()
scorer  = AnswerScorer()
linker  = MorphosemanticTraceLinker()

print(SEP2)
print("  LIVE END-TO-END TEST — Bayani Knowledge System")
print(SEP2)

for arabic_text, gloss, vowelized_tokens in SENTENCES:
    print(f"\n{SEP}")
    print(f"  INPUT : {arabic_text}")
    print(f"  GLOSS : {gloss}")
    print(SEP)

    words = arabic_text.split()
    roots = [f"{w}→{r}" for w in words if (r := lookup_root(w))]
    print(f"  Layer 1 roots    : {' | '.join(roots) if roots else '(none found)'}")

    # ── get_wazn morphological pattern analysis ────────────────────────────
    print(f"  Wazn analysis    :")
    for vw in vowelized_tokens:
        print(f"    {wazn_line(vw)}")

    try:
        bundle = linker.link(words[0])
        g = bundle.folded_word_graph
        print(f"  Pattern linker   : word={words[0]}  root={g.selected_root}  pattern={g.selected_pattern}")
    except Exception as e:
        print(f"  Pattern linker   : {e}")

    result    = decoder.decode(arabic_text)
    domain    = result["domain"]
    rational  = result["rational_judgment"]
    certainty = result["certainty"]
    fake      = result["fake_evidence_report"]
    dal       = result["dal_madlul"]
    ep_status = result["epistemic_status"]

    print(f"  Domain           : {domain['judgment_type']}  ({domain['status']})")
    print(f"  Rational judge   : {rational['status']}  — {rational.get('certainty_hint','')}")
    print(f"  MCD certainty    : {certainty['score']:.2f}  ({certainty['level']})")
    print(f"  Fake evidence    : {'YES ⚠' if fake['has_fake_evidence'] else 'none'}")
    print(f"  Epistemic status : {ep_status}")
    grounded = sum(1 for d in dal if "grounded" in d.get("grounding_status", ""))
    print(f"  Dal-madlul       : {grounded}/{len(dal)} grounded")

    can_reason  = domain.get("can_reason_without_revelation", True)
    ev_strength = float(rational.get("evidence_strength", certainty["score"]))
    inf_val     = 1.0 if rational["status"] == "accepted" else 0.5 if rational["status"] == "probable" else 0.2
    sem_val     = grounded / len(dal) if dal else certainty["score"]
    hall_risk   = 0.80 if fake["has_fake_evidence"] else 0.0

    answer = scorer.score(
        reality_match        = certainty["score"],
        linguistic_coherence = 0.85 if can_reason else 0.40,
        evidence_strength    = ev_strength,
        semantic_validity    = sem_val,
        inference_validity   = inf_val,
        certainty_clarity    = certainty["score"],
        hallucination_risk   = hall_risk,
    )

    print(f"\n  AnswerScore dims:")
    print(f"    reality_match        = {answer.reality_match:.2f}  × 0.25")
    print(f"    linguistic_coherence = {answer.linguistic_coherence:.2f}  × 0.20")
    print(f"    evidence_strength    = {answer.evidence_strength:.2f}  × 0.20")
    print(f"    semantic_validity    = {answer.semantic_validity:.2f}  × 0.15")
    print(f"    inference_validity   = {answer.inference_validity:.2f}  × 0.10")
    print(f"    certainty_clarity    = {answer.certainty_clarity:.2f}  × 0.10")
    print(f"    hallucination_risk   = {answer.hallucination_risk:.2f}  × −0.30")
    print(f"  ─────────────────────────────────────")
    print(f"  AnswerScore          = {answer.final_score:.3f}")
    print(f"  VERDICT              : {verdict_label(answer.verdict.value)}")
    for b in answer.blockers:
        print(f"    BLOCKER: {b}")

print(f"\n{SEP2}")
print("\n  PIPELINE REGISTRY — wired run on: 'العلم نور'")
print(SEP)

reg = PipelineRegistry()
ctx = {"text": "العلم نور", "decoder_result": decoder.decode("العلم نور")}

layer_fns = {
    "reality_grounding_layer":            lambda c: {"reality": c["decoder_result"]["mcd_analysis"]["nodes"]},
    "prior_opinion_filter_layer":         lambda c: {"filtered": not c["decoder_result"]["fake_evidence_report"]["has_fake_evidence"]},
    "differentiation_layer":              lambda c: {"entities": [n["surface"] for n in c["decoder_result"]["mcd_analysis"]["nodes"]]},
    "essence_assignment_layer":           lambda c: {"essences": [d["concept"] for d in c["decoder_result"]["dal_madlul"]]},
    "domain_assignment_layer":            lambda c: {"domain": c["decoder_result"]["domain"]["judgment_type"]},
    "relational_mapping_layer":           lambda c: {"relations": c["decoder_result"]["mcd_analysis"].get("relations", [])},
    "arabic_operator_layer":              lambda c: {"operators_parsed": True},
    "binding_layer":                      lambda c: {"bound": [d["dal"] for d in c["decoder_result"]["dal_madlul"]]},
    "concept_formation_layer":            lambda c: {"concepts": [d["concept"] for d in c["decoder_result"]["dal_madlul"] if d["concept"]]},
    "judgment_formation_layer":           lambda c: {"judgment": c["decoder_result"]["rational_judgment"]["status"]},
    "signifier_analysis_layer":           lambda c: {"dals": [d["dal"] for d in c["decoder_result"]["dal_madlul"]]},
    "signified_analysis_layer":           lambda c: {"madluls": [d["madlul"] for d in c["decoder_result"]["dal_madlul"]]},
    "signifier_signified_relation_layer": lambda c: {"types": [d["dalalah_type"] for d in c["decoder_result"]["dal_madlul"]]},
    "mantuq_layer":                       lambda c: {"mantuq": c["decoder_result"]["mcd_analysis"].get("answer", "")},
    "mafhoom_layer":                      lambda c: {"mafhoom": None},
    "general_specific_layer":             lambda c: {"scope": "general"},
    "absolute_restricted_layer":          lambda c: {"qualified": False},
    "causal_juridical_relations_layer":   lambda c: {"illah": None},
    "tahqeeq_manat_layer":                lambda c: {"manat_status": "applicable", "score": 1.0},
    "application_layer":                  lambda c: {"applied": True, "epistemic_status": c["decoder_result"]["epistemic_status"]},
    "epistemic_audit_layer":              lambda c: {"certainty": c["decoder_result"]["certainty"]},
}

for key, fn in layer_fns.items():
    reg.register(key, fn)

results = reg.executor(ctx).run(stop_on_failure=False)
passed  = sum(1 for r in results if r.success)
print(f"  Layers completed : {passed}/21  failures: {sum(1 for r in results if not r.success)}\n")

for r in results:
    ld  = reg.layer(r.layer_key)
    out = ""
    if r.success and r.output:
        first = str(next(iter(r.output.values())))
        out = "  → " + (first[:50] + "…" if len(first) > 50 else first)
    icon = "✅" if r.success else "❌"
    print(f"  {icon} Layer {ld.number:2d}  {ld.key:<42}{out}")

print(f"\n{SEP2}")
print("  Live test complete.")
print(SEP2)
