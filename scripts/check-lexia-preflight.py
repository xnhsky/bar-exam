#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lexia 同期前の read-only 一括ゲート。

outputs/ と references/ を、Lexia 同期で問題になりやすい順に横断検査する。

  0. test-*.py                    preflight/sync/worklist/stamp チェッカ自体の self-test
  1. check-lexia-stability.py     任意: 最終同期前に HTML 書き込み停止を確認
  2. check-duplicates.py          title/header/footer の ID 揺れ・重複
  3. check-lexia-sync-contract.py fileName/code/title/category/sourcePath/genmeta/data-rx
  4. check-lexia-manifest.py      任意: schemaVersion 付き JSON のスキーマ検査
  5. check-rx-coverage.py         ARIADNE data-rx から RX 実ファイルへの到達性
  6. check-generated-validators.py 任意: ARIADNE/RX/TREE 個別バリデータ横断
  7. lexia-content-worklist.py    任意: 内容改善セッション用 worklist / prompt 出力

生成や修正は行わない。失敗した工程があれば終了コード 1。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DEFAULT_ROOTS = ("outputs", "references")
CHANGE_GROUPS = (
    "ROOT_TOOLING",
    "GENERATION_TOOLING",
    "GENERATED_SYNC_HTML",
    "QUARANTINED_OUTPUT",
    "CANONICAL",
    "DOCS",
    "INPUTS",
    "WORK",
    "LOCAL_CONFIG",
    "OTHER",
)
CHANGE_FAIL_PRESETS = ("root-tooling-only", "tooling-only", "sync-ready")
DEFAULT_FINAL_STABILITY_ATTEMPTS = 3
DEFAULT_FINAL_STABILITY_RETRY_DELAY = 2.0
DEFAULT_TOOLING_CHANGE_SUMMARY_LIMIT = 8


@dataclass(frozen=True)
class Step:
    name: str
    command: list[str]


def bundle_path(bundle_dir: str, name: str) -> str:
    return str(Path(bundle_dir) / name)


