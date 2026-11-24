"""Read-only Codex discovery. It never launches coding actions without approval."""

import shutil
import subprocess


class CodexBridge:
    def __init__(self, executable=None):
        self.executable = executable or shutil.which("codex")

    def status(self):
        if not self.executable:
            return "Codex CLI is not installed."
        try:
            result = subprocess.run(
                [self.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            version = result.stdout.strip()
            capability = subprocess.run(
                [self.executable, "app-server", "--help"],
                capture_output=True,
                timeout=5,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            bridge = "app-server bridge is available" if capability.returncode == 0 else "app-server is unavailable"
            return f"Codex CLI is available: {version}; {bridge}. Coding actions require explicit approval."
        except OSError:
            return "Codex CLI was found but could not be queried."
