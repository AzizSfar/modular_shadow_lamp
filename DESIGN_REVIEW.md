# Reference design review — 2026-09-13

The best direction within the tested carved-shell designs is **a cylinder with a
modest standoff and a larger share of its depth assigned to the optical body**.
Making the optical section very shallow and compensating with a tall electronics
chamber hides too much of the image. A rectangle is now available for comparison,
but it did not improve Monza's visibility at the same outer width and total depth.

## Prepared comparison prototypes

| Reference | Housing XY | Optical body + standoff | Artwork length | Original filled area retained | STL / preview agreement |
|---|---|---|---|---|---|
| Itachi | Ø80 mm | 44 + 10 = **54 mm** | **800 mm** | **88.39%** | **99.02%** at 5,000 px |
| Monza | Ø80 mm | 36 + 10 = **46 mm** | **600 mm** | **97.25%** | **97.84%** at 10,000 px |
| Monza rectangle | 80 × 80 mm | 36 + 10 = **46 mm** | **600 mm** | **94.69%** | **97.95%** at 10,000 px |

The respective files are `output/itachi_final.scad`, `output/monza_final.scad`
and `output/monza_rectangle_final.scad`. Each has a body STL, cover STL, standoff
STL and JSON report. Each final part has one connected surface and two triangles
incident on every mesh edge. The rectangular body, cover and standoff joints were
also checked for positive-volume interference using a non-square 60 × 90 mm case.

These are candidates from a bounded study, not globally optimal dimensions or
print-certified parts. The electronics have not been measured to fit the 10 mm
compartment. The user confirmed a **0.4 mm nozzle**; the **0.2 mm emitting area**
is still only the original project's optical assumption. A larger emitter can
invalidate the sharpness estimates.

The candidates use the original **5% declared-detail** requirement: 40 mm at an
800 mm image, or 30 mm at 600 mm. That does **not** certify the SVG's smaller
features. Repeating the bounded study at 2% finds no Itachi candidate retaining
85% of the artwork, and only a few substantially deeper Monza candidates. The
fine detail requirement is therefore a real design constraint, not a checkbox
that the optimizer can infer from the filename.

## What changed

1. **Standoff and size comparison.** The standoff was already present in the
   inverse rays, source height and wall clipping. The new study varies standoff,
   optical height, XY size, image length and image placement, counts total depth,
   and measures actual filled-SVG visibility. It samples 4,320 combinations for
   each reference. The stack display's lower envelopes now include the standoff.
2. **Rectangular option.** Body, removable cover, mating joints, standoff and
   projection all use the selected footprint. Width and depth can differ. Flat
   faces use a conservative shear-aware compression estimate.
3. **Fragile opaque slivers.** Optional preparation works in physical developed
   shell coordinates, rather than expanding every wall-space stroke by the
   worst-case magnification. It selectively removes tiny dark strips. This is
   a controlled simplification; it does not preserve every dark detail exactly.
4. **Floating islands.** Automatic-only mode removes the blanket twelve spokes.
   Sub-print-size detached specks are removed and reported; larger pieces get
   short 0.9 mm vertical ribs beneath them. Itachi needed eight ribs and removal
   of four tiny specks. Both final Monza versions needed no additional ribs.
5. **Verification.** The helper checks final mesh closure/connectivity, fixes
   collapsed STL export triangles at 0.000001 mm precision, and records a source
   fingerprint. A prepared surface stencil refuses a body export after relevant
   geometry edits until regenerated. Independent STL projection is compared
   with the preview, including the standoff and truncated supports.

## Shadow changes and remaining print questions

The 30 mm body + 30 mm standoff Itachi trial at 600 mm hid about 49% of the original
filled artwork before supports. The 44 + 10 mm candidate at 800 mm hides about
10% before supports, while being 6 mm shallower overall. This is why minimizing
only the optical body height is misleading.

On the final Itachi candidate, cleanup introduces additional light equivalent
to **8.13%** of the otherwise visible light area and supports/cleanup remove
**1.68%**. Its visible-pattern intersection-over-union against the unmodified,
housing-clipped artwork is **90.93%**. The remaining central hole is inherent to
the opaque housing and pillar; it has not been fixed by modifying the SVG.

For Monza, added light is **3.91%** for the cylinder and **2.33%** for the rectangle;
visible-pattern agreement is **96.20%** and **97.71%**, respectively. The rectangle
changes less detail in this test but hides more of the track. At half the raster
resolution, STL agreement was about 96%; the increase to about 98% at 10,000 px
shows the sensitivity of these narrow outlines to raster boundary coverage.

The 0.4 mm small-aperture screen flags **0.98%** of Itachi's sampled inner-shell
light area, **12.60%** of Monza's and **13.36%** of rectangular Monza's. This includes
corners and is not a prediction that those exact percentages disappear in print.
It does mean that Monza's finest openings need close slicer inspection. The
filter does not certify minimum neck thickness, overhangs, layer-by-layer support,
strength, brightness, heat or physical joint fit.

For a 0.4 mm nozzle, the 0.9 mm ribs are a reasonable two-extrusion starting point
when line width is about 0.45 mm; use the actual slicer setting. See
[Prusa's perimeter guidance](https://help.prusa3d.com/article/layers-and-perimeters_1748).
Exact reproduction of arbitrary fine SVG detail with no opaque supports may
require a different mask construction, such as an opaque pattern carried by a
transparent substrate. That would still need optical and material testing.

## Files to inspect

- `output/reference_comparison.png`: compact overview of the three predicted patterns.
- `output/itachi_final_projection/comparison.png`: original, housing-only clipping,
  modified footprint and independent STL projection.
- `output/monza_final_projection/comparison.png`: the same comparison for Monza.
- `output/monza_rectangle_final_projection/comparison.png`: rectangular comparison.
- `output/reference_study_5percent/`: candidate CSVs and selected dimensions under
  the original declared-detail assumption.
- `output/reference_study/`: the stricter 2% study.
- `README.md`: commands for regeneration and the new controls.

Validation: **29 distinct automated tests passed**, including the existing
standoff/source cases, rectangular part closure and dimensions, rectangular joint
interference, flat-face inverse mapping, contour topology and STL roundoff cleanup.
All nine final exported parts passed mesh checks. No physical print or lighting
test has been performed.
