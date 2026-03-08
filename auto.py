#!/usr/bin/env python
"""
Auto-select axial SeriesNumber and run map_axial_slices.py.

用法（CMD）:
  set CASE=21386803
  python auto_map_axial.py

它会扫描 H:\MR\<CASE>\axial 中的 DICOM，选取切片数最多的 SeriesNumber，
然后调用 map_axial_slices.py，输出到 E:\segment1\total-result\<CASE>\axial_slices。
如路径不同，改下面 MR_ROOT/OUT_ROOT。
"""

import collections
import os
import subprocess
from pathlib import Path

import pydicom

MR_ROOT = Path(r"H:\MR")
OUT_ROOT = Path(r"E:\segment1\total-result")


def pick_series(axial_dir: Path) -> int:
    counts = collections.Counter()
    for f in axial_dir.glob("*.dcm"):
        try:
            ds = pydicom.dcmread(f, stop_before_pixels=True)
            counts.update([ds.SeriesNumber])
        except Exception:
            pass
    if not counts:
        raise SystemExit(f"轴位目录中未找到 DICOM: {axial_dir}")
    series = max(counts, key=counts.get)
    print(f"选用 SeriesNumber={series}, counts={dict(counts)}")
    return series


def main():
    case = os.environ.get("CASE")
    if not case:
        raise SystemExit("请先在 CMD 里 set CASE=病例号")

    axial_dir = MR_ROOT / case / "axial"
    series = pick_series(axial_dir)

    vertebrae_csv = OUT_ROOT / case / "vertebrae.csv"
    export_dir = OUT_ROOT / case / "axial_slices"
    output_csv = OUT_ROOT / case / "axial_targets.csv"

    cmd = [
        "python",
        "map_axial_slices.py",
        "--vertebrae-csv",
        str(vertebrae_csv),
        "--sagittal-dicom-dir",
        str(MR_ROOT / case / "sagittal"),
        "--axial-dicom-dir",
        str(axial_dir),
        "--axial-series",
        str(series),
        "--export-dir",
        str(export_dir),
        "--output-csv",
        str(output_csv),
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
