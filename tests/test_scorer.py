from app.services.scorer import score_components


def test_score_components_shape_and_ranges():
    entities = {"skills": ["python", "docker"]}
    skill_matches = [{"skill": "python", "score": 0.9}, {"skill": "docker", "score": 0.8}]
    out = score_components(entities, skill_matches, "Python developer\n- did things\n2019-2021")

    assert "overall_score" in out
    assert "component_scores" in out
    cs = out["component_scores"]
    for k in ["skills", "experience", "education", "format"]:
        assert k in cs
        assert 0.0 <= float(cs[k]) <= 1.0

    assert 0.0 <= float(out["overall_score"]) <= 100.0
