"""Tests for og_pilot.request_context module."""

import os
from unittest.mock import patch

import pytest

from og_pilot.request_context import (
    clear_current_request,
    get_current_path,
    get_current_request,
    set_current_request,
    with_request_context,
)


class TestSetCurrentRequest:
    """Tests for set_current_request."""

    def setup_method(self):
        """Clear request context before each test."""
        clear_current_request()

    def teardown_method(self):
        """Clear request context after each test."""
        clear_current_request()

    def test_sets_request(self):
        """Test that set_current_request stores the request."""
        set_current_request({"url": "/test/path"})
        assert get_current_request() == {"url": "/test/path"}

    def test_overwrites_previous_request(self):
        """Test that setting a new request overwrites the previous one."""
        set_current_request({"url": "/first"})
        set_current_request({"url": "/second"})
        assert get_current_request() == {"url": "/second"}


class TestClearCurrentRequest:
    """Tests for clear_current_request."""

    def setup_method(self):
        """Clear request context before each test."""
        clear_current_request()

    def test_clears_request(self):
        """Test that clear_current_request removes the request."""
        set_current_request({"url": "/test"})
        clear_current_request()
        assert get_current_request() is None


class TestGetCurrentPath:
    """Tests for get_current_path."""

    def setup_method(self):
        """Clear request context before each test."""
        clear_current_request()

    def teardown_method(self):
        """Clear request context after each test."""
        clear_current_request()

    def test_returns_explicit_path(self):
        """Test that explicit path is returned."""
        set_current_request({"url": "/ignored", "path": "/explicit/path"})
        assert get_current_path() == "/explicit/path"

    def test_extracts_path_from_url(self):
        """Test that path is extracted from URL."""
        set_current_request({"url": "/from/url?query=value"})
        assert get_current_path() == "/from/url?query=value"

    def test_extracts_path_from_full_url(self):
        """Test that path is extracted from full URL."""
        set_current_request({"url": "https://example.com/path/here?foo=bar"})
        assert get_current_path() == "/path/here?foo=bar"

    def test_extracts_path_from_full_url_without_query(self):
        """Test that path is extracted from full URL without query."""
        set_current_request({"url": "https://example.com/path/here"})
        assert get_current_path() == "/path/here"

    def test_returns_none_when_no_context(self):
        """Test that None is returned when no context is set."""
        clear_current_request()
        with patch.dict(os.environ, {}, clear=True):
            assert get_current_path() is None

    @patch.dict(os.environ, {"REQUEST_URI": "/from/env"})
    def test_fallback_to_request_uri(self):
        """Test fallback to REQUEST_URI env var."""
        clear_current_request()
        assert get_current_path() == "/from/env"

    @patch.dict(os.environ, {"ORIGINAL_FULLPATH": "/original/path"})
    def test_fallback_to_original_fullpath(self):
        """Test fallback to ORIGINAL_FULLPATH env var."""
        clear_current_request()
        assert get_current_path() == "/original/path"

    @patch.dict(os.environ, {"PATH_INFO": "/path/info", "QUERY_STRING": "foo=bar"})
    def test_fallback_to_path_info_with_query(self):
        """Test fallback to PATH_INFO with QUERY_STRING."""
        clear_current_request()
        assert get_current_path() == "/path/info?foo=bar"

    @patch.dict(os.environ, {"PATH_INFO": "/path/info"})
    def test_fallback_to_path_info_without_query(self):
        """Test fallback to PATH_INFO without QUERY_STRING."""
        clear_current_request()
        assert get_current_path() == "/path/info"

    @patch.dict(os.environ, {"REQUEST_PATH": "/request/path"})
    def test_fallback_to_request_path(self):
        """Test fallback to REQUEST_PATH env var."""
        clear_current_request()
        assert get_current_path() == "/request/path"


class TestWithRequestContext:
    """Tests for with_request_context."""

    def setup_method(self):
        """Clear request context before each test."""
        clear_current_request()

    def teardown_method(self):
        """Clear request context after each test."""
        clear_current_request()

    def test_runs_callback_with_context(self):
        """Test that callback runs with the request context."""
        captured_path = None

        def callback():
            nonlocal captured_path
            captured_path = get_current_path()

        with_request_context({"url": "/context/path"}, callback)
        assert captured_path == "/context/path"

    def test_returns_callback_result(self):
        """Test that with_request_context returns the callback result."""
        result = with_request_context({"url": "/test"}, lambda: "result")
        assert result == "result"

    def test_restores_previous_context(self):
        """Test that previous context is restored after callback."""
        set_current_request({"url": "/original"})

        with_request_context({"url": "/nested"}, lambda: None)

        assert get_current_path() == "/original"

    def test_clears_context_when_no_previous(self):
        """Test that context is cleared when there was no previous context."""
        clear_current_request()

        with_request_context({"url": "/temp"}, lambda: None)

        assert get_current_request() is None

    def test_restores_on_exception(self):
        """Test that context is restored even when callback raises."""
        set_current_request({"url": "/original"})

        with pytest.raises(RuntimeError):
            with_request_context(
                {"url": "/nested"},
                lambda: (_ for _ in ()).throw(RuntimeError("Test error")),
            )

        assert get_current_path() == "/original"
