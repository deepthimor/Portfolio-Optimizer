def test_rag_ask_endpoint_returns_answer_citations_confidence_and_unsupported_flag(client):
    response = client.post(
        "/api/rag/ask",
        json={"question": "What is diversification?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "cited_sections" in data
    assert "confidence" in data
    assert "unsupported" in data
    assert data["unsupported"] is False
    assert data["cited_sections"]


def test_rag_ask_endpoint_handles_unsupported_question(client):
    response = client.post(
        "/api/rag/ask",
        json={"question": "Which ticker should I buy tomorrow?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["unsupported"] is True
    assert data["confidence"] == 0.0