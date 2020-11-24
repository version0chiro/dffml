import os
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "testing.yml"

PLUGIN_DIRS = list(
    map(
        lambda i: i.parent,
        filter(
            lambda i: ("examples" not in str(i) or "shouldi" in str(i))
            and "downloads" not in str(i)
            and ".eggs" not in str(i)
            and not "skel" in str(i),
            list(ROOT.rglob("setup.py")),
        ),
    )
)


class TestCI(unittest.TestCase):
    def test_secrets(self):
        """
        Check that the list of PyPi token secrets for releases matches the
        plugins we have.
        """
        lines = []
        for line in WORKFLOW.read_text().split("\n"):
            line = line.strip()
            if line.startswith("cat > ${PYPI_TOKENS}"):
                lines.append(line)
            elif lines:
                if line.startswith("EOF"):
                    break
                else:
                    lines.append(line)
        lines = lines[1:]
        workflow = dict(map(lambda i: i.split("="), lines))
        for plugin_path in PLUGIN_DIRS:
            relative_path = str(plugin_path.relative_to(ROOT)).replace(
                os.sep, "/"
            )
            if relative_path == ".":
                continue
            self.assertIn(relative_path, workflow)
