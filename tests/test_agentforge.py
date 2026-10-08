#!/usr/bin/env python3
"""AgentForge regression suite: Interface Integrity Gate (I1-I9) and scripts/af.py / install.sh tooling.

Run: python3 tests/test_agentforge.py   (or: python3 -m unittest tests/test_agentforge.py)
Requires PyYAML. Deterministic: no network, temp dirs only, HOME redirected for install.sh.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
AF = os.path.join(ROOT, "scripts", "af.py")
INSTALL = os.path.join(ROOT, "install.sh")


def run(args, cwd=None, env=None):
    return subprocess.run(args, capture_output=True, text=True, cwd=cwd, env=env)


def af(*args, cwd=None):
    return run([sys.executable, AF, *args], cwd=cwd)


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="af-test-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def write(self, name, data, base=None):
        path = os.path.join(base or self.tmp, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            if isinstance(data, str):
                f.write(data)
            else:
                yaml.safe_dump(data, f, sort_keys=False)
        return path


def contract(**over):
    d = {
        "id": "T-1",
        "level": "L2",
        "risk": "medium",
        "objective": "do a thing",
        "context": {"interfaces": "none_modified"},
        "scope": {"allowed_files": ["src/a.py"]},
        "acceptance_criteria": ["works"],
        "verification": {"commands": ["python3 -m unittest"], "gates": ["G1", "G5"]},
    }
    d.update(over)
    for k in [k for k, v in d.items() if v is ...]:
        del d[k]
    return d


def report(**over):
    d = {
        "contract": "T-1",
        "task": "do a thing",
        "status": "DONE",
        "verified": True,
        "interface_changes": "none",
        "verification_results": [
            {"gate": "G1", "result": "pass", "evidence": "ok"},
            {"gate": "G5", "result": "pass", "evidence": "ok"},
        ],
    }
    d.update(over)
    return d


class InterfaceIntegrityGate(TempDirCase):
    """Batería I1-I9."""

    def validate(self, d, *extra):
        p = self.write("c.yaml", d)
        return af("validate", p, *extra)

    def assertRejectedForInterfaces(self, d):
        r = self.validate(d)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("interfaces", r.stdout)

    def test_i1_none_modified_passes(self):
        r = self.validate(contract())
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("ok (task)", r.stdout)

    def test_i1_top_level_none_modified_passes(self):
        r = self.validate(contract(context=..., interfaces="none_modified"))
        self.assertEqual(r.returncode, 0, r.stdout)

    # I2..I7: a task that mutates an interface must declare it; omitting or emptying the declaration fails.
    MUTATIONS = {
        "i2_add_field": {"produces": ["Order.discount (new field)"]},
        "i3_remove_field": {"produces": ["Order.legacy_id (removed)"]},
        "i4_rename_field": {"produces": ["Order.qty -> Order.quantity"]},
        "i5_change_type": {"produces": ["Order.price: int -> Decimal"]},
        "i6_signature": {"consumes": ["pricing.compute(order, tax) -> pricing.compute(order)"]},
        "i7_api_schema": {"produces": ["POST /orders response schema v2"]},
    }

    def test_i2_to_i7_mutation_without_declaration_fails(self):
        for name in self.MUTATIONS:
            with self.subTest(name):
                self.assertRejectedForInterfaces(contract(context=...))

    def test_i2_to_i7_mutation_with_empty_declaration_fails(self):
        for name in self.MUTATIONS:
            for empty in ({}, {"consumes": [], "produces": []}, None, ""):
                with self.subTest(name=name, empty=empty):
                    self.assertRejectedForInterfaces(contract(context={"interfaces": empty}))

    def test_i2_to_i7_mutation_with_declaration_passes(self):
        for name, decl in self.MUTATIONS.items():
            with self.subTest(name):
                r = self.validate(contract(context={"interfaces": decl}))
                self.assertEqual(r.returncode, 0, r.stdout)

    def test_i8_consumes_produces_declared_passes(self):
        d = contract(context={"interfaces": {"consumes": ["db.users"], "produces": ["GET /users"]}})
        r = self.validate(d)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_i9_l2_medium_missing_fails(self):
        self.assertRejectedForInterfaces(contract(context=...))
        self.assertIn("missing", self.validate(contract(context=...)).stdout)

    def test_i9_l2_medium_ambiguously_empty_fails(self):
        d = contract(context={"interfaces": {"consumes": [], "produces": []}})
        self.assertRejectedForInterfaces(d)
        self.assertIn("ambiguously empty", self.validate(d).stdout)

    def test_i9_applies_to_higher_risks(self):
        for risk, extra in (("high", {}), ("critical", {"human_gates": ["merge"]})):
            with self.subTest(risk):
                self.assertRejectedForInterfaces(contract(context=..., risk=risk, **extra))

    def test_i9_low_risk_not_required(self):
        r = self.validate(contract(context=..., risk="low"))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_cross_report_changes_vs_none_modified_fails(self):
        c = self.write("contract.yaml", contract())
        rep = self.write("report.yaml", report(interface_changes=["Order.discount added"]))
        r = af("validate", rep, "--contract", c)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("none_modified", r.stdout)

    def test_cross_report_none_vs_none_modified_passes(self):
        c = self.write("contract.yaml", contract())
        rep = self.write("report.yaml", report())
        r = af("validate", rep, "--contract", c)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_cross_report_changes_with_declared_interfaces_passes(self):
        c = self.write("contract.yaml", contract(context={"interfaces": {"produces": ["Order"]}}))
        rep = self.write("report.yaml", report(interface_changes=["Order.discount added"]))
        r = af("validate", rep, "--contract", c)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_report_without_interface_changes_fails(self):
        d = report()
        del d["interface_changes"]
        r = af("validate", self.write("r.yaml", d))
        self.assertEqual(r.returncode, 1)
        self.assertIn("interface_changes", r.stdout)


class TierResolution(unittest.TestCase):
    EXPECTED = {
        "claude-code": {
            "FAST": ("haiku", "low"), "STANDARD": ("sonnet", "medium"),
            "DEEP": ("opus", "high"), "MAX": ("fable", "xhigh"),
        },
        "antigravity": {
            "FAST": ("gemini-3.8-flash-low", "low"), "STANDARD": ("gemini-3.8-flash-medium", "medium"),
            "DEEP": ("gemini-3.1-pro-high", "high"), "MAX": ("gemini-3.1-pro-high", "xhigh"),
        },
    }

    def test_all_tiers_both_platforms(self):
        for platform, tiers in self.EXPECTED.items():
            for tier, (model, effort) in tiers.items():
                with self.subTest(platform=platform, tier=tier):
                    r = af("tier", tier, "--platform", platform)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertIn(f"tier={tier} model={model} effort={effort}", r.stdout)

    def test_tier_is_case_insensitive(self):
        r = af("tier", "fast", "--platform", "claude-code")
        self.assertEqual(r.returncode, 0)
        self.assertIn("tier=FAST", r.stdout)

    def test_unknown_tier_and_platform(self):
        self.assertEqual(af("tier", "ULTRA", "--platform", "claude-code").returncode, 2)
        self.assertEqual(af("tier", "FAST", "--platform", "nope").returncode, 2)

    def test_role_resolves_to_posture_tier(self):
        r = af("role", "executor", "--platform", "claude-code")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("tier=", r.stdout)
        self.assertEqual(af("role", "bogus", "--platform", "claude-code").returncode, 2)


class AgentValidation(TempDirCase):
    def agent(self, **over):
        d = {"name": "af-x", "role": "executor", "purpose": "does x", "default_tier": "STANDARD", "returns": "report"}
        d.update(over)
        return d

    def test_real_agent_files_are_not_yaml_but_valid_yaml_agent_is_ok(self):
        r = af("validate", self.write("agent.yaml", self.agent()))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("ok (agent)", r.stdout)

    def test_invalid_agent_rejected(self):
        for name, d in {
            "missing_field": {k: v for k, v in self.agent().items() if k != "purpose"},
            "bad_role": self.agent(role="wizard"),
            "bad_tier": self.agent(default_tier="HUGE"),
            "bad_delegate": self.agent(authority={"delegate": "everywhere"}),
        }.items():
            with self.subTest(name):
                r = af("validate", self.write(f"{name}.yaml", d))
                self.assertEqual(r.returncode, 1, r.stdout)


class ReportValidation(TempDirCase):
    def check(self, d, *extra):
        return af("validate", self.write("r.yaml", d), *extra)

    def test_valid_done_passes(self):
        r = self.check(report())
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("ok (report)", r.stdout)

    def test_done_with_verified_false_rejected(self):
        r = self.check(report(verified=False))
        self.assertEqual(r.returncode, 1)
        self.assertIn("verified: true", r.stdout)

    def test_done_with_not_run_rejected(self):
        res = [{"gate": "G1", "result": "pass", "evidence": "ok"}, {"gate": "G5", "result": "not_run"}]
        r = self.check(report(verification_results=res))
        self.assertEqual(r.returncode, 1)
        self.assertIn("not_run", r.stdout)

    def test_done_with_failed_gate_rejected(self):
        res = [{"gate": "G1", "result": "fail"}]
        self.assertEqual(self.check(report(verification_results=res)).returncode, 1)

    def test_pass_without_evidence_rejected(self):
        res = [{"gate": "G1", "result": "pass"}]
        self.assertEqual(self.check(report(verification_results=res)).returncode, 1)

    def test_done_with_concerns_accepts_not_run(self):
        res = [{"gate": "G1", "result": "pass", "evidence": "ok"}, {"gate": "G5", "result": "not_run"}]
        r = self.check(report(status="DONE_WITH_CONCERNS", verified=False, verification_results=res))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_invalid_status_rejected(self):
        self.assertEqual(self.check(report(status="WIN")).returncode, 1)

    def test_contract_cross_check_missing_gate(self):
        c = self.write("c.yaml", contract())
        res = [{"gate": "G1", "result": "pass", "evidence": "ok"}]
        r = self.check(report(verification_results=res), "--contract", c)
        self.assertEqual(r.returncode, 1)
        self.assertIn("contract gate G5 missing", r.stdout)

    def test_contract_cross_check_ok(self):
        c = self.write("c.yaml", contract())
        self.assertEqual(self.check(report(), "--contract", c).returncode, 0)


def git(cwd, *args):
    r = run(["git", *args], cwd=cwd)
    assert r.returncode == 0, f"git {args}: {r.stderr}"
    return r.stdout


class CheckScope(TempDirCase):
    CONTRACT_REL = ".agentforge/contracts/T-1.yaml"

    def setUp(self):
        super().setUp()
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        git(self.repo, "config", "commit.gpgsign", "false")
        self.write("src/a.py", "a = 1\n", base=self.repo)
        self.write("src/b.py", "b = 1\n", base=self.repo)
        self.contract_path = self.write(self.CONTRACT_REL, contract(scope={
            "allowed_files": ["src/a.py"], "excluded_areas": ["src/secret/"]}), base=self.repo)

    def commit_all(self, msg="c"):
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", msg)

    def scope(self, *extra):
        return af("check-scope", self.contract_path, *extra, cwd=self.repo)

    def test_untracked_contract_rejected(self):
        git(self.repo, "add", "src")
        git(self.repo, "commit", "-q", "-m", "base")
        r = self.scope()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("CONTRACT NOT TRACKED", r.stdout)

    def test_untracked_contract_allowed_with_flag(self):
        git(self.repo, "add", "src")
        git(self.repo, "commit", "-q", "-m", "base")
        self.write("src/a.py", "a = 2\n", base=self.repo)
        r = self.scope("--allow-untracked-contract")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("not tracked", r.stderr)

    def test_in_scope_change_passes(self):
        self.commit_all()
        self.write("src/a.py", "a = 2\n", base=self.repo)
        r = self.scope()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("G5 scope: pass", r.stdout)

    def test_contract_modification_rejected(self):
        self.commit_all()
        wider = contract(scope={"allowed_files": ["src/a.py", "src/b.py"]})
        self.write(self.CONTRACT_REL, wider, base=self.repo)
        self.write("src/b.py", "b = 2\n", base=self.repo)
        r = self.scope()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("CONTRACT MODIFIED", r.stdout)
        # scope is read from the base revision, so widening does not legalise src/b.py
        self.assertIn("OUT OF SCOPE (not in scope): src/b.py", r.stdout)

    def test_out_of_scope_modified_and_new_files_detected(self):
        self.commit_all()
        self.write("src/b.py", "b = 2\n", base=self.repo)
        self.write("src/new.py", "n = 1\n", base=self.repo)
        r = self.scope()
        self.assertEqual(r.returncode, 1)
        self.assertIn("OUT OF SCOPE (not in scope): src/b.py", r.stdout)
        self.assertIn("OUT OF SCOPE (not in scope): src/new.py", r.stdout)

    def test_excluded_area_detected(self):
        self.commit_all()
        c = contract(scope={"allowed_directories": ["src/"], "excluded_areas": ["src/secret/"]})
        self.write(self.CONTRACT_REL, c, base=self.repo)
        self.commit_all("widen")
        self.write("src/secret/k.py", "k = 1\n", base=self.repo)
        r = self.scope()
        self.assertEqual(r.returncode, 1)
        self.assertIn("OUT OF SCOPE (excluded_area): src/secret/k.py", r.stdout)

    def test_own_report_is_exempt(self):
        self.commit_all()
        self.write(".agentforge/reports/T-1.yaml", report(), base=self.repo)
        self.write("src/a.py", "a = 3\n", base=self.repo)
        self.assertEqual(self.scope().returncode, 0)


class InstallScript(TempDirCase):
    def test_agents_dry_run_uses_symlinks(self):
        home = os.path.join(self.tmp, "home")
        os.makedirs(home)
        env = {**os.environ, "HOME": home}
        r = run(["bash", INSTALL, "--agents", "--dry-run"], env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        agent_lines = [l for l in r.stdout.splitlines() if l.startswith("[dry-run] ln -s") and "/agents/" in l]
        names = sorted(f for f in os.listdir(os.path.join(ROOT, "adapters", "claude-code", "agents")) if f.endswith(".md"))
        self.assertTrue(names)
        for n in names:
            with self.subTest(agent=n):
                self.assertTrue(any(l.endswith(os.path.join(home, ".claude", "agents", n)) and f"/{n} " in l for l in agent_lines), r.stdout)
        # dry-run must not touch the filesystem
        self.assertEqual(os.listdir(home), [])

    def test_unknown_flag_is_usage_error(self):
        self.assertEqual(run(["bash", INSTALL, "--bogus"]).returncode, 2)


if __name__ == "__main__":
    unittest.main()
