#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-lexia-preflight.py."""
from __future__ import annotations

import argparse
import io
import importlib.util
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-lexia-preflight.py")


def load_preflight_module():
    spec = importlib.util.spec_from_file_location("check_lexia_preflight", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def args(**overrides):
    defaults = dict(
        skip_self_test=False,
        list_steps=False,
        final=False,
        root_only=False,
        tooling_only=False,
        stability_seconds=None,
        stability_attempts=1,
        stability_retry_delay_seconds=1.0,
        stability_json=None,
        change_summary_json=None,
        compare_sync_manifest=None,
        manifest_diff_json=None,
        manifest_diff_fail_on_content_change=False,
        change_summary_limit=None,
        change_summary_untracked_files=None,
        change_fail_preset=[],
        change_fail_on_group=[],
        json=None,
        allow_untracked_sync_artifacts=False,
        skip_rx=False,
        no_rx_strict=False,
        generated_validators=False,
        generated_validator_root="outputs/ux",
        generated_validator_target=[],
        generated_validator_json=None,
        generated_validator_fail_on_warning=False,
        generated_validator_show_warnings=False,
        bundle_dir=None,
        bundle_fail_on_not_ready=False,
        rx_json=None,
        worklist_markdown=None,
        worklist_json=None,
        worklist_json_format=None,
        worklist_prompts_dir=None,
        worklist_fail_on=None,
        worklist_target=[],
        json_format=None,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class LexiaPreflightTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_preflight_module()

    def test_self_tests_are_first_steps(self) -> None:
        steps = self.mod.build_steps(args(), ["outputs", "references"])
        self.assertEqual(
            [
                "preflight wrapper self-test",
                "duplicate checker self-test",
                "ARIADNE validator self-test",
                "RX validator self-test",
                "TREE validator self-test",
                "generated validators self-test",
                "generated validators manifest self-test",
                "ARIADNE RX backfill self-test",
                "sync checker self-test",
                "manifest checker self-test",
                "manifest diff self-test",
                "content worklist self-test",
                "worklist manifest self-test",
                "RX coverage self-test",
                "RX coverage manifest self-test",
                "preflight bundle self-test",
                "file stability self-test",
                "change summary self-test",
                "footer stamp self-test",
                "created-date stamp self-test",
                "restamp migration self-test",
                "staged stamp self-test",
            ],
            [step.name for step in steps[:22]],
        )
        self.assertEqual("duplicate/id drift", steps[22].name)

    def test_allow_untracked_is_passed_to_sync_contract(self) -> None:
        steps = self.mod.build_steps(args(allow_untracked_sync_artifacts=True), ["outputs", "references"])
        sync_step = next(step for step in steps if step.name == "Lexia sync contract")
        self.assertIn("--allow-untracked-sync-artifacts", sync_step.command)

    def test_rx_coverage_runs_without_ansi_colors(self) -> None:
        steps = self.mod.build_steps(args(skip_self_test=True), ["outputs", "references"])
        rx_step = next(step for step in steps if step.name == "ARIADNE -> RX coverage")
        self.assertIn("--no-color", rx_step.command)

    def test_rx_coverage_json_is_passed(self) -> None:
        steps = self.mod.build_steps(args(skip_self_test=True, rx_json="deploy/rx.json"), ["outputs", "references"])
        rx_step = next(step for step in steps if step.name == "ARIADNE -> RX coverage")
        self.assertIn("--json", rx_step.command)
        self.assertIn("deploy/rx.json", rx_step.command)
        schema_step = next(step for step in steps if step.name == "RX coverage manifest schema")
        self.assertIn("deploy/rx.json", schema_step.command)
        self.assertIn("--verify-current", schema_step.command)

    def test_generated_validators_are_optional_and_targetable(self) -> None:
        steps = self.mod.build_steps(args(skip_self_test=True), ["outputs", "references"])
        self.assertFalse(any(step.name == "generated HTML validators" for step in steps))

        steps = self.mod.build_steps(
            args(
                skip_self_test=True,
                generated_validators=True,
                generated_validator_root="outputs/ux",
                generated_validator_target=["rx", "tree"],
                generated_validator_json="deploy/generated-validators.json",
                generated_validator_fail_on_warning=True,
                generated_validator_show_warnings=True,
            ),
            ["outputs", "references"],
        )
        generated_step = next(step for step in steps if step.name == "generated HTML validators")
        self.assertIn("outputs/ux", [part.replace("\\", "/") for part in generated_step.command])
        self.assertEqual(2, generated_step.command.count("--target"))
        self.assertIn("rx", generated_step.command)
        self.assertIn("tree", generated_step.command)
        self.assertIn("--json", generated_step.command)
        self.assertIn("deploy/generated-validators.json", generated_step.command)
        self.assertIn("--fail-on-warning", generated_step.command)
        self.assertIn("--show-warnings", generated_step.command)
        schema_step = next(step for step in steps if step.name == "generated validators manifest schema")
        self.assertIn("deploy/generated-validators.json", schema_step.command)
        self.assertIn("--verify-current", schema_step.command)

    def test_bundle_dir_sets_stable_outputs(self) -> None:
        ns = args(skip_self_test=True, bundle_dir="deploy/lexia-preflight")
        self.mod.apply_bundle_defaults(ns)
        self.assertEqual("deploy/lexia-preflight/lexia-sync-manifest.json", ns.json.replace("\\", "/"))
        self.assertEqual("manifest", ns.json_format)
        self.assertEqual("deploy/lexia-preflight/rx-coverage.json", ns.rx_json.replace("\\", "/"))
        self.assertEqual("deploy/lexia-preflight/lexia-content-worklist.md", ns.worklist_markdown.replace("\\", "/"))
        self.assertEqual("deploy/lexia-preflight/lexia-content-worklist.json", ns.worklist_json.replace("\\", "/"))
        self.assertEqual("manifest", ns.worklist_json_format)
        self.assertEqual("deploy/lexia-preflight/lexia-content-prompts", ns.worklist_prompts_dir.replace("\\", "/"))
        self.assertEqual("deploy/lexia-preflight/lexia-change-summary.json", ns.change_summary_json.replace("\\", "/"))
        self.assertIsNone(ns.stability_json)
        self.assertIsNone(ns.manifest_diff_json)

        steps = self.mod.build_steps(ns, ["outputs", "references"])
        change_step = next(step for step in steps if step.name == "change summary")
        self.assertIn("deploy/lexia-preflight/lexia-change-summary.json", [part.replace("\\", "/") for part in change_step.command])
        self.assertTrue(any(step.name == "Lexia manifest schema" for step in steps))
        self.assertTrue(any(step.name == "RX coverage manifest schema" for step in steps))
        self.assertTrue(any(step.name == "Lexia worklist schema" for step in steps))
        bundle_step = steps[-1]
        self.assertEqual("Lexia preflight bundle schema", bundle_step.name)
        self.assertIn("deploy/lexia-preflight", bundle_step.command)
        self.assertIn("--verify-current", bundle_step.command)
        self.assertIn("--write-index", bundle_step.command)
        self.assertIn("--verify-index", bundle_step.command)
        self.assertNotIn("--fail-on-not-ready", bundle_step.command)
        sync_index = next(index for index, step in enumerate(steps) if step.name == "Lexia sync contract")
        bundle_index = next(index for index, step in enumerate(steps) if step.name == "Lexia preflight bundle schema")
        self.assertLess(sync_index, bundle_index)
        self.assertEqual("Lexia manifest schema", steps[sync_index + 1].name)

    def test_standard_bundle_path_matching_accepts_absolute_paths(self) -> None:
        relative = self.mod.bundle_path("deploy/lexia-preflight", "lexia-sync-manifest.json")
        absolute = str((self.mod.ROOT / relative).resolve())
        self.assertTrue(self.mod.same_path(absolute, relative))

        ns = args(skip_self_test=True, bundle_dir="deploy/lexia-preflight")
        self.mod.apply_bundle_defaults(ns)
        ns.json = absolute
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        self.assertTrue(any(step.name == "Lexia preflight bundle schema" for step in steps))

    def test_bundle_dir_sets_manifest_diff_output_when_baseline_is_given(self) -> None:
        ns = args(
            skip_self_test=True,
            bundle_dir="deploy/lexia-preflight",
            compare_sync_manifest="deploy/baseline/lexia-sync-manifest.json",
        )
        self.mod.apply_bundle_defaults(ns)
        self.assertEqual("deploy/lexia-preflight/lexia-manifest-diff.json", ns.manifest_diff_json.replace("\\", "/"))
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        names = [step.name for step in steps]
        self.assertLess(names.index("Lexia manifest schema"), names.index("Lexia manifest diff"))
        self.assertLess(names.index("Lexia manifest diff"), names.index("Lexia preflight bundle schema"))
        diff_step = next(step for step in steps if step.name == "Lexia manifest diff")
        normalized = [part.replace("\\", "/") for part in diff_step.command]
        self.assertIn("deploy/baseline/lexia-sync-manifest.json", normalized)
        self.assertIn("deploy/lexia-preflight/lexia-sync-manifest.json", normalized)
        self.assertIn("deploy/lexia-preflight/lexia-manifest-diff.json", normalized)

    def test_bundle_dir_sets_generated_validator_json_when_enabled(self) -> None:
        ns = args(skip_self_test=True, bundle_dir="deploy/lexia-preflight", generated_validators=True)
        self.mod.apply_bundle_defaults(ns)
        self.assertEqual("deploy/lexia-preflight/generated-validators.json", ns.generated_validator_json.replace("\\", "/"))
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        generated_step = next(step for step in steps if step.name == "generated HTML validators")
        normalized = [part.replace("\\", "/") for part in generated_step.command]
        self.assertIn("deploy/lexia-preflight/generated-validators.json", normalized)
        schema_step = next(step for step in steps if step.name == "generated validators manifest schema")
        self.assertIn("deploy/lexia-preflight/generated-validators.json", [part.replace("\\", "/") for part in schema_step.command])

    def test_manifest_diff_fail_on_content_change_is_passed(self) -> None:
        steps = self.mod.build_steps(
            args(
                skip_self_test=True,
                json="deploy/current.json",
                json_format="manifest",
                compare_sync_manifest="deploy/baseline.json",
                manifest_diff_json="deploy/diff.json",
                manifest_diff_fail_on_content_change=True,
            ),
            ["outputs", "references"],
        )
        diff_step = next(step for step in steps if step.name == "Lexia manifest diff")
        self.assertIn("--fail-on-content-change", diff_step.command)

    def test_bundle_dir_preserves_explicit_outputs(self) -> None:
        ns = args(
            bundle_dir="deploy/lexia-preflight",
            json="custom/sync.json",
            json_format="entries",
            rx_json="custom/rx.json",
            change_summary_json="custom/changes.json",
            worklist_json="custom/worklist.json",
            worklist_json_format="items",
        )
        self.mod.apply_bundle_defaults(ns)
        self.assertEqual("custom/sync.json", ns.json)
        self.assertEqual("entries", ns.json_format)
        self.assertEqual("custom/rx.json", ns.rx_json)
        self.assertEqual("custom/changes.json", ns.change_summary_json)
        self.assertEqual("custom/worklist.json", ns.worklist_json)
        self.assertEqual("items", ns.worklist_json_format)
        self.assertEqual("deploy/lexia-preflight/lexia-content-worklist.md", ns.worklist_markdown.replace("\\", "/"))
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        self.assertFalse(any(step.name == "Lexia preflight bundle schema" for step in steps))

    def test_final_sets_worklist_gate(self) -> None:
        ns = args(skip_self_test=True, final=True)
        self.mod.apply_final_defaults(ns)
        self.assertEqual("any", ns.worklist_fail_on)
        self.assertEqual(["sync-ready"], ns.change_fail_preset)
        self.assertEqual(2.0, ns.stability_seconds)
        self.assertEqual(3, ns.stability_attempts)
        self.assertEqual(2.0, ns.stability_retry_delay_seconds)
        self.assertTrue(ns.bundle_fail_on_not_ready)
        self.assertTrue(ns.generated_validators)
        self.assertTrue(ns.generated_validator_show_warnings)
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        change_step = next(step for step in steps if step.name == "change summary")
        self.assertIn("--fail-preset", change_step.command)
        self.assertIn("sync-ready", change_step.command)
        generated_step = next(step for step in steps if step.name == "generated HTML validators")
        self.assertIn("--show-warnings", generated_step.command)
        stability_step = next(step for step in steps if step.name == "Lexia file stability")
        self.assertIn("--attempts", stability_step.command)
        self.assertIn("3", stability_step.command)
        self.assertIn("--retry-delay-seconds", stability_step.command)
        worklist_step = next(step for step in steps if step.name == "content worklist")
        self.assertIn("--fail-on", worklist_step.command)
        self.assertIn("any", worklist_step.command)

    def test_final_keeps_existing_change_fail_preset_without_duplicate(self) -> None:
        ns = args(skip_self_test=True, final=True, change_fail_preset=["sync-ready"])
        self.mod.apply_final_defaults(ns)
        self.assertEqual(["sync-ready"], ns.change_fail_preset)

    def test_tooling_only_profile_sets_gate_and_keeps_running(self) -> None:
        ns = args(skip_self_test=True, tooling_only=True)
        self.mod.apply_tooling_only_defaults(ns)
        self.assertTrue(ns.keep_going)
        self.assertTrue(ns.allow_untracked_sync_artifacts)
        self.assertTrue(ns.generated_validators)
        self.assertTrue(ns.generated_validator_show_warnings)
        self.assertEqual(8, ns.change_summary_limit)
        self.assertEqual(["tooling-only"], ns.change_fail_preset)
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        self.assertEqual("change summary", steps[0].name)
        self.assertIn("tooling-only", steps[0].command)
        self.assertIn("--limit", steps[0].command)
        self.assertIn("8", steps[0].command)
        self.assertTrue(any(step.name == "generated HTML validators" for step in steps))
        generated_step = next(step for step in steps if step.name == "generated HTML validators")
        self.assertIn("--show-warnings", generated_step.command)
        sync_step = next(step for step in steps if step.name == "Lexia sync contract")
        self.assertIn("--allow-untracked-sync-artifacts", sync_step.command)

    def test_root_only_profile_sets_root_gate_and_keeps_running(self) -> None:
        ns = args(skip_self_test=True, root_only=True)
        self.mod.apply_root_only_defaults(ns)
        self.assertTrue(ns.keep_going)
        self.assertTrue(ns.allow_untracked_sync_artifacts)
        self.assertFalse(ns.generated_validators)
        self.assertFalse(ns.generated_validator_show_warnings)
        self.assertEqual(8, ns.change_summary_limit)
        self.assertEqual(["root-tooling-only"], ns.change_fail_preset)
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        self.assertEqual("change summary", steps[0].name)
        self.assertIn("root-tooling-only", steps[0].command)
        self.assertIn("--limit", steps[0].command)
        self.assertIn("8", steps[0].command)
        self.assertFalse(any(step.name == "generated HTML validators" for step in steps))
        sync_step = next(step for step in steps if step.name == "Lexia sync contract")
        self.assertIn("--allow-untracked-sync-artifacts", sync_step.command)

    def test_root_only_profile_keeps_existing_preset_without_duplicate(self) -> None:
        ns = args(skip_self_test=True, root_only=True, change_fail_preset=["root-tooling-only"])
        self.mod.apply_root_only_defaults(ns)
        self.assertEqual(["root-tooling-only"], ns.change_fail_preset)

    def test_tooling_only_profile_keeps_existing_preset_without_duplicate(self) -> None:
        ns = args(skip_self_test=True, tooling_only=True, change_fail_preset=["tooling-only"])
        self.mod.apply_tooling_only_defaults(ns)
        self.assertEqual(["tooling-only"], ns.change_fail_preset)

    def test_tooling_only_profile_preserves_explicit_change_summary_limit(self) -> None:
        ns = args(skip_self_test=True, tooling_only=True, change_summary_limit=3)
        self.mod.apply_tooling_only_defaults(ns)
        self.assertEqual(3, ns.change_summary_limit)
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        self.assertIn("--limit", steps[0].command)
        self.assertIn("3", steps[0].command)

    def test_stability_step_is_added_when_requested(self) -> None:
        steps = self.mod.build_steps(
            args(skip_self_test=True, stability_seconds=0.1, stability_json="deploy/stability.json"),
            ["outputs", "references"],
        )
        stability_step = steps[0]
        self.assertEqual("Lexia file stability", stability_step.name)
        self.assertIn("--settle-seconds", stability_step.command)
        self.assertIn("0.1", stability_step.command)
        self.assertIn("--json", stability_step.command)
        self.assertIn("deploy/stability.json", stability_step.command)

    def test_change_fail_groups_are_passed(self) -> None:
        steps = self.mod.build_steps(
            args(
                skip_self_test=True,
                change_fail_preset=["root-tooling-only", "tooling-only", "sync-ready"],
                change_fail_on_group=["GENERATED_SYNC_HTML", "WORK"],
                change_summary_untracked_files="normal",
            ),
            ["outputs", "references"],
        )
        change_step = steps[0]
        self.assertEqual("change summary", change_step.name)
        self.assertNotIn("--json", change_step.command)
        self.assertIn("--fail-preset", change_step.command)
        self.assertIn("root-tooling-only", change_step.command)
        self.assertIn("tooling-only", change_step.command)
        self.assertIn("sync-ready", change_step.command)
        self.assertIn("--untracked-files", change_step.command)
        self.assertIn("normal", change_step.command)
        self.assertEqual(2, change_step.command.count("--fail-on-group"))
        self.assertIn("GENERATED_SYNC_HTML", change_step.command)
        self.assertIn("WORK", change_step.command)

    def test_render_step_plan_lists_names_and_commands(self) -> None:
        ns = args(skip_self_test=True, final=True, bundle_dir="deploy/lexia-preflight")
        self.mod.apply_final_defaults(ns)
        self.mod.apply_bundle_defaults(ns)
        self.assertEqual("deploy/lexia-preflight/lexia-file-stability.json", ns.stability_json.replace("\\", "/"))
        self.assertEqual("deploy/lexia-preflight/lexia-change-summary.json", ns.change_summary_json.replace("\\", "/"))
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        rendered = self.mod.render_step_plan(steps)
        self.assertIn("=== Lexia preflight steps ===", rendered)
        self.assertIn("lexia-file-stability.json", rendered)
        self.assertIn("lexia-change-summary.json", rendered)
        self.assertIn("content worklist", rendered)
        self.assertIn("--fail-on any", rendered)
        self.assertIn("--fail-on-not-ready", rendered)
        self.assertIn("Lexia preflight bundle schema", rendered)

    def test_bundle_fail_on_not_ready_is_passed(self) -> None:
        ns = args(skip_self_test=True, bundle_dir="deploy/lexia-preflight", bundle_fail_on_not_ready=True)
        self.mod.apply_bundle_defaults(ns)
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        bundle_step = next(step for step in steps if step.name == "Lexia preflight bundle schema")
        self.assertIn("--fail-on-not-ready", bundle_step.command)

    def test_final_preserves_explicit_worklist_gate(self) -> None:
        ns = args(final=True, worklist_fail_on="error")
        self.mod.apply_final_defaults(ns)
        self.assertEqual("error", ns.worklist_fail_on)

    def test_final_rejects_allow_untracked_before_running_steps(self) -> None:
        original_argv = sys.argv
        out = io.StringIO()
        try:
            sys.argv = [str(SCRIPT), "--final", "--allow-untracked-sync-artifacts"]
            with redirect_stdout(out):
                rc = self.mod.main()
        finally:
            sys.argv = original_argv
        self.assertEqual(2, rc)
        self.assertIn("--final と --allow-untracked-sync-artifacts は同時に指定できません", out.getvalue())
        self.assertNotIn("Lexia preflight", out.getvalue())

    def test_final_rejects_tooling_only_before_running_steps(self) -> None:
        original_argv = sys.argv
        out = io.StringIO()
        try:
            sys.argv = [str(SCRIPT), "--final", "--tooling-only"]
            with redirect_stdout(out):
                rc = self.mod.main()
        finally:
            sys.argv = original_argv
        self.assertEqual(2, rc)
        self.assertIn("--final と --tooling-only は同時に指定できません", out.getvalue())
        self.assertNotIn("Lexia preflight", out.getvalue())

    def test_root_only_rejects_other_profiles_before_running_steps(self) -> None:
        original_argv = sys.argv
        out = io.StringIO()
        try:
            sys.argv = [str(SCRIPT), "--root-only", "--tooling-only"]
            with redirect_stdout(out):
                rc = self.mod.main()
        finally:
            sys.argv = original_argv
        self.assertEqual(2, rc)
        self.assertIn("--root-only と --tooling-only は同時に指定できません", out.getvalue())
        self.assertNotIn("Lexia preflight", out.getvalue())

        out = io.StringIO()
        try:
            sys.argv = [str(SCRIPT), "--root-only", "--final"]
            with redirect_stdout(out):
                rc = self.mod.main()
        finally:
            sys.argv = original_argv
        self.assertEqual(2, rc)
        self.assertIn("--final と --root-only は同時に指定できません", out.getvalue())
        self.assertNotIn("Lexia preflight", out.getvalue())

    def test_invalid_change_summary_limit_is_rejected(self) -> None:
        original_argv = sys.argv
        out = io.StringIO()
        try:
            sys.argv = [str(SCRIPT), "--change-summary-limit", "0", "--change-fail-preset", "tooling-only"]
            with redirect_stdout(out):
                rc = self.mod.main()
        finally:
            sys.argv = original_argv
        self.assertEqual(2, rc)
        self.assertIn("--change-summary-limit は 1 以上", out.getvalue())
        self.assertNotIn("Lexia preflight", out.getvalue())

    def test_keep_going_summary_lists_failed_steps(self) -> None:
        original_argv = sys.argv
        original_build_steps = self.mod.build_steps
        original_run_step = self.mod.run_step
        out = io.StringIO()
        try:
            sys.argv = [str(SCRIPT), "--skip-self-test", "--keep-going"]
            self.mod.build_steps = lambda _args, _roots: [
                self.mod.Step("first gate", []),
                self.mod.Step("passing check", []),
                self.mod.Step("second gate", []),
            ]
            self.mod.run_step = lambda step: {"first gate": 7, "passing check": 0, "second gate": 3}[step.name]
            with redirect_stdout(out):
                rc = self.mod.main()
        finally:
            self.mod.build_steps = original_build_steps
            self.mod.run_step = original_run_step
            sys.argv = original_argv
        self.assertEqual(1, rc)
        self.assertIn("FAIL=2", out.getvalue())
        self.assertIn("failed steps: first gate, second gate", out.getvalue())
        self.assertIn("failed step exits: first gate=7, second gate=3", out.getvalue())

    def test_bundle_dir_writes_sync_manifest_late(self) -> None:
        ns = args(skip_self_test=True, bundle_dir="deploy/lexia-preflight")
        self.mod.apply_bundle_defaults(ns)
        steps = self.mod.build_steps(ns, ["outputs", "references"])
        names = [step.name for step in steps]
        self.assertLess(names.index("Lexia worklist schema"), names.index("Lexia sync contract"))
        self.assertLess(names.index("Lexia sync contract"), names.index("Lexia preflight bundle schema"))

    def test_json_format_is_passed_to_sync_contract(self) -> None:
        steps = self.mod.build_steps(args(json="deploy/audit.json", json_format="manifest"), ["outputs", "references"])
        sync_step = next(step for step in steps if step.name == "Lexia sync contract")
        self.assertIn("--json", sync_step.command)
        self.assertIn("deploy/audit.json", sync_step.command)
        self.assertIn("--json-format", sync_step.command)
        self.assertIn("manifest", sync_step.command)
        manifest_step = next(step for step in steps if step.name == "Lexia manifest schema")
        self.assertIn("deploy/audit.json", manifest_step.command)
        self.assertIn("--verify-current", manifest_step.command)

    def test_worklist_step_passes_output_and_targets(self) -> None:
        steps = self.mod.build_steps(
            args(
                skip_self_test=True,
                skip_rx=True,
                worklist_markdown="deploy/wl.md",
                worklist_json="deploy/wl.json",
                worklist_json_format="manifest",
                worklist_prompts_dir="deploy/prompts",
                worklist_fail_on="any",
                worklist_target=["刑JX020", "刑TX045"],
            ),
            ["outputs", "references"],
        )
        worklist_step = next(step for step in steps if step.name == "content worklist")
        self.assertEqual("content worklist", worklist_step.name)
        command = worklist_step.command
        self.assertIn("--markdown", command)
        self.assertIn("deploy/wl.md", command)
        self.assertIn("--json", command)
        self.assertIn("deploy/wl.json", command)
        self.assertIn("--json-format", command)
        self.assertIn("manifest", command)
        self.assertIn("--prompts-dir", command)
        self.assertIn("deploy/prompts", command)
        self.assertIn("--fail-on", command)
        self.assertIn("any", command)
        self.assertEqual(2, command.count("--target"))
        self.assertLess(command.index("刑JX020"), command.index("刑TX045"))
        schema_step = steps[-1]
        self.assertEqual("Lexia worklist schema", schema_step.name)
        self.assertIn("deploy/wl.json", schema_step.command)
        self.assertIn("--verify-current", schema_step.command)


if __name__ == "__main__":
    unittest.main(verbosity=2)
