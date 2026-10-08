#!/usr/bin/env python3
"""AgentForge helper: deterministic checks that are cheaper than asking a model.

  af.py tier <TIER> --platform <claude-code|antigravity>   model/effort for a tier
  af.py role <executor|reviewer|orchestrator> --platform P  tier + model/effort for a role (active posture)
  af.py validate [--contract C] <contract|report|agent.yaml>...  structural check by kind; --contract also checks a report's gates and interface coherence
  af.py check-scope <contract.yaml> [--base REF] [--allow-untracked-contract]
                                                            gate G5: changes since REF (default HEAD) vs contract scope
  af.py init [PROJECT_DIR]                                  create .agentforge/ with CONTEXT.md

Exit codes: 0 ok, 1 check failed, 2 usage/config error. Requires PyYAML.
"""
import argparse
import os
import re
import shlex
import subprocess
import sys

def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


try:
    import yaml
except ImportError:
    die("af.py: PyYAML is required (pip install pyyaml)")

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PROFILES = os.path.join(ROOT, "routing", "profiles.yaml")

LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5"]
RISKS = ["low", "medium", "high", "critical"]
TIERS = ["FAST", "STANDARD", "DEEP", "MAX"]
# Single status vocabulary for delegated answers and reports (methodology/routing.md §4).
STATUS = ["DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED", "ESCALATE", "FAILED"]
DELEGATION = ["none", "down", "any"]
GATE_RESULTS = ["pass", "fail", "not_run"]
TASK_REQUIRED = {
    "L2": ["id", "level", "risk", "objective", "scope", "acceptance_criteria", "verification"],
    "L3": ["context", "routing"],
}


def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as e:
        die(f"af.py: cannot read {path}: {e}")


def platform_cfg(platform):
    prof = load_yaml(PROFILES)
    plat = prof.get("platforms", {}).get(platform)
    if not plat:
        die(f"af.py: unknown platform '{platform}' (see routing/profiles.yaml)")
    return prof, plat


def print_tier(plat, tier):
    t = plat.get("tiers", {}).get(tier)
    if not t:
        die(f"af.py: unknown tier '{tier}' (expected one of {TIERS})")
    # Shell-safe assignments: `eval "$(af.py tier DEEP --platform claude-code)"` sets $model and $effort.
    print(f"tier={tier} model={shlex.quote(t['model'])} effort={shlex.quote(t['effort'])}")
    if t.get("alternative"):
        print(f"alternative={shlex.quote(t['alternative'])}")


def cmd_tier(a):
    _, plat = platform_cfg(a.platform)
    print_tier(plat, a.tier.upper())


def cmd_role(a):
    prof, plat = platform_cfg(a.platform)
    posture = prof.get("postures", {}).get(prof.get("active_posture", "default"), {})
    tier = posture.get(a.role)
    if not tier:
        die(f"af.py: role '{a.role}' not in active posture")
    print_tier(plat, tier)


def is_empty(v):
    return v is None or v == "" or v == [] or v == {} or (isinstance(v, str) and v.strip() in ("...", "-"))


IFACE_RISKS = ["medium", "high", "critical"]
NONE_MODIFIED = "none_modified"


def get_interfaces(d):
    """Interface declaration: context.interfaces (template location) or top-level interfaces."""
    ctx = d.get("context")
    if isinstance(ctx, dict) and "interfaces" in ctx:
        return ctx["interfaces"]
    return d.get("interfaces")


def interface_errors(d):
    """Interface Integrity Gate (contract side): L2+ with risk >= medium must declare interfaces explicitly."""
    ifc = get_interfaces(d)
    if ifc == NONE_MODIFIED:
        return []
    if isinstance(ifc, dict) and (ifc.get("consumes") or ifc.get("produces")):
        return []
    if ifc is None:
        why = "missing"
    elif isinstance(ifc, dict):
        why = "ambiguously empty"
    else:
        why = "invalid"
    return [f"interfaces {why} (required at L2+ with risk medium/high/critical): "
            f"declare 'interfaces: {NONE_MODIFIED}' or a dict with non-empty consumes/produces"]


