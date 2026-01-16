import json
from pathlib import Path


def test_schema_is_valid_json():
    schema_path = Path(__file__).resolve().parents[1] / "src" / "schema.json"
    data = json.loads(schema_path.read_text())
    assert data.get("type") == "object"
    assert "properties" in data
    assert "required" in data


def test_sample_response_is_valid_json():
    sample_path = Path(__file__).resolve().parent / "sample_response.json"
    data = json.loads(sample_path.read_text())

    assert isinstance(data.get("answer"), str)
    assert isinstance(data.get("top_documents"), list)
    assert len(data["top_documents"]) >= 1

    for doc in data["top_documents"]:
        assert isinstance(doc.get("doc_id"), str)
        assert isinstance(doc.get("file_name"), str)
        assert isinstance(doc.get("snippet"), str)
