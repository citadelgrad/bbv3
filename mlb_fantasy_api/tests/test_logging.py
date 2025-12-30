from app.core.logging import LogService, _redact_dict, redact_sensitive_data


class TestRedaction:
    """Tests for sensitive data redaction."""

    def test_redact_password(self):
        """Test that password fields are redacted."""
        event = {"password": "secret123", "username": "john"}
        result = redact_sensitive_data(None, None, event)
        assert result["password"] == "[REDACTED]"
        assert result["username"] == "john"

    def test_redact_token(self):
        """Test that token fields are redacted."""
        event = {"access_token": "abc123", "user_id": "123"}
        result = redact_sensitive_data(None, None, event)
        assert result["access_token"] == "[REDACTED]"
        assert result["user_id"] == "123"

    def test_redact_nested_dict(self):
        """Test that nested dictionaries are redacted."""
        event = {
            "user": {
                "password": "secret",
                "name": "John",
            }
        }
        result = redact_sensitive_data(None, None, event)
        assert result["user"]["password"] == "[REDACTED]"
        assert result["user"]["name"] == "John"

    def test_redact_dict_function(self):
        """Test the _redact_dict helper function."""
        data = {
            "api_key": "key123",
            "data": {
                "secret": "value",
                "public": "visible",
            },
        }
        result = _redact_dict(data)
        assert result["api_key"] == "[REDACTED]"
        assert result["data"]["secret"] == "[REDACTED]"
        assert result["data"]["public"] == "visible"


class TestLogService:
    """Tests for the LogService class."""

    def test_log_service_creation(self):
        """Test that LogService can be created."""
        service = LogService("test")
        assert service is not None

    def test_log_service_bind(self):
        """Test that bind returns a new LogService."""
        service = LogService("test")
        bound = service.bind(user_id="123")
        assert bound is not service

    def test_log_methods_exist(self):
        """Test that all log methods exist."""
        service = LogService("test")
        assert hasattr(service, "info")
        assert hasattr(service, "warning")
        assert hasattr(service, "error")
        assert hasattr(service, "debug")
        assert hasattr(service, "audit")
