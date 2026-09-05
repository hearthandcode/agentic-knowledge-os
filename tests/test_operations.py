from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agentic_knowledge_os import apply_plan, build_plan, rollback, uninstall, verify_install


class OperationTests(unittest.TestCase):
    def _plan(self, parent: Path, name: str = "extended-mind", host: str = "neutral") -> dict:
        return build_plan(name="Test Extended Mind", workspace=str(parent / name), host=host)

    def test_apply_requires_exact_plan_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent)
            receipt = apply_plan(plan, "sha256:not-the-plan")
            self.assertEqual(receipt["status"], "blocked")
            self.assertFalse((parent / "extended-mind").exists())

    def test_apply_verify_and_idempotent_reapply(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent, host="hermes")
            applied = apply_plan(plan, plan["plan_id"])
            self.assertEqual(applied["status"], "applied")
            workspace = parent / "extended-mind"
            self.assertTrue((workspace / "AGENTS.md").is_file())
            self.assertFalse((workspace / ".hermes.md").exists())
            self.assertEqual(verify_install(workspace)["status"], "clear")
            repeated = apply_plan(plan, plan["plan_id"])
            self.assertEqual(repeated["status"], "already-applied")

    def test_nonempty_foreign_target_is_preserved_and_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "existing"
            workspace.mkdir()
            foreign = workspace / "notes.md"
            foreign.write_text("mine\n", encoding="utf-8")
            plan = build_plan(name="Existing", workspace=str(workspace))
            receipt = apply_plan(plan, plan["plan_id"])
            self.assertEqual(receipt["status"], "blocked")
            self.assertEqual(foreign.read_text(encoding="utf-8"), "mine\n")
            self.assertFalse((workspace / ".akos").exists())

    def test_drift_blocks_uninstall_without_explicit_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent)
            applied = apply_plan(plan, plan["plan_id"])
            workspace = parent / "extended-mind"
            (workspace / "brain.json").write_text("changed\n", encoding="utf-8")
            verification = verify_install(workspace)
            self.assertEqual(verification["status"], "blocked")
            refused = uninstall(workspace, applied["manifest_digest"])
            self.assertEqual(refused["status"], "blocked")
            self.assertTrue((workspace / "brain.json").exists())

    def test_uninstall_removes_owned_files_and_preserves_user_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent)
            applied = apply_plan(plan, plan["plan_id"])
            workspace = parent / "extended-mind"
            user_record = workspace / "knowledge" / "my-note.md"
            user_record.write_text("user-owned\n", encoding="utf-8")
            removed = uninstall(workspace, applied["manifest_digest"])
            self.assertEqual(removed["status"], "removed")
            self.assertTrue(user_record.is_file())
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertFalse((workspace / ".akos" / "install-manifest.json").exists())
            self.assertIn("knowledge/my-note.md", removed["preserved_paths"])

    def test_force_removes_changed_owned_file_but_not_user_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent)
            applied = apply_plan(plan, plan["plan_id"])
            workspace = parent / "extended-mind"
            (workspace / "AGENTS.md").write_text("changed by user\n", encoding="utf-8")
            user_record = workspace / "sources" / "original.md"
            user_record.write_text("source\n", encoding="utf-8")
            removed = uninstall(workspace, applied["manifest_digest"], force_owned_changes=True)
            self.assertEqual(removed["status"], "removed")
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertTrue(user_record.exists())

    def test_rollback_uses_same_ownership_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent)
            applied = apply_plan(plan, plan["plan_id"])
            receipt = rollback(parent / "extended-mind", applied["manifest_digest"])
            self.assertEqual(receipt["operation"], "rollback")
            self.assertEqual(receipt["status"], "removed")

    def test_manifest_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent)
            apply_plan(plan, plan["plan_id"])
            manifest_path = parent / "extended-mind" / ".akos" / "install-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["workspace_root"] = str(parent / "elsewhere")
            manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
            receipt = verify_install(parent / "extended-mind")
            self.assertEqual(receipt["status"], "blocked")
            self.assertTrue(any("digest mismatch" in finding for finding in receipt["findings"]))

    def test_changed_line_endings_are_detected_as_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent)
            apply_plan(plan, plan["plan_id"])
            agents_path = parent / "extended-mind" / "AGENTS.md"
            agents_path.write_bytes(agents_path.read_bytes().replace(b"\n", b"\r\n"))
            receipt = verify_install(parent / "extended-mind")
            self.assertEqual(receipt["status"], "blocked")
            self.assertTrue(any("digest mismatch: AGENTS.md" in finding for finding in receipt["findings"]))

    def test_symbolic_linked_control_directory_is_not_traversed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            plan = self._plan(parent)
            applied = apply_plan(plan, plan["plan_id"])
            workspace = parent / "extended-mind"
            control = workspace / ".akos"
            moved = workspace / ".akos-preserved"
            control.rename(moved)
            control.symlink_to(moved, target_is_directory=True)
            verified = verify_install(workspace)
            self.assertEqual(verified["status"], "blocked")
            removed = uninstall(workspace, applied["manifest_digest"], force_owned_changes=True)
            self.assertEqual(removed["status"], "blocked")
            self.assertTrue((moved / "install-manifest.json").is_file())

    def test_apply_does_not_create_missing_parent_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "missing" / "extended-mind"
            plan = build_plan(name="Nested", workspace=str(target))
            receipt = apply_plan(plan, plan["plan_id"])
            self.assertEqual(receipt["status"], "blocked")
            self.assertFalse(target.parent.exists())


if __name__ == "__main__":
    unittest.main()
