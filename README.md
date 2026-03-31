# end-to-end-pipeline
This project is based on the open-source projects Spinenet and LPM_segmentator, so you need to first configure and download the virtual environments and resources required for these two projects.
1. **SpineNet**
   - Upstream: https://github.com/rwindsor1/SpineNet
   - Version used in this project: commit `5e96ac54b1c1845a37d12e40bfd16f647d40acd8`
   - License: `LICENCE.md` from SpineNet (research/non-commercial license by University of Oxford VGG)
   - Local adaptations in our pipeline include:
     - added integration scripts: `auto.py`, `map_axial_slices.py`, `run_sagittal_pipeline.py`

2. **LPM_Segmentator**
   - Upstream: https://github.com/johnnydfci/LPM_Segmentator
   - Version used in this project: commit `4937fa4d7dbf56e78aa547e29151511683d1469e`
   - License: Apache License 2.0
   - Local adaptations in our pipeline include:
     - added scripts/tools: `split_nifti_slices.py`, `run_predict_singleproc.py`, `largest_component.py`, `make_3d.py`, `otsu/*`

3. **Perforemence**
[overlay_240195146_L3-L4.tiff](https://github.com/user-attachments/files/26364275/overlay_240195146_L3-L4.tiff)
[overlay_240195146_L4-L5.tiff](https://github.com/user-attachments/files/26364279/overlay_240195146_L4-L5.tiff)
[overlay_240195146_L5-S1.tiff](https://github.com/user-attachments/files/26364281/overlay_240195146_L5-S1.tiff)
