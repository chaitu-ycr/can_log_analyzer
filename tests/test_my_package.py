import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
from can_log_analyzer.web_app import WebApp
from src.can_log_analyzer.run_web_app import WebAppRunner

def test_upload_files_returns_none_when_no_files(monkeypatch):
    # Patch Streamlit file_uploader to return None
    monkeypatch.setattr("streamlit.sidebar.file_uploader", lambda *a, **kw: None)
    monkeypatch.setattr("streamlit.sidebar.header", lambda *a, **kw: None)
    can_log, db = WebApp.upload_files()
    assert can_log is None
    assert db is None

def test_load_can_database_with_invalid_file(monkeypatch):
    # Patch Streamlit error to capture error messages
    errors = []
    monkeypatch.setattr("streamlit.error", lambda msg: errors.append(msg))
    # Mock file with unsupported extension
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    mock_file.read.return_value = b""  # Add a read method
    result = WebApp.load_database(mock_file)
    assert result is None
    assert any("Unsupported database format" in str(e) for e in errors)

def test_load_can_log_with_invalid_extension(monkeypatch):
    # Patch Streamlit warning to capture warnings
    warnings = []
    monkeypatch.setattr("streamlit.warning", lambda msg: warnings.append(msg))
    # Provide dummy bytes and unsupported extension
    result = WebApp.load_log(b"dummy", ".txt")
    assert isinstance(result, dict)
    assert any("Unsupported log format" in str(w) for w in warnings)
    assert 1 in result  # Check dummy data structure

def test_load_can_log_with_empty_bytes(monkeypatch):
    warnings = []
    monkeypatch.setattr("streamlit.warning", lambda msg: warnings.append(msg))
    result = WebApp.load_log(b"", ".asc")
    assert isinstance(result, dict)
    assert any("Unsupported log format" in str(w) for w in warnings)
    assert 1 in result  # Check dummy data structure

def test_parse_args_defaults(monkeypatch):
    # Patch sys.argv to simulate no arguments
    monkeypatch.setattr("sys.argv", ["run_web_app.py"])
    args = WebAppRunner.parse_args()
    assert args.server_address is None
    assert args.server_port == 8501

def test_parse_args_custom(monkeypatch):
    monkeypatch.setattr("sys.argv", [
        "run_web_app.py", "--server-address", "127.0.0.1", "--server-port", "9000"
    ])
    args = WebAppRunner.parse_args()
    assert args.server_address == "127.0.0.1"
    assert args.server_port == 9000

def test_launch_success(monkeypatch):
    # Patch Path.is_file to return True and subprocess.Popen to simulate success
    with patch("src.can_log_analyzer.run_web_app.Path.is_file", return_value=True), \
         patch("src.can_log_analyzer.run_web_app.subprocess.Popen") as mock_popen:
        result = WebAppRunner.launch("localhost", 9999)
        assert result is True
        mock_popen.assert_called_once()

def test_launch_failure(monkeypatch):
    # Patch Path.is_file to return False to simulate missing file
    with patch("src.can_log_analyzer.run_web_app.Path.is_file", return_value=False):
        result = WebAppRunner.launch("localhost", 9999)
        assert result is False