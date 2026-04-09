#!/usr/bin/env python3
"""Run nnUNet prediction in a single process on Windows."""

from nnunet.inference.predict import predict_from_folder

MODEL_DIR = r"G:\imagemri\muscle\LPM_Segmentator\nnUNet_trained_models\nnUNet\3d_fullres\Task515_muscle\nnUNetTrainerV2_noMirroring__nnUNetPlansv2.1"
INPUT_DIR = r"G:\imagemri\muscle\LPM_Segmentator\nnUNet_raw_data_base\nnUNet_test_data\test_img_in_nii"
OUTPUT_DIR = r"G:\imagemri\muscle\LPM_Segmentator\nnUNet_raw_data_base\nnUNet_test_data\test_seg_in_nii_raw"

def main() -> None:
    predict_from_folder(
        model=MODEL_DIR,
        input_folder=INPUT_DIR,
        output_folder=OUTPUT_DIR,
        folds=(1,),  # change to (0,) if you want fold 0
        save_npz=False,
        num_threads_preprocessing=1,
        num_threads_nifti_save=1,
        lowres_segmentations=None,
        part_id=0,
        num_parts=1,
        tta=False,
        mixed_precision=True,
        overwrite_existing=True,
        mode='normal',
        overwrite_all_in_gpu=False,
        step_size=0.5,
        checkpoint_name="model_final_checkpoint",
        segmentation_export_kwargs=None,
        disable_postprocessing=False,
    )


if __name__ == "__main__":
    main()
