#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lightweight self-test for check-rx-coverage-manifest.py."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("check-rx-coverage-manifest.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RxCoverageManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = load_module("check_rx_coverage_manifest", SCRIPT)
        self.rx = self.checker.load_rx_module()

    def counts(self, **overrides):
        data = {
            "jx": 1,
            "present": 2,
            "referenced": 1,
            "uncovered": 1,
            "unreachable": 0,
            "safetynet": 1,
            "dangling": 0,
            "ok": 1,
            "ari_missing": 0,
        }
        data.update(overrides)
        return data

    def subject(self, **overrides):
        data = {
            "subject": "001_刑法",
            **self.counts(),
            "danglingDetail": [],
            "unreachableDetail": [],
        }
        data.update(overrides)
        return data

    def payload(self, **overrides):
        data = {
            "schemaVersion": self.rx.SCHEMA_VERSION,
            "filter": "",
            "strict": True,
            "supplementCap": self.rx.SUPPLEMENT_CAP,
            "fail": False,
            "counts": self.counts(),
            "subjects": [self.subject()],
            "skippedSubjects": ["002_刑事訴訟法"],
        }
        data.update(overrides)
        return data

    def test_valid_manifest_passes(self) -> None:
        errors = self.checker.validate_manifest(self.rx, self.payload())
        self.assertEqual([], errors)

    def test_array_payload_is_rejected(self) -> None:
        errors = self.checker.validate_manifest(self.rx, [self.payload()])
        self.assertTrue(any("manifest object expected" in error for error in errors), errors)

    def test_schema_counts_and_fail_are_checked(self) -> None:
        payload = self.payload(
            schemaVersion="bad",
            fail=False,
            counts=self.counts(unreachable=1),
        )
        errors = self.checker.validate_manifest(self.rx, payload)
        self.assertTrue(any("schemaVersion mismatch" in error for error in errors), errors)
        self.assertTrue(any("counts mismatch" in error for error in errors), errors)
        self.assertTrue(any("fail mismatch" in error for error in errors), errors)

    def test_count_invariants_are_checked(self) -> None:
        subject = self.subject(
            present=3,
            referenced=3,
            uncovered=2,
            unreachable=1,
            safetynet=0,
            dangling=0,
            ok=2,
            ari_missing=2,
        )
        payload = self.payload(counts={key: subject[key] for key in self.checker.COUNT_FIELDS}, subjects=[subject])
        errors = self.checker.validate_manifest(self.rx, payload)
        self.assertTrue(any("expected unreachable+safetynet" in error for error in errors), errors)
        self.assertTrue(any("present/referenced/uncovered/dangling counts are inconsistent" in error for error in errors), errors)
        self.assertTrue(any("ok: cannot exceed jx" in error for error in errors), errors)
        self.assertTrue(any("ari_missing: cannot exceed jx" in error for error in errors), errors)

    def test_subject_detail_values_are_checked(self) -> None:
        subject = self.subject(
            subject="",
            danglingDetail=[{"jx": "", "rx": [""]}],
            unreachable=1,
            unreachableDetail=[{"jx": "刑JX001", "rx": [{"code": "", "reason": ""}]}],
        )
        errors = self.checker.validate_manifest(self.rx, self.payload(subjects=[subject]))
        self.assertTrue(any("subject: expected non-empty" in error for error in errors), errors)
        self.assertTrue(any("danglingDetail" in error for error in errors), errors)
        self.assertTrue(any("unreachableDetail" in error for error in errors), errors)

    def test_verify_current_detects_stale_manifest(self) -> None:
        payload = self.payload()
        current = self.payload(counts=self.counts(present=3), subjects=[self.subject(present=3)])
        old_current_payload = self.checker.current_payload
        try:
            self.checker.current_payload = lambda _rx, _filter, _strict: self.checker.comparable_payload(current)
            errors = self.checker.validate_against_current(self.rx, payload)
        finally:
            self.checker.current_payload = old_current_payload
        self.assertTrue(any("current counts mismatch" in error for error in errors), errors)
        self.assertTrue(any("current subjects mismatch" in error for error in errors), errors)

    def test_verify_current_passes_when_projection_matches(self) -> None:
        payload = self.payload()
        old_current_payload = self.checker.current_payload
        try:
            self.checker.current_payload = lambda _rx, _filter, _strict: self.checker.comparable_payload(payload)
            errors = self.checker.validate_against_current(self.rx, payload)
        finally:
            self.checker.current_payload = old_current_payload
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
