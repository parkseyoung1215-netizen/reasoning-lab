"""Checker for no-four-in-plane (OEIS A280537), built for AI experiments.

Upgraded from verify4.py (a280537-n28). Instead of stopping at the first
problem, it reports *every* problem, so the result can be used as a score
and fed back to an AI:

- invalid points (outside the grid, duplicates)
- how many 4-point sets lie on one plane (0 means valid)
- a few example coplanar sets
- which points cause the most problems

Usage:
    python3 checker.py points.txt [--show 5]

File format (same as a280537-n28):
    first line: n k
    then k lines: x y z      (lines starting with # are ignored)
"""
import re
import sys
from collections import Counter
from itertools import combinations


def coplanar(a, b, c, d):
    """True if the four points lie on one plane (integer determinant is 0)."""
    u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    w = (d[0] - a[0], d[1] - a[1], d[2] - a[2])
    det = (u[0] * (v[1] * w[2] - v[2] * w[1])
           - u[1] * (v[0] * w[2] - v[2] * w[0])
           + u[2] * (v[0] * w[1] - v[1] * w[0]))
    return det == 0


def check_points(n, pts, max_examples=5):
    """Check a list of (x, y, z) points in the n x n x n grid {0..n-1}^3.

    Returns a dict:
        valid          True only if there are no problems at all
        n, submitted   grid size and number of points given
        outside        points outside the grid
        duplicates     points given more than once
        count          number of distinct points inside the grid
        num_coplanar   number of 4-point sets that lie on one plane
        examples       up to max_examples of those sets
        worst_points   points involved in the most coplanar sets
    """
    pts = [tuple(p) for p in pts]
    outside = [p for p in pts if not all(0 <= c < n for c in p)]
    counts = Counter(p for p in pts if p not in outside)
    duplicates = [p for p, c in counts.items() if c > 1]
    good = list(counts)  # distinct points inside the grid, in input order

    num_coplanar = 0
    examples = []
    blame = Counter()
    for quad in combinations(good, 4):
        if coplanar(*quad):
            num_coplanar += 1
            if len(examples) < max_examples:
                examples.append(quad)
            blame.update(quad)

    return {
        "valid": not outside and not duplicates and num_coplanar == 0,
        "n": n,
        "submitted": len(pts),
        "outside": outside,
        "duplicates": duplicates,
        "count": len(good),
        "num_coplanar": num_coplanar,
        "examples": examples,
        "worst_points": blame.most_common(5),
    }


def parse_points_text(text):
    """Pull every (x, y, z) integer triple out of free text, e.g. an AI answer.

    Accepts "(1, 2, 3)", "[1,2,3]" or "1 2 3" on its own line.
    """
    found = re.findall(r"[\(\[]\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*[\)\]]", text)
    if not found:
        found = re.findall(r"^\s*(-?\d+)\s+(-?\d+)\s+(-?\d+)\s*$", text, re.M)
    return [tuple(map(int, t)) for t in found]


def read_file(path):
    lines = [l.split() for l in open(path) if l.strip() and not l.startswith("#")]
    n, k = map(int, lines[0][:2])
    pts = [tuple(map(int, t[:3])) for t in lines[1:]]
    if len(pts) != k:
        print(f"note: header says {k} points but file has {len(pts)}")
    return n, pts


def report(r):
    """Human-readable summary (also usable as feedback text for an AI)."""
    out = []
    if r["valid"]:
        out.append(f"OK: n={r['n']}, {r['count']} points, no four in a plane")
        return "\n".join(out)
    out.append(f"FAIL: n={r['n']}, {r['submitted']} points submitted")
    if r["outside"]:
        out.append(f"- {len(r['outside'])} point(s) outside the grid 0..{r['n'] - 1}: {r['outside'][:5]}")
    if r["duplicates"]:
        out.append(f"- duplicate point(s): {r['duplicates'][:5]}")
    if r["num_coplanar"]:
        out.append(f"- {r['num_coplanar']} set(s) of 4 points lie on one plane, for example:")
        for q in r["examples"]:
            out.append("    " + " ".join(str(p) for p in q))
        out.append("- points in the most bad sets: "
                   + ", ".join(f"{p} ({c})" for p, c in r["worst_points"]))
    return "\n".join(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    show = 5
    if "--show" in args:
        i = args.index("--show")
        show = int(args[i + 1])
        del args[i:i + 2]
    for path in args:
        n, pts = read_file(path)
        print(path)
        print(report(check_points(n, pts, max_examples=show)))
