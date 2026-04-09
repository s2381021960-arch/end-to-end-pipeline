#!/usr/bin/env python3
"""Keep the largest connected component for each label in a segmentation mask."""

import argparse
from pathlib import Path
from typing import Iterable, List

import nibabel as nib
import numpy as np
from scipy import ndimage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Keep the largest connected component for each label in a NIfTI mask.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input mask NIfTI (.nii/.nii.gz)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output mask NIfTI",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        type=int,
        default=[1, 2, 3, 4],
        help="Labels to process (default: 1 2 3 4)",
    )
    return parser.parse_args()


def largest_component(binary: np.ndarray) -> np.ndarray:
    if binary.ndim == 2:
        structure = np.ones((3, 3), dtype=bool)
    else:
        structure = np.ones((3, 3, 3), dtype=bool)

    labeled, num = ndimage.label(binary, structure=structure)
    if num == 0:
        return binary

    counts = np.bincount(labeled.ravel())
    counts[0] = 0
    max_label = counts.argmax()
    return labeled == max_label


def keep_largest_by_label(mask: np.ndarray, labels: Iterable[int]) -> np.ndarray:
    output = np.zeros_like(mask, dtype=mask.dtype)
    for lbl in labels:
        binary = mask == lbl
        if not binary.any():
            continue
        kept = largest_component(binary)
        output[kept] = lbl
    return output


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    img = nib.load(str(input_path))
    data = img.get_fdata()

    # Ensure integer labels
    mask = np.asarray(data, dtype=np.int16)
    cleaned = keep_largest_by_label(mask, args.labels)

    out = nib.Nifti1Image(cleaned.astype(np.int16), img.affine, img.header)
    out.set_data_dtype(np.int16)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_filename(str(output_path))
    print(f"Saved -> {output_path}")


if __name__ == "__main__":
    main()