def validate_task(d):
    errs = []
    level = d.get("level")
    if level not in LEVELS:
        errs.append(f"level must be one of {LEVELS}")
        level = "L2"  # keep checking as the lightest written contract, so every error is reported at once
    required = []
    for lv, fields in TASK_REQUIRED.items():
        if LEVELS.index(level) >= LEVELS.index(lv):
            required += fields
    errs += [f"missing or empty field '{k}' (required at {level})" for k in required if is_empty(d.get(k))]
    if d.get("risk") is not None and d["risk"] not in RISKS:
        errs.append(f"risk must be one of {RISKS}")
    crit = d.get("acceptance_criteria") or []
    if any(is_empty(c) for c in crit):
        errs.append("acceptance_criteria contains placeholder entries")
    r = d.get("routing") or {}
    if r.get("preferred_tier") not in (None, *TIERS):
        errs.append(f"routing.preferred_tier must be one of {TIERS}")
    if r.get("allow_delegation") not in (None, *DELEGATION):
        errs.append(f"routing.allow_delegation must be one of {DELEGATION}")
    if LEVELS.index(level) >= LEVELS.index("L2") and d.get("risk") in IFACE_RISKS:
        errs += interface_errors(d)
    if d.get("risk") == "critical" and is_empty(d.get("human_gates")):
        errs.append("risk critical requires explicit human_gates")
    scope = d.get("scope") or {}
    if "scope" in required and not (scope.get("allowed_files") or scope.get("allowed_directories")):
        errs.append("scope needs allowed_files or allowed_directories")
    if "verification" in required and is_empty((d.get("verification") or {}).get("commands")):
        errs.append("verification.commands is empty: name at least one real, red-capable command")
    return errs


def task_warnings(d, path):
    warns = []
    scope = d.get("scope") or {}
    for p in (scope.get("allowed_files") or []) + (scope.get("allowed_directories") or []):
        if p.strip().rstrip("/*").count("/") == 0 and ("*" in p or p.endswith("/")):
            warns.append(f"broad scope '{p}': prefer concrete paths and list nearby sensitive areas in excluded_areas")
    folder = os.path.dirname(os.path.abspath(path))
    if d.get("id") and os.path.basename(folder) == "contracts":
        for f in sorted(os.listdir(folder)):
            other = os.path.join(folder, f)
            if f.endswith((".yaml", ".yml")) and other != os.path.abspath(path):
                if (load_yaml(other) or {}).get("id") == d["id"]:
                    warns.append(f"id '{d['id']}' already used by {f}")
    return warns


AGENT_REQUIRED = ["name", "role", "purpose", "default_tier", "returns"]
AGENT_ROLES = ["executor", "specialist", "reviewer"]


def validate_agent(d):
    errs = [f"missing or empty field '{k}'" for k in AGENT_REQUIRED if is_empty(d.get(k))]
    if d.get("role") is not None and d["role"] not in AGENT_ROLES:
        errs.append(f"role must be one of {AGENT_ROLES}")
    if d.get("default_tier") is not None and d["default_tier"] not in TIERS:
        errs.append(f"default_tier must be one of {TIERS}")
    if (d.get("authority") or {}).get("delegate") not in (None, *DELEGATION):
        errs.append(f"authority.delegate must be one of {DELEGATION}")
    return errs


def classify(d):
    if "status" in d and "objective" not in d:
        return "report"
    if "objective" not in d and "level" not in d and ("default_tier" in d or "authority" in d):
        return "agent"
    return "task"


def validate_report(d, contract=None):
    errs = []
    if d.get("status") not in STATUS:
        errs.append(f"status must be one of {STATUS}")
    if is_empty(d.get("task")):
        errs.append("missing 'task'")
    results = d.get("verification_results") or []
    for v in results:
        if v.get("result") not in GATE_RESULTS:
            errs.append(f"gate {v.get('gate')}: result must be one of {GATE_RESULTS}")
        if v.get("result") == "pass" and is_empty(v.get("evidence")):
            errs.append(f"gate {v.get('gate')}: pass without evidence")
    if d.get("status") in ("DONE", "DONE_WITH_CONCERNS"):
        if not results:
            errs.append("status DONE without verification_results")
        if any(v.get("result") == "fail" for v in results):
            errs.append("status DONE with a failed gate")
        if d.get("status") == "DONE":
            if d.get("verified") is not True:
                errs.append("status DONE requires verified: true")
            errs += [f"status DONE with gate {v.get('gate')} {v.get('result')}" for v in results if v.get("result") == "not_run"]
        elif d.get("verified") is True and any(v.get("result") == "not_run" for v in results):
            errs.append("verified: true but some gate is not_run")
    ic = d.get("interface_changes")
    if is_empty(ic):
        errs.append("missing 'interface_changes' (use 'none' or a non-empty list of changes)")
    elif ic != "none" and not (isinstance(ic, list) and all(not is_empty(c) for c in ic)):
        errs.append("interface_changes must be 'none' or a non-empty list of changes")
    if contract is not None:
        if get_interfaces(contract) == NONE_MODIFIED and not is_empty(ic) and ic != "none":
            errs.append("interface_changes declares changes but the contract declared 'interfaces: none_modified'")
        reported = {str(v.get("gate")) for v in results}
        errs += [f"contract gate {g} missing from verification_results"
                 for g in (contract.get("verification") or {}).get("gates") or [] if str(g) not in reported]
    return errs


def cmd_validate(a):
    failed = False
    contract = load_yaml(a.contract) if a.contract else None
    for path in a.files:
        d = load_yaml(path)
        kind = classify(d)
        errs = validate_report(d, contract) if kind == "report" else validate_agent(d) if kind == "agent" else validate_task(d)
        for e in errs:
            print(f"{path}: {e}")
        for w in (task_warnings(d, path) if kind == "task" else []):
            print(f"{path}: warning: {w}")
        if not errs:
            print(f"{path}: ok ({kind})")
        failed |= bool(errs)
    sys.exit(1 if failed else 0)


