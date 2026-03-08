# end-to-end-pipeline
# 1. SpineNet：定位轴位切片
(spinenet-venv)
cd /d E:\segment1\SpineNet
E:\segment1\SpineNet\spinenet-venv\Scripts\activate
set PYTHONPATH=%PYTHONPATH%;E:\segment1\SpineNet
python run_sagittal_pipeline.py ^
  --input-folder "H:\MR\%CASE%\sagittal" ^
  --output-dir   "E:\segment1\total-result\%CASE%"

set CASE=

python map_axial_slices.py ^
  --vertebrae-csv "E:\segment1\total-result\%CASE%\vertebrae.csv" ^
  --sagittal-dicom-dir "H:\MR\%CASE%\sagittal" ^
  --axial-dicom-dir    "H:\MR\%CASE%\axial" ^
  --axial-series 401 ^
  --export-dir  "E:\segment1\total-result\%CASE%\axial_slices" ^
  --output-csv  "E:\segment1\total-result\%CASE%\axial_targets.csv"


python auto.py

powershell -ExecutionPolicy Bypass -File "G:\imagemri\otsu\batch_prepare_nifti.ps1"


cd g:\imagemri\otsu
# 如需调整路径，直接编辑脚本顶部 param 中的默认值
.\batch_prepare_nifti.ps1

3.cd /d G:\imagemri\muscle\LPM_Segmentator

G:\imagemri\Miniconda3\condabin\conda.bat activate lpm

set nnUNet_raw_data_base=G:\imagemri\muscle\LPM_Segmentator\nnUNet_raw_data_base
set nnUNet_results=G:\imagemri\muscle\LPM_Segmentator\nnUNet_trained_models
set nnUNet_preprocessed=G:\imagemri\muscle\LPM_Segmentator\nnUNet_preprocessed

# 将 case%CASE%_0000.nii.gz 放到 test_img_in_nii_raw（批量复制可手动或用脚本）
copy /Y "E:\segment1\total-result\%CASE%\nifti\case%CASE%_0000.nii.gz" ^
        "G:\imagemri\muscle\LPM_Segmentator\nnUNet_raw_data_base\nnUNet_test_data\test_img_in_nii_raw\case%CASE%_0000.nii.gz"
        
python split_nifti_slices.py

# 推理（如 GPU 显存不够，可先 set CUDA_VISIBLE_DEVICES= 走 CPU）
python run_predict_singleproc.py

# 批量 largest component（CMD）：
cmd /v:on
set MASKDIR=G:\imagemri\muscle\LPM_Segmentator\nnUNet_raw_data_base\nnUNet_test_data\test_seg_in_nii_raw
set OUTDIR=G:\imagemri\muscle\LPM_Segmentator\nnUNet_raw_data_base\nnUNet_test_data\test_seg_in_nii
for %f in ("%MASKDIR%\*.nii*") do (
  set "BASE=%~nf"
  set "BASE=!BASE:.nii=!"
  python G:\imagemri\muscle\LPM_Segmentator\largest_component.py --input "%~f" --output "%OUTDIR%\!BASE!_largest_curated.nii.gz"
)
