# Release Notes

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and uses the Zettelkasten ID (ZID) tagging convention for robust traceability across commits, conversation logs, and release documentation.

---

## [v1.0.2] - 2026-05-17
**ZID Anchor:** `20260517193351`  
**Git Tag Range:** `v1.0.0..20260517193230`

### Summary
This release focuses on optimizing the media conversion output quality and providing verbose installation diagnostics. Specifically, we've updated the script to prevent background canvas color shifting during conversion (e.g. WAV to MP4) by tuning FFmpeg settings for static content. This guarantees consistent black backgrounds, reduces overall video track file sizes to the absolute minimum, and allows downstream compressed archives (ZIP files) to compress much more efficiently. Additionally, shortcut installation feedback is now fully informative.

### Detailed Changes

#### 1. Video Compression & Background Color Stabilization
- **ZID Link:** `20260517184558`
- **Issue:** Background black canvas occasionally suffered color shifting and compression artifacts over the course of longer WAV conversions, resulting in unnecessary frame updates and larger file sizes.
- **Optimization Solution:**
  - Integrated `DEFAULT_VIDEO_CRF = '36'` to leverage Constant Rate Factor encoding, ensuring highly optimized compression suitable for static canvases.
  - Enabled `-tune stillimage` to maximize inter-frame duplicate detection and suppress unneeded visual changes.
  - Implemented `-x264-params keyint=300:min-keyint=300:scenecut=0` to enforce long, stable keyframe intervals without unwanted scenecuts, maintaining a consistent solid color and allowing for maximum compression ratio under ZIP/7z.
- **Result:** Video files are exceptionally lightweight, with extremely clean background preservation and massive archive space savings.

#### 2. Verbose SendTo Installation Diagnostics
- **ZID Link:** `20260517184151`
- **Improvement:** Shortcut creation via `--install-sendto` now provides complete visibility to the user instead of silent operations.
- **Diagnostics Details:**
  - Displays fully expanded absolute paths of the target script, resolved `pythonw.exe` executable, target Windows SendTo directory, and the generated `.lnk` shortcut path.
  - Details selected options such as `--output-mode`, `--duplicate-mode`, and `--converted-subdir-name` passed during setup.
  - Displays explicit user guidance on Explorer usage and outputs a distinct `SUCCESS` indicator upon successful shortcut deployment.

---

## [v1.0.0] - 2026-05-17
**ZID Anchor:** `20260517182831`  
**Git Tag:** `20260517183128`

### Summary
Initial official release of the **Convert Media Utility**, bringing SendTo explorer integration, custom configurable output folders, and ZID-based duplicate handling.

### Key Features
- **SendTo Shortcut Integration:** Seamless right-click selection of multiple files to convert.
- **Custom Output Control:** Flexible configuration of output locations via `--output-mode same-dir|converted-subdir`.
- **Traceable Duplicate Management:** ZID-based duplicate routing to prevent data loss while keeping file histories clear.
- **Legacy Compatibility:** Seamless command line support for traditional workflows.
