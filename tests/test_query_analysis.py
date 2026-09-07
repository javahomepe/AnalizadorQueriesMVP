from domain.query_analysis import analyze_risk_query


def test_happy_path_is_grounded_and_does_not_require_approval():
    result = analyze_risk_query(
        "SELECT id, customer_id, status FROM query_analyzer.orders WHERE id = 42",
        "ops.demo", "operador", "09:00", "consulta", "query_analyzer",
    )
    assert result["ok"] is True
    assert result["decision"] == "approved"
    assert result["requires_dba_approval"] is False
    assert result["evidence_complete"] is True
    assert result["query_analysis"]["masked_query"].endswith("WHERE id = %s")


def test_heavy_download_and_incidents_require_dba():
    result = analyze_risk_query(
        "SELECT status, COUNT(*) FROM query_analyzer.orders GROUP BY status ORDER BY status",
        "ana.analista", "analista", "11:00", "descarga", "query_analyzer",
    )
    assert result["ok"] is True
    assert result["decision"] == "requires_dba_approval"
    assert result["requires_dba_approval"] is True
    policy_ids = {item["policy_id"] for item in result["policy_alerts"]}
    assert {"POL-VOL-001", "POL-DWN-001", "POL-INC-001", "POL-SEC-001"}.issubset(policy_ids)


def test_missing_metadata_is_declared_without_invention():
    result = analyze_risk_query(
        "SELECT id FROM query_analyzer.unknown_table WHERE id = 1",
        "ops.demo", "operador", "09:00", "consulta", "query_analyzer",
    )
    assert result["ok"] is True
    assert result["evidence_complete"] is False
    assert result["decision"] == "incomplete"
    assert result["evidence"]["metadata"] == []
    assert result["missing_evidence"]


def test_write_operation_is_out_of_scope():
    result = analyze_risk_query(
        "DELETE FROM query_analyzer.orders WHERE id = 42",
        "ops.demo", "operador", "09:00", "consulta", "query_analyzer",
    )
    assert result["ok"] is False
    assert result["error"]["code"] == "WRITE_OPERATION_DENIED"


def test_invalid_tool_input_returns_clear_error():
    result = analyze_risk_query("", "ops.demo", "operador", "09:00")
    assert result["ok"] is False
    assert result["error"]["code"] == "EMPTY_QUERY"

