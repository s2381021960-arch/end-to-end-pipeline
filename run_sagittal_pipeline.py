#!/usr/bin/env python3
"""Run SpineNet on sagittal DICOM data and save results."""

import argparse
import csv
from pathlib import Path

import torch
import torch.serialization
import numpy as np

torch.serialization.add_safe_globals([np._core.multiarray.scalar])
_original_torch_load = torch.load


def _compat_torch_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(*args, **kwargs)


torch.load = _compat_torch_load

import spinenet
from spinenet.io import load_dicoms_from_folder, save_vert_dicts_to_csv

TARGET_IVD_LEVELS = {"L3-L4", "L4-L5", "L5-S1"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect vertebrae/discs on a sagittal MR stack with SpineNet",
    )
    parser.add_argument(
        "--input-folder",
        default=r"H:\MR\200008150\sagittal",
        help="????? DICOM ???????",
    )
    parser.add_argument(
        "--output-dir",
        default=r"E:\segment1\total-result\200008150",
        help="?? CSV/?? ???",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda:0"],
        help="?????auto ????? GPU",
    )
    parser.add_argument(
        "--require-extensions",
        action="store_true",
        help="?????? .dcm ??????????????",
    )
    return parser.parse_args()


def pick_device(flag: str) -> str:
    if flag != "auto":
        return flag
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def save_target_ivd_summary(ivd_dicts, output_dir: Path) -> None:
    summary_path = output_dir / "target_ivds.csv"
    fieldnames = ["level_name", "volume_shape"]
    with summary_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for ivd in ivd_dicts:
            if ivd["level_name"] in TARGET_IVD_LEVELS:
                shape_text = "x".join(str(dim) for dim in ivd["volume"].shape)
                writer.writerow({"level_name": ivd["level_name"], "volume_shape": shape_text})


def save_vert_slice_summary(vert_dicts, output_dir: Path) -> None:
    summary_path = output_dir / "vertebrae_slices.csv"
    fieldnames = ["predicted_label", "num_slices", "slice_nos"]
    with summary_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for vert in vert_dicts:
            writer.writerow(
                {
                    "predicted_label": vert.get("predicted_label", ""),
                    "num_slices": len(vert.get("slice_nos", [])),
                    "slice_nos": ";".join(str(idx) for idx in vert.get("slice_nos", [])),
                }
            )


def main() -> None:
    args = parse_args()
    input_folder = Path(args.input_folder)
    if not input_folder.exists():
        raise FileNotFoundError(f"???????: {input_folder}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] ?? DICOM?{input_folder}")
    scan = load_dicoms_from_folder(
        str(input_folder),
        require_extensions=args.require_extensions,
        metadata_overwrites={},
    )

    device = pick_device(args.device)
    print(f"[2/4] ??? SpineNet (device={device})")
    spnt = spinenet.SpineNet(device=device, scan_type="lumbar")

    print("[3/4] ??????")
    vert_dicts = spnt.detect_vb(scan.volume, scan.pixel_spacing)

    print("[4/4] ??????????")
    ivd_dicts = spnt.get_ivds_from_vert_dicts(vert_dicts, scan.volume)
    ivd_grades = spnt.grade_ivds(ivd_dicts)
    try:
        level_names = [ivd.get("level_name", "") for ivd in ivd_dicts]
        if len(level_names) == len(ivd_grades):
            ivd_grades.insert(0, "level_name", level_names)
        else:
            print("Warning: level_name count does not match ivd_grades rows; skipping level_name column")
    except Exception as exc:
        print(f"Warning: failed to attach level_name: {exc}")

    vert_csv = output_dir / "vertebrae.csv"
    print(f"?? vertebrae ?????{vert_csv}")
    save_vert_dicts_to_csv(vert_dicts, vert_csv)

    ivd_csv = output_dir / "ivd_grades.csv"
    print(f"????????{ivd_csv}")
    ivd_grades.to_csv(ivd_csv, index=False)

    save_vert_slice_summary(vert_dicts, output_dir)
    save_target_ivd_summary(ivd_dicts, output_dir)
    print("????? L3/L4?L4/L5?L5/S1 ??????? target_ivds.csv")


if __name__ == "__main__":
    main()
