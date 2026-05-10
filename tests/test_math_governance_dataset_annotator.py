from mcd.math_governance import DatasetMathAnnotator


def test_dataset_annotation_score():
    ann = DatasetMathAnnotator()
    report = ann.run("data/evaluation/ambiguity_ar.jsonl", write=False)
    assert report.total_examples > 0
    assert report.dataset_annotation_score <= 1.0