def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        if not check:
            return None
        die(f"af.py: git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def git_paths(*args):
    # -z: raw paths, no quoting of non-ASCII names.
    return [p for p in git(*args, "-z").split("\0") if p]


def glob_re(pattern):
    """Path glob: `*` and `?` stay inside one segment, `**` crosses segments, a trailing `/` means the whole directory."""
    p = pattern.strip()
    if p.endswith("/"):
        p += "**"
    out, i = "", 0
    while i < len(p):
        if p.startswith("**/", i):
            out += "(?:.*/)?"; i += 3
        elif p.startswith("**", i):
            out += ".*"; i += 2
        elif p[i] == "*":
            out += "[^/]*"; i += 1
        elif p[i] == "?":
            out += "[^/]"; i += 1
        else:
            out += re.escape(p[i]); i += 1
    return re.compile(out + r"(?:/.*)?\Z")  # a pattern naming a directory also covers its contents


def matches(path, patterns):
    return any(glob_re(p).match(path) for p in patterns)


def cmd_check_scope(a):
    top = git("rev-parse", "--show-toplevel").strip()
    contract_rel = os.path.relpath(os.path.abspath(a.contract), top)
    d = load_yaml(a.contract)
    problems = []
    # Read the scope from the base revision when the contract is tracked, so editing it cannot widen it.
    at_base = git("-C", top, "show", f"{a.base}:{contract_rel}", check=False)
    if at_base is not None:
        base_d = yaml.safe_load(at_base) or {}
        if base_d != d:
            problems.append(f"CONTRACT MODIFIED since {a.base}: {contract_rel}")
        d = base_d
    elif a.allow_untracked_contract:
        print(f"warning: {contract_rel} is not tracked at {a.base}; scope edits to it cannot be detected", file=sys.stderr)
    else:
        problems.append(f"CONTRACT NOT TRACKED at {a.base}: {contract_rel} (commit it before delegating, or pass --allow-untracked-contract)")
    scope = d.get("scope") or {}
    allowed = (scope.get("allowed_files") or []) + (scope.get("allowed_directories") or [])
    excluded = scope.get("excluded_areas") or []
    if not allowed:
        die("af.py: contract has no allowed_files/allowed_directories")
    # Always-allowed deliverables: this contract's report; shared memory only with write_memory.
    exempt = [f".agentforge/reports/{d.get('id')}.yaml"]
    if (d.get("permissions") or {}).get("write_memory"):
        exempt += [".agentforge/CONTEXT.md", ".agentforge/decisions.md", ".agentforge/learnings.md"]
    changed = set(git_paths("-C", top, "diff", "--name-only", "--no-renames", a.base))
    changed |= set(git_paths("-C", top, "ls-files", "--others", "--exclude-standard"))
    changed -= {contract_rel}  # reported above as CONTRACT MODIFIED if it changed
    changed = {c for c in changed if c not in exempt}
    out = sorted(c for c in changed if matches(c, excluded) or not matches(c, allowed))
    for c in out:
        problems.append(f"OUT OF SCOPE ({'excluded_area' if matches(c, excluded) else 'not in scope'}): {c}")
    for p in problems:
        print(p)
    if not changed:
        print(f"warning: no changes against {a.base}; if the executor committed, pass --base <start commit>", file=sys.stderr)
    print(f"G5 scope: {'fail' if problems else 'pass'} — {len(changed)} changed, {len(out)} out of scope (base {a.base})")
    sys.exit(1 if problems else 0)


def cmd_init(a):
    target = os.path.join(a.project, ".agentforge")
    os.makedirs(target, exist_ok=True)
    ctx = os.path.join(target, "CONTEXT.md")
    if os.path.exists(ctx):
        print(f"{ctx} already exists; left untouched")
        return
    with open(os.path.join(ROOT, "contracts", "templates", "CONTEXT.md")) as src, open(ctx, "w") as dst:
        dst.write(src.read())
    print(f"created {ctx}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("tier"); s.add_argument("tier"); s.add_argument("--platform", required=True); s.set_defaults(f=cmd_tier)
    s = sub.add_parser("role"); s.add_argument("role"); s.add_argument("--platform", required=True); s.set_defaults(f=cmd_role)
    s = sub.add_parser("validate"); s.add_argument("files", nargs="+"); s.add_argument("--contract"); s.set_defaults(f=cmd_validate)
    s = sub.add_parser("check-scope"); s.add_argument("contract"); s.add_argument("--base", default="HEAD"); s.add_argument("--allow-untracked-contract", action="store_true"); s.set_defaults(f=cmd_check_scope)
    s = sub.add_parser("init"); s.add_argument("project", nargs="?", default="."); s.set_defaults(f=cmd_init)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
