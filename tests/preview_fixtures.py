"""Generate NON-INSTALLABLE fixture manifests in a new directory for CI parsing."""
import argparse
from pathlib import Path
import subprocess

from support import FakeGitHub, project, release, sync

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", required=True)
args = parser.parse_args()
root = Path(args.output).resolve()
root.mkdir(parents=True, exist_ok=False)
project(root)
sync.synchronize(root, FakeGitHub([release(), release("beta", "3.4.0")]))
subprocess.run(["git", "init", "-b", "main", str(root)], check=True, capture_output=True)
subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True)
subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture", "-c",
                "user.email=fixture@example.invalid", "commit", "-m", "Fixture metadata"],
               check=True, capture_output=True)
print("Metadata fixtures only: these are not installable software packages.")
