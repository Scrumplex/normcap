import subprocess
import sys

import pytest

from normcap import clipboard


def test_windll_copy():
    if not sys.platform.startswith("win"):
        pytest.xfail("Skipping Windows specific test")

    text = "test"
    clipboard.windows._windll_copy(text)

    with subprocess.Popen(
        ["powershell", "-command", "Get-Clipboard"], stdout=subprocess.PIPE
    ) as p:
        stdout = p.communicate()[0]
    clipped = stdout.decode("utf-8").strip()

    assert text == clipped


def test_unable_to_open_clipboard_raises(monkeypatch):
    if not sys.platform.startswith("win"):
        pytest.xfail("Skipping Windows specific test")

    # Block Clipboard from being opened
    from ctypes import windll
    from ctypes.wintypes import BOOL, HWND

    OpenClipboard = windll.user32.OpenClipboard  # noqa: N806
    OpenClipboard.argtypes = [HWND]
    OpenClipboard.restype = BOOL

    safeCloseClipboard = windll.user32.CloseClipboard  # noqa: N806
    safeCloseClipboard.argtypes = []
    safeCloseClipboard.restype = BOOL

    assert OpenClipboard(0)

    try:
        # Opening should fail now
        with pytest.raises(RuntimeError, match="Error calling OpenClipboard"):
            clipboard.windows._windll_copy("test")
    finally:
        assert safeCloseClipboard()


def test_not_on_windows_raises(monkeypatch):
    monkeypatch.setattr(clipboard.windows.sys, "platform", "linux")
    with pytest.raises(RuntimeError, match="only available on Windows"):
        clipboard.windows._windll_copy("test")