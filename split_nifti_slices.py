#!/usr/bin/env python3
"""Split or expand NIfTI volumes for nnU-Net inference."""

import argparse
from pathlib import Path
from typing import List, Optional

import nibabel as nib
import numpy as np

DEFAULT_INPUT = (
    r"G:\imagemri\muscle\LPM_Segmentator\nnUNet_raw_data_base\nnUNet_test_data"
    r"\test_img_in_nii_raw"
)
DEFAULT_OUTPUT = (
    r"G:\imagemri\muscle\LPM_Segmentator\nnUNet_raw_data_base\nnUNet_test_data"
    r"\test_img_in_nii"
)
DEFAULT_NAMES = ["case001", "case002", "case003"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split or expand NIfTI files for nnU-Net inference.",
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help="Input NIfTI file or a directory containing *_0000.nii.gz (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT,
        help="Directory to write the output files (default: %(default)s)",
    )
    parser.add_argument(
        "--names",
        nargs="+",
        default=None,
        help=(
            "List of base filenames (without _0000.nii.gz) for multi-slice input files. "
            f"Length must match number of slices (default: {DEFAULT_NAMES})"
        ),
    )
    return parser.parse_args()


def iter_input_files(input_path: Path) -> List[Path]:
    if input_path.is_dir():
        files = sorted(input_path.glob("*_0000.nii.gz"))
        files += sorted(input_path.glob("*_0000.nii"))
        if not files:
            raise FileNotFoundError(
                f"No *_0000.nii.gz or *_0000.nii found in {input_path}"
            )
        return files
    if input_path.is_file():
        return [input_path]
    raise FileNotFoundError(f"Input path not found: {input_path}")


def write_volume(volume: np.ndarray, affine, header, output_path: Path) -> None:
    img = nib.Nifti1Image(volume.astype(np.float32), affine, header)
    img.set_data_dtype(np.float32)
    img.to_filename(output_path)
    print(f"Saved -> {output_path}")


def save_slices(input_path: Path, output_dir: Path, names: Optional[List[str]]) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    input_files = iter_input_files(input_path)
    for src in input_files:
        img = nib.load(str(src))
        data = img.get_fdata()
        affine = img.affine
        header = img.header.copy()

        if src.is_file() and src == input_path and data.ndim == 3 and data.shape[-1] > 1:
            slice_count = data.shape[-1]
            slice_names = names or DEFAULT_NAMES
            if slice_count != len(slice_names):
                raise ValueError(
                    f"Number of names ({len(slice_names)}) must match number of slices ({slice_count})."
                )
            for idx, name in enumerate(slice_names):
                single = data[:, :, idx]
                slice_data = np.repeat(single[:, :, None], 16, axis=2)
                out_path = output_dir / f"{name}_0000.nii.gz"
                write_volume(slice_data, affine, header, out_path)
            continue

        if data.ndim == 2:
            single = data
        elif data.ndim == 3 and data.shape[-1] == 1:
            single = data[:, :, 0]
        else:
            out_path = output_dir / src.name
            write_volume(data, affine, header, out_path)
            continue

        slice_data = np.repeat(single[:, :, None], 16, axis=2)
        out_path = output_dir / src.name
        write_volume(slice_data, affine, header, out_path)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    save_slices(input_path, output_dir, args.names)


if __name__ == "__main__":
    main()
