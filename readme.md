# reasoning-lab

Measuring how different strategies change an AI's ability to find
no-four-in-plane configurations (OEIS A280537): no four points on
an n×n×n grid may lie on the same plane.

Every answer is checked by code, so improvement is measured by
numbers, not by the AI agreeing with itself.

## Status
- Week 1: upgrading the checker and running a baseline (no help given to the AI)

## Files
- `checker.py`: checks a set of points and reports every problem (points outside the grid, duplicates, how many 4-point sets lie on one plane, and which points cause the most problems). Upgraded from `verify4.py` in a280537-n28.

```
python3 checker.py points.txt
```

## Related
- [a280537-n28](https://github.com/parkseyoung1215-netizen/a280537-n28): my n=28 result (58 points; the best bound derivable from published values was 57)