def same_path(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    left_path = Path(left)
    right_path = Path(right)
    if not left_path.is_absolute():
        left_path = ROOT / left_path
    if not right_path.is_absolute():
        right_path = ROOT / right_path
    return left_path.resolve() == right_path.resolve()


def apply_bundle_defaults(args: argparse.Namespace) -> None:
    """--bundle-dir 指定時に同期前監査の安定出力一式を埋める。明示指定済みの値は尊重する。"""
    if not args.bundle_dir:
        return
    if args.stability_seconds and args.stability_seconds > 0 and not args.stability_json:
        args.stability_json = bundle_path(args.bundle_dir, "lexia-file-stability.json")
    if not args.change_summary_json:
        args.change_summary_json = bundle_path(args.bundle_dir, "lexia-change-summary.json")
    if not args.json:
        args.json = bundle_path(args.bundle_dir, "lexia-sync-manifest.json")
    if not args.json_format:
        args.json_format = "manifest"
    if not args.skip_rx and not args.rx_json:
        args.rx_json = bundle_path(args.bundle_dir, "rx-coverage.json")
    if not args.worklist_markdown:
        args.worklist_markdown = bundle_path(args.bundle_dir, "lexia-content-worklist.md")
    if not args.worklist_json:
        args.worklist_json = bundle_path(args.bundle_dir, "lexia-content-worklist.json")
    if not args.worklist_json_format:
        args.worklist_json_format = "manifest"
    if not args.worklist_prompts_dir:
        args.worklist_prompts_dir = bundle_path(args.bundle_dir, "lexia-content-prompts")
    if args.compare_sync_manifest and not args.manifest_diff_json:
        args.manifest_diff_json = bundle_path(args.bundle_dir, "lexia-manifest-diff.json")
    if args.generated_validators and not args.generated_validator_json:
        args.generated_validator_json = bundle_path(args.bundle_dir, "generated-validators.json")


def apply_final_defaults(args: argparse.Namespace) -> None:
    """--final は最終同期前の厳格プロファイル。残 worklist と同期前の残り物を gate 化する。"""
    if not args.final:
        return
    if not args.worklist_fail_on:
        args.worklist_fail_on = "any"
    if "sync-ready" not in args.change_fail_preset:
        args.change_fail_preset.append("sync-ready")
    args.generated_validators = True
    args.generated_validator_show_warnings = True
    if args.stability_seconds is None:
        args.stability_seconds = 2.0
    if args.stability_attempts == 1:
        args.stability_attempts = DEFAULT_FINAL_STABILITY_ATTEMPTS
    if args.stability_retry_delay_seconds == 1.0:
        args.stability_retry_delay_seconds = DEFAULT_FINAL_STABILITY_RETRY_DELAY
    args.bundle_fail_on_not_ready = True


def apply_tooling_only_defaults(args: argparse.Namespace) -> None:
    """--tooling-only は root/tooling 作業中に別セッションの生成差分を棚卸ししつつ全検査を回す。"""
    if not args.tooling_only:
        return
    if "tooling-only" not in args.change_fail_preset:
        args.change_fail_preset.append("tooling-only")
    args.allow_untracked_sync_artifacts = True
    args.generated_validators = True
    args.generated_validator_show_warnings = True
    args.keep_going = True
    if args.change_summary_limit is None:
        args.change_summary_limit = DEFAULT_TOOLING_CHANGE_SUMMARY_LIMIT


def apply_root_only_defaults(args: argparse.Namespace) -> None:
    """--root-only は ROOT_TOOLING だけを許すルート改善セッション用プロファイル。"""
    if not args.root_only:
        return
    if "root-tooling-only" not in args.change_fail_preset:
        args.change_fail_preset.append("root-tooling-only")
    args.allow_untracked_sync_artifacts = True
    args.keep_going = True
    if args.change_summary_limit is None:
        args.change_summary_limit = DEFAULT_TOOLING_CHANGE_SUMMARY_LIMIT


def should_check_bundle(args: argparse.Namespace) -> bool:
    if not args.bundle_dir or args.skip_rx:
        return False
    return (
        same_path(args.json, bundle_path(args.bundle_dir, "lexia-sync-manifest.json"))
        and args.json_format == "manifest"
        and same_path(args.rx_json, bundle_path(args.bundle_dir, "rx-coverage.json"))
        and same_path(args.worklist_markdown, bundle_path(args.bundle_dir, "lexia-content-worklist.md"))
        and same_path(args.worklist_json, bundle_path(args.bundle_dir, "lexia-content-worklist.json"))
        and args.worklist_json_format == "manifest"
        and same_path(args.worklist_prompts_dir, bundle_path(args.bundle_dir, "lexia-content-prompts"))
        and same_path(args.change_summary_json, bundle_path(args.bundle_dir, "lexia-change-summary.json"))
    )


def display_cmd(command: list[str]) -> str:
    rel_parts: list[str] = []
    for part in command:
        if part == sys.executable:
            rel_parts.append("python")
            continue
        try:
            p = Path(part)
            if p.is_absolute():
                rel_parts.append(p.relative_to(ROOT).as_posix())
                continue
        except Exception:
            pass
        rel_parts.append(part)
    return " ".join(rel_parts)


def resolve_roots(roots: list[str]) -> tuple[list[str], list[str]]:
    cmd_roots: list[str] = []
    missing: list[str] = []
    for root in roots:
        p = Path(root)
        abs_path = p if p.is_absolute() else ROOT / p
        if not abs_path.exists():
            missing.append(root)
        try:
            cmd_roots.append(abs_path.resolve().relative_to(ROOT).as_posix())
        except ValueError:
            cmd_roots.append(str(abs_path.resolve()))
    return cmd_roots, missing


def build_steps(args: argparse.Namespace, roots: list[str]) -> list[Step]:
    py_utf8 = [sys.executable, "-X", "utf8"]
    steps: list[Step] = []
    if not args.skip_self_test:
        steps.extend([
            Step(
                "preflight wrapper self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-preflight.py")],
            ),
            Step(
                "duplicate checker self-test",
                [sys.executable, str(SCRIPTS / "test-check-duplicates.py")],
            ),
            Step(
                "ARIADNE validator self-test",
                [sys.executable, str(SCRIPTS / "test-validate-ariadne.py")],
            ),
            Step(
                "RX validator self-test",
                [sys.executable, str(SCRIPTS / "test-validate-rx.py")],
            ),
            Step(
                "TREE validator self-test",
                [sys.executable, str(SCRIPTS / "test-validate-tree.py")],
            ),
            Step(
                "generated validators self-test",
                [sys.executable, str(SCRIPTS / "test-generated-validators.py")],
            ),
            Step(
                "generated validators manifest self-test",
                [sys.executable, str(SCRIPTS / "test-generated-validators-manifest.py")],
            ),
            Step(
                "ARIADNE RX backfill self-test",
                [sys.executable, str(SCRIPTS / "test-ariadne-backfill-rx-link.py")],
            ),
            Step(
                "sync checker self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-sync-contract.py")],
            ),
            Step(
                "manifest checker self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-manifest.py")],
            ),
            Step(
                "manifest diff self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-manifest-diff.py")],
            ),
            Step(
                "content worklist self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-content-worklist.py")],
            ),
            Step(
                "worklist manifest self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-worklist.py")],
            ),
            Step(
                "RX coverage self-test",
                [sys.executable, str(SCRIPTS / "test-rx-coverage.py")],
            ),
            Step(
                "RX coverage manifest self-test",
                [sys.executable, str(SCRIPTS / "test-rx-coverage-manifest.py")],
            ),
            Step(
                "preflight bundle self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-bundle.py")],
            ),
            Step(
                "file stability self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-stability.py")],
            ),
            Step(
                "change summary self-test",
                [sys.executable, str(SCRIPTS / "test-lexia-change-summary.py")],
            ),
            Step(
                "footer stamp self-test",
                [sys.executable, str(SCRIPTS / "test-stamp-footer.py")],
            ),
            Step(
                "created-date stamp self-test",
                [sys.executable, str(SCRIPTS / "test-stamp-created-date.py")],
            ),
            Step(
                "restamp migration self-test",
                [sys.executable, str(SCRIPTS / "test-restamp-english.py")],
            ),
            Step(
                "staged stamp self-test",
                [sys.executable, str(SCRIPTS / "test-stamp-staged.py")],
            ),
        ])
    if args.change_summary_json or args.change_fail_on_group or args.change_fail_preset:
        change_cmd = [sys.executable, str(SCRIPTS / "lexia-change-summary.py")]
        if args.change_summary_json:
            change_cmd.extend(["--json", args.change_summary_json])
        if args.change_summary_limit is not None:
            change_cmd.extend(["--limit", str(args.change_summary_limit)])
        if args.change_summary_untracked_files:
            change_cmd.extend(["--untracked-files", args.change_summary_untracked_files])
        for preset in args.change_fail_preset:
            change_cmd.extend(["--fail-preset", preset])
        for group in args.change_fail_on_group:
            change_cmd.extend(["--fail-on-group", group])
        steps.append(Step("change summary", change_cmd))
    if args.stability_seconds and args.stability_seconds > 0:
        stability_cmd = [
            *py_utf8,
            str(SCRIPTS / "check-lexia-stability.py"),
            *roots,
            "--settle-seconds",
            str(args.stability_seconds),
        ]
        if args.stability_attempts != 1:
            stability_cmd.extend(["--attempts", str(args.stability_attempts)])
        if args.stability_retry_delay_seconds != 1.0:
            stability_cmd.extend(["--retry-delay-seconds", str(args.stability_retry_delay_seconds)])
        if args.stability_json:
            stability_cmd.extend(["--json", args.stability_json])
        steps.append(Step("Lexia file stability", stability_cmd))
    check_bundle = should_check_bundle(args)
    steps.append(Step(
        "duplicate/id drift",
        [sys.executable, str(SCRIPTS / "check-duplicates.py"), *roots],
    ))
    sync_steps = [Step(
        "Lexia sync contract",
        [
            *py_utf8,
            str(SCRIPTS / "check-lexia-sync-contract.py"),
            "--summary",
            *roots,
        ],
    )]
    if args.json:
        sync_steps[0].command.extend(["--json", args.json])
        if args.json_format:
            sync_steps[0].command.extend(["--json-format", args.json_format])
    if args.allow_untracked_sync_artifacts:
        sync_steps[0].command.append("--allow-untracked-sync-artifacts")
    if args.json and args.json_format == "manifest":
        sync_steps.append(Step(
            "Lexia manifest schema",
            [sys.executable, str(SCRIPTS / "check-lexia-manifest.py"), args.json, "--verify-current"],
        ))
    if args.compare_sync_manifest:
        diff_cmd = [
            *py_utf8,
            str(SCRIPTS / "compare-lexia-manifests.py"),
            args.compare_sync_manifest,
            args.json,
        ]
        if args.manifest_diff_json:
            diff_cmd.extend(["--json", args.manifest_diff_json])
        if args.manifest_diff_fail_on_content_change:
            diff_cmd.append("--fail-on-content-change")
        sync_steps.append(Step("Lexia manifest diff", diff_cmd))
    if not check_bundle:
        steps.extend(sync_steps)
    if not args.skip_rx:
        rx_cmd = [
            *py_utf8,
            str(SCRIPTS / "check-rx-coverage.py"),
            "--summary",
            "--no-color",
        ]
        if not args.no_rx_strict:
            rx_cmd.append("--strict")
        if args.rx_json:
            rx_cmd.extend(["--json", args.rx_json])
        steps.append(Step("ARIADNE -> RX coverage", rx_cmd))
        if args.rx_json:
            steps.append(Step(
                "RX coverage manifest schema",
                [sys.executable, str(SCRIPTS / "check-rx-coverage-manifest.py"), args.rx_json, "--verify-current"],
            ))
    if args.generated_validators:
        generated_cmd = [
            *py_utf8,
            str(SCRIPTS / "check-generated-validators.py"),
            args.generated_validator_root,
        ]
        for target in args.generated_validator_target:
            generated_cmd.extend(["--target", target])
        if args.generated_validator_json:
            generated_cmd.extend(["--json", args.generated_validator_json])
        if args.generated_validator_fail_on_warning:
            generated_cmd.append("--fail-on-warning")
        if args.generated_validator_show_warnings:
            generated_cmd.append("--show-warnings")
        steps.append(Step("generated HTML validators", generated_cmd))
        if args.generated_validator_json:
            steps.append(Step(
                "generated validators manifest schema",
                [
                    sys.executable,
                    str(SCRIPTS / "check-generated-validators-manifest.py"),
                    args.generated_validator_json,
                    "--verify-current",
                ],
            ))
    if args.worklist_markdown or args.worklist_json or args.worklist_prompts_dir or args.worklist_fail_on:
        worklist_cmd = [
            sys.executable,
            str(SCRIPTS / "lexia-content-worklist.py"),
            *roots,
            "--quiet",
        ]
        if args.worklist_markdown:
            worklist_cmd.extend(["--markdown", args.worklist_markdown])
        if args.worklist_json:
            worklist_cmd.extend(["--json", args.worklist_json])
            if args.worklist_json_format:
                worklist_cmd.extend(["--json-format", args.worklist_json_format])
        if args.worklist_prompts_dir:
            worklist_cmd.extend(["--prompts-dir", args.worklist_prompts_dir])
        if args.worklist_fail_on:
            worklist_cmd.extend(["--fail-on", args.worklist_fail_on])
        for target in args.worklist_target:
            worklist_cmd.extend(["--target", target])
        steps.append(Step("content worklist", worklist_cmd))
        if args.worklist_json and args.worklist_json_format == "manifest":
            steps.append(Step(
                "Lexia worklist schema",
                [sys.executable, str(SCRIPTS / "check-lexia-worklist.py"), args.worklist_json, "--verify-current"],
            ))
    if check_bundle:
        steps.extend(sync_steps)
        steps.append(Step(
            "Lexia preflight bundle schema",
            [
                sys.executable,
                str(SCRIPTS / "check-lexia-bundle.py"),
                args.bundle_dir,
                "--verify-current",
                "--write-index",
                "--verify-index",
            ] + (["--fail-on-not-ready"] if args.bundle_fail_on_not_ready else []),
        ))
    return steps


