#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-lexia-manifest.py."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-lexia-manifest.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LexiaManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_module("check_lexia_manifest", SCRIPT)
        self.contract = self.manifest.load_contract_module()

    def entry(self, source_path: str = "outputs/001_JX/001_刑法/刑JX001.html", **overrides):
        data = {
            "sourcePath": source_path,
            "fileName": source_path.rsplit("/", 1)[-1],
            "code": "刑JX001",
            "baseCode": "刑JX001",
            "title": "刑JX001",
            "subject": "刑法",
            "subjectDir": "001_刑法",
            "category": "JX",
            "bytes": 20480,
            "textLength": 1200,
            "stableSha256": "a" * 64,
            "generated": "2026-06-28T00:00+09:00",
        }
        data.update(overrides)
        return data

    def payload(self, entries=None, **overrides):
        entries = entries if entries is not None else [self.entry()]
        data = {
            "schemaVersion": self.contract.SCHEMA_VERSION,
            "roots": ["outputs", "references"],
            "html": len(entries),
            "classified": len(entries),
            "categories": {"JX": len(entries)},
            "errorCount": 0,
            "warningCount": 0,
            "entries": entries,
        }
        data.update(overrides)
        return data

    def test_valid_manifest_passes(self) -> None:
        errors = self.manifest.validate_manifest(self.contract, self.payload())
        self.assertEqual([], errors)

    def test_kjx_category_is_allowed(self) -> None:
        entry = self.entry(
            source_path="outputs/005_KJX/001_刑法/刑KJX001.html",
            code="刑KJX001",
            baseCode="刑KJX001",
            title="刑KJX001",
            category="KJX",
        )
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=[entry], categories={"KJX": 1}))
        self.assertEqual([], errors)

    def test_entries_array_is_rejected(self) -> None:
        errors = self.manifest.validate_manifest(self.contract, [self.entry()])
        self.assertTrue(any("manifest object expected" in error for error in errors), errors)

    def test_schema_and_field_order_are_checked(self) -> None:
        payload = self.payload(schemaVersion="bad")
        errors = self.manifest.validate_manifest(self.contract, payload)
        self.assertTrue(any("schemaVersion mismatch" in error for error in errors), errors)

        entry = self.entry()
        reordered = {"fileName": entry["fileName"], **{k: v for k, v in entry.items() if k != "fileName"}}
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=[reordered]))
        self.assertTrue(any("field order/keys mismatch" in error for error in errors), errors)

    def test_counts_sort_and_duplicates_are_checked(self) -> None:
        entries = [
            self.entry("outputs/001_JX/001_刑法/刑JX002.html", code="刑JX002", baseCode="刑JX002", title="刑JX002"),
            self.entry("outputs/001_JX/001_刑法/刑JX001.html"),
        ]
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=entries, classified=1))
        self.assertTrue(any("sourcePath order" in error for error in errors), errors)
        self.assertTrue(any("classified mismatch" in error for error in errors), errors)

        duplicate = [self.entry(), self.entry()]
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=duplicate))
        self.assertTrue(any("duplicate sourcePath" in error for error in errors), errors)
        self.assertTrue(any("duplicate fileName" in error for error in errors), errors)
        self.assertTrue(any("duplicate category+code" in error for error in errors), errors)

    def test_entry_values_are_checked(self) -> None:
        entry = self.entry(
            source_path=r"outputs\001_JX\001_刑法\刑JX001.html",
            fileName="wrong.html",
            category="BAD",
            bytes=0,
            textLength=0,
            stableSha256="BAD",
            generated="2026/06/28 00:00",
        )
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=[entry], categories={"BAD": 1}))
        self.assertTrue(any("forward slashes" in error for error in errors), errors)
        self.assertTrue(any("fileName" in error for error in errors), errors)
        self.assertTrue(any("unknown category" in error for error in errors), errors)
        self.assertTrue(any("positive integer" in error for error in errors), errors)
        self.assertTrue(any("invalid data-generated" in error for error in errors), errors)
        self.assertTrue(any("textLength" in error and "positive integer" in error for error in errors), errors)
        self.assertTrue(any("stableSha256" in error and "sha256" in error for error in errors), errors)

    def test_entry_metadata_must_match_source_path(self) -> None:
        entry = self.entry(
            code="刑JX999",
            baseCode="刑JX999",
            category="TX_OFFICIAL",
            subject="民法",
            subjectDir="003_民法",
        )
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=[entry], categories={"TX_OFFICIAL": 1}))
        self.assertTrue(any("entries[0].category" in error and "sourcePath-derived" in error for error in errors), errors)
        self.assertTrue(any("entries[0].code" in error and "'刑JX001'" in error for error in errors), errors)
        self.assertTrue(any("entries[0].baseCode" in error and "'刑JX001'" in error for error in errors), errors)
        self.assertTrue(any("entries[0].subject" in error and "'刑法'" in error for error in errors), errors)
        self.assertTrue(any("entries[0].subjectDir" in error and "'001_刑法'" in error for error in errors), errors)

    def test_source_path_must_stay_under_manifest_roots_and_be_html(self) -> None:
        outside = self.entry(source_path="docs/LEXIA.html", fileName="LEXIA.html")
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=[outside]))
        self.assertTrue(any("outside manifest roots" in error for error in errors), errors)

        non_html = self.entry(source_path="outputs/001_JX/001_刑法/刑JX001.txt", fileName="刑JX001.txt")
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=[non_html]))
        self.assertTrue(any("expected .html/.htm" in error for error in errors), errors)

        parent_segment = self.entry(source_path="outputs/../references/刑GDE001.html", fileName="刑GDE001.html")
        errors = self.manifest.validate_manifest(self.contract, self.payload(entries=[parent_segment]))
        self.assertTrue(any("parent path segments" in error for error in errors), errors)

    def test_malformed_roots_and_source_paths_do_not_raise(self) -> None:
        entry = self.entry(sourcePath=None, fileName=None, code=None)
        entry.pop("sourcePath")
        payload = self.payload(entries=["bad", entry], roots=["outputs", 123])
        errors = self.manifest.validate_manifest(self.contract, payload)
        self.assertTrue(any("roots: expected non-empty string list" in error for error in errors), errors)
        self.assertTrue(any("entries[0]: expected object" in error for error in errors), errors)
        self.assertTrue(any("entries[1]: field order/keys mismatch" in error for error in errors), errors)
        self.assertTrue(any("entries[1].fileName: expected non-empty string" in error for error in errors), errors)
        self.assertTrue(any("entries[1].code: expected non-empty string" in error for error in errors), errors)

    def test_verify_current_passes_when_projection_matches(self) -> None:
        payload = self.payload()
        old_current_payload = self.manifest.current_payload
        try:
            self.manifest.current_payload = lambda _contract, _roots: self.manifest.comparable_payload(self.contract, payload)
            self.assertEqual([], self.manifest.validate_against_current(self.contract, payload))
        finally:
            self.manifest.current_payload = old_current_payload

    def test_verify_current_detects_stale_manifest(self) -> None:
        payload = self.payload()
        current = self.payload(entries=[self.entry(bytes=40960, textLength=1600, stableSha256="b" * 64)])
        old_current_payload = self.manifest.current_payload
        try:
            self.manifest.current_payload = lambda _contract, _roots: self.manifest.comparable_payload(self.contract, current)
            errors = self.manifest.validate_against_current(self.contract, payload)
        finally:
            self.manifest.current_payload = old_current_payload
        self.assertTrue(any("current entries mismatch" in error for error in errors), errors)
        self.assertTrue(any("bytes" in error for error in errors), errors)
        self.assertTrue(any("textLength" in error for error in errors), errors)
        self.assertTrue(any("stableSha256" in error for error in errors), errors)

    def test_verify_current_detects_generated_only_drift(self) -> None:
        payload = self.payload()
        current = self.payload(entries=[self.entry(generated="2026-06-29T00:00+09:00")])
        old_current_payload = self.manifest.current_payload
        try:
            self.manifest.current_payload = lambda _contract, _roots: self.manifest.comparable_payload(self.contract, current)
            errors = self.manifest.validate_against_current(self.contract, payload)
        finally:
            self.manifest.current_payload = old_current_payload
        self.assertTrue(any("current entries mismatch" in error for error in errors), errors)
        self.assertTrue(any("generated-only drift" in error for error in errors), errors)

    def test_verify_current_detects_size_only_drift(self) -> None:
        payload = self.payload()
        current = self.payload(entries=[self.entry(bytes=40960, textLength=1600)])
        old_current_payload = self.manifest.current_payload
        try:
            self.manifest.current_payload = lambda _contract, _roots: self.manifest.comparable_payload(self.contract, current)
            errors = self.manifest.validate_against_current(self.contract, payload)
        finally:
            self.manifest.current_payload = old_current_payload
        self.assertTrue(any("bytes/textLength-only drift" in error for error in errors), errors)

    def test_verify_current_detects_error_count_drift(self) -> None:
        payload = self.payload()
        current = self.payload(errorCount=1, warningCount=1)
        old_current_payload = self.manifest.current_payload
        try:
            self.manifest.current_payload = lambda _contract, _roots: self.manifest.comparable_payload(self.contract, current)
            errors = self.manifest.validate_against_current(self.contract, payload)
        finally:
            self.manifest.current_payload = old_current_payload
        self.assertTrue(any("current errorCount mismatch" in error for error in errors), errors)
        self.assertTrue(any("current warningCount mismatch" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
