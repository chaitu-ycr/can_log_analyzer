import subprocess
import sys
import pytest
from python_project_template.app import App, AdvancedApp

def test_app_initialization():
    app = App("TestApp")
    assert app.get_name() == "TestApp"

def test_app_run_output(capsys):
    app = App("TestApp")
    app.run()
    captured = capsys.readouterr()
    assert "TestApp is running." in captured.out

def test_advanced_app_inheritance():
    adv_app = AdvancedApp("AdvApp")
    assert isinstance(adv_app, App)
    assert adv_app.get_name() == "AdvApp"

def test_advanced_app_run_output(capsys):
    adv_app = AdvancedApp("AdvApp")
    adv_app.run()
    captured = capsys.readouterr()
    assert "Advanced features enabled for AdvApp. App is running with enhancements." in captured.out

def test_app_get_name():
    app = App("AnotherApp")
    assert app.get_name() == "AnotherApp"

def test_advanced_app_get_name():
    adv_app = AdvancedApp("SuperApp")
    assert adv_app.get_name() == "SuperApp"

def test_app_main_block_output():
    result = subprocess.run(
        [sys.executable, "-m", "python_project_template.app"],
        capture_output=True,
        text=True
    )
    assert "BasicApp is running." in result.stdout
    assert "Advanced features enabled for ProApp. App is running with enhancements." in result.stdout