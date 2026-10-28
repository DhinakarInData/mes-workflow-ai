import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import main
from api import workflow_api


client = TestClient(main.app)

SAMPLE_IR = {
    "workflow_name": "Material Check",
    "nodes": [
        {"id": "START", "type": "START", "label": "Start"},
        {
            "id": "A1",
            "type": "MANUAL_ACTIVITY",
            "label": "Scan material"
        },
        {"id": "END", "type": "END", "label": "End"}
    ],
    "edges": [
        {
            "source": "START",
            "target": "A1",
            "edge_type": "SEQUENCE"
        },
        {
            "source": "A1",
            "target": "END",
            "edge_type": "SEQUENCE"
        }
    ]
}


def test_generate_workflow_returns_renderable_graph(monkeypatch):
    submitted_text = "Scan the material, then end the workflow."
    extracted_texts = []

    def fake_extract_workflow(workflow_text):
        extracted_texts.append(workflow_text)
        return json.dumps(SAMPLE_IR)

    monkeypatch.setattr(
        workflow_api,
        "_extract_workflow",
        fake_extract_workflow
    )

    response = client.post(
        "/workflow/generate",
        json={"workflow_text": submitted_text}
    )

    assert response.status_code == 200
    graph = response.json()
    assert isinstance(graph["nodes"], list)
    assert isinstance(graph["edges"], list)
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2
    assert extracted_texts == [submitted_text]


def test_generate_workflow_rejects_blank_text(monkeypatch):
    def unexpected_extract_workflow(_workflow_text):
        raise AssertionError("Blank workflow text must not be extracted.")

    monkeypatch.setattr(
        workflow_api,
        "_extract_workflow",
        unexpected_extract_workflow
    )

    response = client.post(
        "/workflow/generate",
        json={"workflow_text": "  \n"}
    )

    assert response.status_code == 422
