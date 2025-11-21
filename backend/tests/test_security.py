"""
Tests for security utilities, specifically API key sanitization.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.security import sanitize_api_key, sanitize_error_message


def test_sanitize_api_key_with_openai_key():
    """Test that OpenAI API keys are properly sanitized"""
    text = "Error: Invalid API key sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567"
    result = sanitize_api_key(text)
    assert "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567" not in result
    assert "sk-****REDACTED****" in result
    print("✓ OpenAI key sanitization works")


def test_sanitize_api_key_with_generic_key():
    """Test that generic long alphanumeric strings are sanitized"""
    text = "Error with key: abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890"
    result = sanitize_api_key(text)
    assert "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890" not in result
    assert "****REDACTED****" in result
    print("✓ Generic key sanitization works")


def test_sanitize_api_key_with_specific_value():
    """Test that specific API key values are properly masked"""
    key = "my-secret-api-key-12345678"
    text = f"Authentication failed with key: {key}"
    result = sanitize_api_key(text, key)
    assert key not in result
    assert "my-s...5678" in result
    print("✓ Specific key value sanitization works")


def test_sanitize_error_message():
    """Test that error messages are properly sanitized"""
    error = Exception("Invalid credentials: sk-proj-abc123def456ghi789jkl012mno345pqr678stu901")
    sensitive_values = ["sk-proj-abc123def456ghi789jkl012mno345pqr678stu901"]
    result = sanitize_error_message(error, sensitive_values)
    assert "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901" not in result
    print("✓ Error message sanitization works")


def test_sanitize_preserves_safe_text():
    """Test that normal text without keys is preserved"""
    text = "This is a normal error message without any keys"
    result = sanitize_api_key(text)
    assert result == text
    print("✓ Safe text is preserved")


def test_sanitize_preserves_uuids():
    """Test that UUIDs and other non-key identifiers are preserved"""
    # UUIDs typically don't have both letters and numbers in long sequences
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    text = f"Error processing request {uuid}"
    result = sanitize_api_key(text)
    # UUID should be preserved since it has dashes every 8-12 chars
    assert uuid in result
    print("✓ UUIDs are preserved")


if __name__ == "__main__":
    test_sanitize_api_key_with_openai_key()
    test_sanitize_api_key_with_generic_key()
    test_sanitize_api_key_with_specific_value()
    test_sanitize_error_message()
    test_sanitize_preserves_safe_text()
    test_sanitize_preserves_uuids()
    print("\n✅ All security tests passed!")
