from mcd.math_governance import JamiManiCalculator, JamiManiDefinition


def test_jami_mani_evidence():
    calc = JamiManiCalculator()
    d = JamiManiDefinition(
        concept_id="evidence",
        positive_cases=["verified_source", "traceable_observation"],
        negative_cases=["emphasis", "tool_output"],
    )
    r = calc.calculate(d, ["verified_source", "traceable_observation"], ["emphasis", "tool_output"])
    assert r.jami_score == 1.0
    assert r.mani_score == 1.0


def test_concept_tightness_harmonic_mean():
    calc = JamiManiCalculator()
    assert calc.harmonic_mean(0.8, 0.5) == 2 * 0.8 * 0.5 / (0.8 + 0.5)
