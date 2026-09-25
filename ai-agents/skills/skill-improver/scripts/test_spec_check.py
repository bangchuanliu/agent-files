#!/usr/bin/env python3
"""Regression fixtures for spec_check.py.

    python3 scripts/test_spec_check.py

Every case here is a bug that actually shipped. Four of them were false
positives - a checker that cries wolf gets ignored, which is worse than not
having one - so each fix is pinned by a test that fails without it.

Exit 0 = all pass, 1 = failures.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "spec_check.py")

GOOD_FM = ('---\nname: {name}\nkind: leaf\n'
           'description: "Use when: demos. NOT for: creation -> use skill-creator"\n---\n\n')


def build(root, name, skill_md, files=None):
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(skill_md)
    for rel, content in (files or {}).items():
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(content)
    return d


def run(path, *extra):
    proc = subprocess.run([sys.executable, CHECKER, path, *extra],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


CASES = []


def case(fn):
    CASES.append(fn)
    return fn


@case
def house_routing_arrow_is_allowed(root):
    """'NOT for: X -> use Y' is the house convention; '>' there is not markup."""
    d = build(root, "arrow", GOOD_FM.format(name="arrow") + "body\n")
    _, out = run(d)
    return "breaks strict validators" not in out, out


@case
def real_angle_brackets_still_flagged(root):
    """But a genuine <placeholder> must still fail."""
    fm = ('---\nname: angle\nkind: leaf\n'
          'description: "Use when: running <build> commands."\n---\n\nbody\n')
    d = build(root, "angle", fm)
    _, out = run(d)
    return "breaks strict validators" in out, out


@case
def non_mapping_frontmatter_does_not_crash(root):
    """A YAML list where a mapping belongs must be a finding, not a traceback."""
    d = build(root, "nonmap", "---\n- a\n- b\n---\n\nbody\n")
    _, out = run(d)
    return "Traceback" not in out and "must be a YAML mapping" in out, out


@case
def link_title_is_not_part_of_the_path(root):
    """[Guide](references/g.md "Title") resolves to references/g.md."""
    d = build(root, "title", GOOD_FM.format(name="title")
              + '[Guide](references/g.md "Title")\n',
              {"references/g.md": "# g\n"})
    _, out = run(d)
    return "broken link" not in out, out


@case
def literal_markdown_example_is_not_a_link(root):
    """A skill documenting markdown syntax contains `[text](url)` as an example."""
    d = build(root, "literal", GOOD_FM.format(name="literal")
              + "Do NOT use: `[text](url)` in chat.\n\n~~~\n[other](nope.md)\n~~~\n")
    _, out = run(d)
    return "broken link" not in out, out


@case
def odd_number_of_fences_does_not_expose_inline_code(root):
    """An unbalanced fence must not let the inline-code pass span lines."""
    body = ("```\ncode\n```\n\nuse `[text](url)` here\n\n```\nstray open fence\n")
    d = build(root, "oddfence", GOOD_FM.format(name="oddfence") + body)
    _, out = run(d)
    return "broken link" not in out, out


@case
def genuinely_broken_link_still_flagged(root):
    d = build(root, "broken", GOOD_FM.format(name="broken") + "[Gone](references/x.md)\n")
    _, out = run(d)
    return "broken link" in out, out


@case
def reference_subdirectory_does_not_crash(root):
    """references/ may contain a directory; opening it as a file is a crash."""
    d = build(root, "subdir", GOOD_FM.format(name="subdir") + "see scripts/s.py\n",
              {"references/r.md": "# r\n", "references/sub/deep.md": "# d\n",
               "scripts/s.py": "#!/usr/bin/env python3\n"})
    _, out = run(d)
    return "Traceback" not in out, out


@case
def init_py_is_not_a_cli(root):
    """A package marker needs neither +x nor documentation."""
    d = build(root, "pkg", GOOD_FM.format(name="pkg") + "body\n",
              {"scripts/__init__.py": ""})
    _, out = run(d)
    return "__init__.py" not in out, out


@case
def directly_invoked_script_needs_executable_bit(root):
    """'./scripts/x.py' in the docs means +x is required, shebang or not."""
    d = build(root, "direct", GOOD_FM.format(name="direct") + "Run ./scripts/x.py now\n",
              {"scripts/x.py": "print(1)\n"})
    _, out = run(d)
    return "not executable" in out, out


@case
def interpreter_invoked_script_does_not_need_it(root):
    """'python3 scripts/x.py' does not require the executable bit."""
    d = build(root, "interp", GOOD_FM.format(name="interp")
              + "Run `python3 scripts/x.py` now\n", {"scripts/x.py": "print(1)\n"})
    _, out = run(d)
    return "not executable" not in out, out


@case
def empty_discovery_is_an_error(root):
    """--all over a directory with no skills must not look like a pass."""
    empty = os.path.join(root, "nothing")
    os.makedirs(empty, exist_ok=True)
    code, out = run(empty, "--all")
    return code == 2, f"exit={code} {out}"


@case
def exactly_500_body_lines_is_within_budget(root):
    """A trailing newline is not a 501st line."""
    d = build(root, "budget", GOOD_FM.format(name="budget")[:-1] + ("x\n" * 500))
    _, out = run(d)
    return "over the 500-line" not in out, out


@case
def clean_skill_is_clean(root):
    build(root, "skill-creator", GOOD_FM.format(name="skill-creator") + "stub\n")
    d = build(root, "clean", GOOD_FM.format(name="clean") + "body\n")
    code, out = run(d)
    return code == 0 and "clean" in out, f"exit={code} {out}"


@case
def dangling_route_is_flagged(root):
    """A NOT-for clause pointing at a renamed or absent skill is a real defect."""
    fm = ('---\nname: dangling\nkind: leaf\n'
          'description: "Use when: x. NOT for: y (no-such-skill-here)"\n---\n\nbody\n')
    d = build(root, "dangling", fm)
    _, out = run(d)
    return "not an installed skill" in out, out


@case
def user_invoked_description_is_not_house_routed(root):
    fm = ('---\nname: manual\nkind: leaf\ndisable-model-invocation: true\n'
          'description: "Manual-only maintenance helper."\n---\n\nbody\n')
    d = build(root, "manual", fm)
    _, out = run(d, "--house")
    return "description does not start" not in out and "has no 'NOT for:'" not in out, out


@case
def agents_frontmatter_accepts_supported_filter(root):
    fm = ('---\nname: filtered\nkind: leaf\nagents: claude, copilot\n'
          'description: "Use when: filtered demos. NOT for: creation -> use skill-creator"\n---\n\nbody\n')
    d = build(root, "filtered", fm)
    _, out = run(d)
    return "agents" not in out, out


@case
def all_discovery_skips_data_heavy_dirs(root):
    parent = os.path.join(root, "discover_parent")
    os.makedirs(parent, exist_ok=True)
    build(parent, "skill-creator", GOOD_FM.format(name="skill-creator") + "stub\n")
    build(parent, "real", GOOD_FM.format(name="real") + "body\n")
    build(parent, "data", "not frontmatter\n")
    code, out = run(parent, "--all")
    return code == 0 and "real" in out and "data" not in out, f"exit={code} {out}"


@case
def missing_kind_is_flagged(root):
    fm = ('---\nname: nokind\n'
          'description: "Use when: x. NOT for: y (z-skill)"\n---\n\nbody\n')
    d = build(root, "nokind", fm)
    _, out = run(d)
    return "no kind:" in out, out


def main():
    root = os.path.join(HERE, ".spec_check_fixtures")
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root, exist_ok=True)
    failures = []
    try:
        for fn in CASES:
            try:
                ok, detail = fn(root)
            except Exception as exc:                      # noqa: BLE001
                ok, detail = False, f"raised {exc!r}"
            print(f"{'PASS' if ok else 'FAIL'}  {fn.__name__}")
            if not ok:
                failures.append((fn.__name__, fn.__doc__ or "", detail))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print(f"\n{len(CASES) - len(failures)}/{len(CASES)} passed")
    for name, doc, detail in failures:
        print(f"\n{name}\n  expected: {doc.strip()}\n  got: {detail.strip()[:400]}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
