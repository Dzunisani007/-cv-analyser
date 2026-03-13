from app.utils.pii import strip_pii_for_models


def test_strip_pii_redacts_email_and_phone():
    t = "Email: a.b@example.com Phone: +491234567890 Date: 2024-01-02"
    out = strip_pii_for_models(t)
    assert "example.com" not in out
    assert "+491234" not in out
    assert "2024-01-02" not in out
    assert "[REDACTED]" in out
