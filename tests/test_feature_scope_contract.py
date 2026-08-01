import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FeatureScopeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontend = (ROOT / "simple.html").read_text(encoding="utf-8")

    def test_manual_save_is_removed_but_automatic_storage_and_backups_remain(self):
        for removed in (
            'id="saveMode"',
            "manualSave",
            "saveFileHandle",
            "showSaveFilePicker",
            "loadFromFile",
        ):
            self.assertNotIn(removed, self.frontend)

        self.assertIn("electronStorage._saveToDisk", self.frontend)
        self.assertIn('onclick="exportBackup()"', self.frontend)
        self.assertIn('onclick="importBackup()"', self.frontend)

    def test_unlearned_library_is_removed_but_unrated_mode_remains(self):
        for removed in (
            "未完全学会词库",
            "unlearnedWords",
            "vocab_unlearned",
            "unlearnedModal",
            "addToUnlearned",
        ):
            self.assertNotIn(removed, self.frontend)

        self.assertIn("function unlearnedMode()", self.frontend)
        self.assertIn("setMode('unlearned',this)", self.frontend)

    def test_full_reset_is_explicitly_scoped_to_current_book(self):
        self.assertIn("重置当前词书全部进度", self.frontend)
        self.assertIn("requestConfirm('重置当前词书'", self.frontend)


if __name__ == "__main__":
    unittest.main()
