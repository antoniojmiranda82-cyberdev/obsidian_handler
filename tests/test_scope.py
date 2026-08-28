import os
import unittest
from unittest.mock import patch


class AssetDreamScopeTests(unittest.TestCase):
    def test_asset_dream_path_stays_under_project_root(self):
        with patch.dict(os.environ, {"ASSET_DREAM_ROOT": "Projects/asset-dream"}, clear=False):
            from python_src.scope import asset_dream_path
            self.assertEqual(asset_dream_path("01 - Inbox/note.md"), "Projects/asset-dream/01 - Inbox/note.md")

    def test_asset_dream_path_rejects_parent_escape(self):
        from python_src.scope import asset_dream_path
        with self.assertRaises(ValueError):
            asset_dream_path("../Q-Core/private.md")

    def test_proposal_path_never_overwrites_source(self):
        from python_src.scope import proposal_path
        source = "Projects/asset-dream/01 - Inbox/idea.md"
        proposal = proposal_path(source)
        self.assertNotEqual(proposal, source)
        self.assertEqual(proposal, "Projects/asset-dream/01 - Inbox/propuesta-idea.md")


if __name__ == "__main__":
    unittest.main()
