from mcd.math_governance import FractalPatternMemory, FractalPattern


def test_pattern_recall_by_residual():
    mem = FractalPatternMemory()
    mem.add_pattern(FractalPattern("p1", "ambiguity_ignored", residual_signature="ambiguity_ignored"))
    got = mem.recall_by_residual("ambiguity_ignored")
    assert len(got) == 1


def test_pattern_recall_by_operator_chain():
    mem = FractalPatternMemory()
    mem.add_pattern(FractalPattern("p1", "tool_as_proof", operator_chain=["gpt_operator", "emphasis_operator"]))
    got = mem.recall_by_operator_chain(["gpt_operator", "emphasis_operator"])
    assert len(got) == 1
