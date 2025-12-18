import re

TEST_TYPE_MEANING = {
    "K": "Knowledge and Skills",
    "P": "Personality and Behavior",
    "A": "Ability and Aptitude",
    "B": "Biodata",
    "C": "Cognitive Ability",
    "D": "Developmental",
    "E": "Emotional Intelligence",
    "S": "Situational Judgement"
}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_assessment_text(a: dict) -> str:
    test_types_expanded = " ".join(
        TEST_TYPE_MEANING.get(t, t) for t in a.get("test_types", [])
    )

    duration_text = (
        f"{a['duration_minutes']} minutes"
        if a.get("duration_minutes") else
        "duration not specified"
    )

    text = (
        f"Assessment Name: {a.get('assessment_name','')} "
        f"Description: {a.get('description','')} "
        f"Test Types: {test_types_expanded} "
        f"Job Levels: {' '.join(a.get('job_levels', []))} "
        f"Languages: {' '.join(a.get('languages', []))} "
        f"Duration: {duration_text}"
    )

    return normalize_text(text)