def render_step_plan(steps: list[Step]) -> str:
    lines = ["=== Lexia preflight steps ==="]
    for index, step in enumerate(steps, 1):
        lines.append(f"{index}. {step.name}")
        lines.append(f"   $ {display_cmd(step.command)}")
    return "\n".join(lines)


def run_step(step: Step) -> int:
    print(f"\n--- {step.name} ---")
    print(f"$ {display_cmd(step.command)}")
    completed = subprocess.run(
        step.command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n")
    if completed.returncode == 0:
        print(f"[PASS] {step.name}")
    else:
        print(f"[FAIL] {step.name}: exit {completed.returncode}")
    return completed.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Lexia 同期前 read-only 一括ゲート")
    ap.add_argument("roots", nargs="*", default=list(DEFAULT_ROOTS), help="走査ルート（既定: outputs references）")
    ap.add_argument("--keep-going", action="store_true", help="失敗後も残りの検査を続ける")
    ap.add_argument("--list-steps", action="store_true", help="実行せず、展開後の検査手順だけ表示する")
    ap.add_argument("--skip-self-test", action="store_true", help="同期契約チェッカの self-test を実行しない")
    ap.add_argument("--final", action="store_true", help="最終同期前プロファイル。worklist 残件を失敗扱いにし、未追跡同期 HTML は許さない")
    ap.add_argument("--root-only", action="store_true", help="root 改善専用プロファイル。ROOT_TOOLING 以外の dirty 差分を gate 化し、生成差分があっても全検査を最後まで回す")
    ap.add_argument("--tooling-only", action="store_true", help="root/tooling 作業中プロファイル。tooling-only 差分 gate と生成 validator 横断実行を入れ、生成差分があっても全検査を最後まで回す")
    ap.add_argument("--stability-seconds", type=float, help="outputs/references HTML が観測中に変わらないか確認する秒数。0 で無効")
    ap.add_argument("--stability-attempts", type=int, default=1, help="stability check を安定するまで最大何回試すか")
    ap.add_argument("--stability-retry-delay-seconds", type=float, default=1.0, help="stability check の再試行間隔秒")
    ap.add_argument("--stability-json", help="check-lexia-stability.py の安定 JSON 出力先")
    ap.add_argument("--skip-rx", action="store_true", help="check-rx-coverage.py を実行しない")
    ap.add_argument("--no-rx-strict", action="store_true", help="RX UNREACHABLE を終了コード 1 にしない")
    ap.add_argument("--bundle-dir", help="Lexia 同期前監査の manifest/worklist/RX JSON 一式を出すディレクトリ")
    ap.add_argument("--bundle-fail-on-not-ready", action="store_true", help="bundle 検証時に gates.ready=false なら失敗させる。--final では自動有効")
    ap.add_argument("--change-summary-json", help="lexia-change-summary.py の安定 JSON 出力先")
    ap.add_argument("--change-summary-limit", type=int, help="lexia-change-summary.py の標準出力に出すパス数上限。--root-only/--tooling-only 既定は 8")
    ap.add_argument("--change-summary-untracked-files", choices=("all", "normal", "no"), help="lexia-change-summary.py --untracked-files へ渡す値")
    ap.add_argument("--change-fail-preset", action="append", choices=CHANGE_FAIL_PRESETS, default=[], help="change summary の fail-on-group プリセット（例: root-tooling-only, tooling-only, sync-ready）")
    ap.add_argument("--change-fail-on-group", action="append", choices=CHANGE_GROUPS, default=[], help="指定した dirty change group があれば preflight を失敗させる（複数回指定可）")
    ap.add_argument("--rx-json", help="check-rx-coverage.py の安定 JSON 出力先")
    ap.add_argument("--generated-validators", action="store_true", help="outputs/ux の ARIADNE/RX/TREE 個別バリデータを横断実行する")
    ap.add_argument("--generated-validator-root", default="outputs/ux", help="check-generated-validators.py の走査ルート")
    ap.add_argument("--generated-validator-target", action="append", choices=("ariadne", "rx", "tree"), default=[], help="横断実行する個別バリデータ対象（複数回指定可）")
    ap.add_argument("--generated-validator-json", help="check-generated-validators.py の安定 JSON 出力先")
    ap.add_argument("--generated-validator-fail-on-warning", action="store_true", help="横断バリデータの WARNING を preflight 失敗扱いにする")
    ap.add_argument("--generated-validator-show-warnings", action="store_true", help="横断バリデータの WARNING ファイル/グループを一行表示する")
    ap.add_argument("--json", help="check-lexia-sync-contract.py の導出メタ JSON 出力先")
    ap.add_argument("--json-format", choices=("entries", "manifest"), help="check-lexia-sync-contract.py --json の出力形式")
    ap.add_argument("--compare-sync-manifest", help="既存 lexia-sync-manifest.json と今回生成する manifest を比較する")
    ap.add_argument("--manifest-diff-json", help="compare-lexia-manifests.py の安定 JSON 出力先")
    ap.add_argument("--manifest-diff-fail-on-content-change", action="store_true", help="stableSha256 が変わる本文差分があれば preflight を失敗させる")
    ap.add_argument("--allow-untracked-sync-artifacts", action="store_true", help="outputs/references 配下の未追跡 HTML を同期エラーにしない（ローカル作業中のみ）")
    ap.add_argument("--worklist-markdown", help="内容改善セッション用 worklist Markdown 出力先")
    ap.add_argument("--worklist-json", help="内容改善セッション用 worklist JSON 出力先")
    ap.add_argument("--worklist-json-format", choices=("items", "manifest"), help="lexia-content-worklist.py --json の出力形式")
    ap.add_argument("--worklist-prompts-dir", help="target ごとの子セッション用プロンプト出力ディレクトリ")
    ap.add_argument("--worklist-target", action="append", default=[], help="worklist/prompt を指定 target に絞る（複数回指定可）")
    ap.add_argument("--worklist-fail-on", choices=("any", "error", "todo", "warn"), help="worklist item が残っていれば severity に応じて preflight を失敗させる")
    args = ap.parse_args()

    if args.final and args.tooling_only:
        print("[ERROR] --final と --tooling-only は同時に指定できません")
        return 2
    if args.final and args.root_only:
        print("[ERROR] --final と --root-only は同時に指定できません")
        return 2
    if args.root_only and args.tooling_only:
        print("[ERROR] --root-only と --tooling-only は同時に指定できません")
        return 2
    apply_root_only_defaults(args)
    apply_tooling_only_defaults(args)
    apply_final_defaults(args)
    apply_bundle_defaults(args)

    if args.final and args.allow_untracked_sync_artifacts:
        print("[ERROR] --final と --allow-untracked-sync-artifacts は同時に指定できません")
        return 2
    if args.stability_seconds is not None and args.stability_seconds < 0:
        print("[ERROR] --stability-seconds は 0 以上で指定してください")
        return 2
    if args.stability_attempts < 1:
        print("[ERROR] --stability-attempts は 1 以上で指定してください")
        return 2
    if args.stability_retry_delay_seconds < 0:
        print("[ERROR] --stability-retry-delay-seconds は 0 以上で指定してください")
        return 2
    if args.change_summary_limit is not None and args.change_summary_limit < 1:
        print("[ERROR] --change-summary-limit は 1 以上で指定してください")
        return 2
    if args.stability_json and (not args.stability_seconds or args.stability_seconds <= 0):
        print("[ERROR] --stability-json は --stability-seconds が 0 より大きい場合だけ指定できます")
        return 2
    if args.json_format and not args.json:
        print("[ERROR] --json-format は --json と一緒に指定してください")
        return 2
    if args.compare_sync_manifest and (not args.json or args.json_format != "manifest"):
        print("[ERROR] --compare-sync-manifest は --json と --json-format manifest と一緒に指定してください")
        return 2
    if args.manifest_diff_json and not args.compare_sync_manifest:
        print("[ERROR] --manifest-diff-json は --compare-sync-manifest と一緒に指定してください")
        return 2
    if args.manifest_diff_fail_on_content_change and not args.compare_sync_manifest:
        print("[ERROR] --manifest-diff-fail-on-content-change は --compare-sync-manifest と一緒に指定してください")
        return 2
    if args.worklist_json_format and not args.worklist_json:
        print("[ERROR] --worklist-json-format は --worklist-json と一緒に指定してください")
        return 2
    if (args.generated_validator_json or args.generated_validator_fail_on_warning or args.generated_validator_show_warnings or args.generated_validator_target) and not args.generated_validators:
        print("[ERROR] generated-validator 系オプションは --generated-validators と一緒に指定してください")
        return 2

    roots, missing = resolve_roots(args.roots)
    if missing:
        print("[ERROR] 走査ルートが存在しない: " + ", ".join(missing))
        return 2

    print("=== Lexia preflight ===")
    print("roots=" + ", ".join(Path(r).relative_to(ROOT).as_posix() if Path(r).is_relative_to(ROOT) else r for r in roots))

    steps = build_steps(args, roots)
    if args.list_steps:
        print()
        print(render_step_plan(steps))
        return 0

    failed_steps: list[tuple[str, int]] = []
    for step in steps:
        rc = run_step(step)
        if rc != 0:
            failed_steps.append((step.name, rc))
            if not args.keep_going:
                print("\n=== summary ===")
                print(f"FAIL={len(failed_steps)} / stopped at: {step.name} (exit {rc})")
                return 1

    print("\n=== summary ===")
    if failed_steps:
        print(f"FAIL={len(failed_steps)}")
        print("failed steps: " + ", ".join(name for name, _rc in failed_steps))
        print("failed step exits: " + ", ".join(f"{name}={rc}" for name, rc in failed_steps))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
