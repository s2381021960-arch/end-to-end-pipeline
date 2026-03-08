import sys
from pathlib import Path

import nibabel as nib
import numpy as np


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: python make_3d.py <input_nii> <repeats> [output_nii]")

    src = Path(sys.argv[1]).resolve()
    repeats = int(sys.argv[2])
    dst = Path(sys.argv[3]) if len(sys.argv) > 3 else src.with_name(src.stem + "_3d.nii.gz")

    img = nib.load(src.as_posix())
    data = img.get_fdata()

    if data.ndim == 2:
        data = data[..., np.newaxis]
    elif data.shape[-1] != 1:
        sys.exit("Input already has >1 slice; no need to copy.")

    vol = np.repeat(data, repeats=repeats, axis=2)
    nib.save(nib.Nifti1Image(vol, img.affine, img.header), dst.as_posix())
    print(f"Saved to {dst}")


if __name__ == "__main__":
    main()
