import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = REPO_ROOT / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"


class TrainScriptTests(unittest.TestCase):
    def tearDown(self) -> None:
        if MODEL_DIR.exists():
            shutil.rmtree(MODEL_DIR)

    def test_train_script_creates_model_artifact(self) -> None:
        result = subprocess.run(
            [sys.executable, "src/train.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(MODEL_PATH.exists())
        self.assertIn("Model saved to models/model.pkl", result.stdout)


if __name__ == "__main__":
    unittest.main()
