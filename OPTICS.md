# Projection geometry and optimization

All distances below are millimetres. These equations are derived for straight rays, an opaque cylinder and a point source. Finite-source estimates are a first-order extension; the display itself uses the point-source footprint.

## 1. Coordinate system and the inverse construction

The room wall is z=0. The cylinder axis is normal to it. Let the source be S=(0,0,h), with h measured **from the room wall**, and let a desired lit wall point be P=(x,y,0), with radial distance rho=sqrt(x²+y²).

The complete ray is

```
Q(t) = S + t(P-S),       0 <= t <= 1.
```

At a cylindrical surface of radius r, t=r/rho. Therefore:

```
Q_r(P) = (r*x/rho, r*y/rho, h*(1-r/rho)).
z_r    = h*(1-r/rho).
```

The outer surface is crossed at z_o=h(1-R/rho), and the inner surface at z_i=h(1-R_i/rho). Since R_i<R, z_i>z_o. **The inner and outer openings must be at different heights.** Simply wrapping the SVG around the cylinder, or making straight radial holes, does not implement the correct projection through a thick shell.

The forward check is:

```
P_xy = h/(h-z) * Q_xy.
rho  = h*r/(h-z).
```

For every filled 2D target point, `linear_extrude()` with a linearly decreasing scale sweeps precisely this ray. The script subtracts that entire perspective cone from the shell. It ends the cone 0.05 mm below the source, with scale 0.05/h, avoiding a degenerate apex while leaving the optical shell intersections unchanged. All valid source clearances keep the shell crossings below that truncated tip.

The approach uses OpenSCAD's [linear extrusion with scale](https://files.openscad.org/documentation/manual/OpenSCAD_User_Manual.pdf) and [SVG geometry import](https://files.openscad.org/documentation/manual/SVG_Import.html). The equations and feasibility policy here are specific to this project.

## 2. Mechanical planes and the hidden centre

Let H be one closed module's depth, J the tongue insertion depth, T the cover plate thickness and p=H-J-T the stacking pitch. For module n:

```
z0 = S + n*p                     module back's distance from wall
A  = z0 + rear_floor + rear_guard lower optical opening limit
B  = z0 + p - front_guard         upper optical opening limit
R_f = R - frame_width            thick front collar's inner radius
```

S is the wall standoff: the clear gap held between the room wall and module 0's back,
by a separate spacer ring or by an extended rear skirt on the body. It enters every plane
above, so optically a standoff is indistinguishable from mounting the same module that
much further into the room.

A ray must cross the outer radius above A. Thus

```
h*(1-R/rho) >= A
rho >= R*h/(h-A),                 with h>A.
```

This is larger than R: the rear plate and uncut structural rim hide more than just the visible body diameter.

The pillar is modelled as a cylinder of radius r_p ending e below the emitting centre. Its upper edge creates another central shadow:

```
rho_pillar = r_p*h/e.
rho_dead   = max(R*h/(h-A), r_p*h/e).
```

Both expressions use **absolute h**, including the stacking offset. They explain why farther modules hide a larger central portion of the wall. The source cannot be put on the wall plane: the forward mapping degenerates at h=0 and the hardware occupies that space.

If h>B, the front collar sets an outer reach:

```
rho <= R_f*h/(h-B).
```

If h<=B, this upper-collar limit is absent because all rays heading toward the wall are below the collar. The sidewall's upper opening gives the same form with R_i; R_f is smaller and therefore more restrictive in this design.

The displayed light is the intended 2D transmitting region intersected with this reachable annulus, minus the radial support wedges. The cylinder itself overlays the central body disk in the display. Mounting holes sit behind that disk; other electronics are not represented as occluders.

## 3. Why x=y=0 for the supported layout

The objective is to maximize the **worst local reproduction scale over a complete concentric 360-degree field**, not to fit a spotlight image displaced to one side. The pillar moves with the source in the hypothetical comparison, and the housing remains concentric.

For a lateral displacement d, look at the two wall directions parallel and opposite to the displacement at the same radius rho. The radial stretch coefficients are proportional to:

```
g_near = (R_i-d)/(rho-d)^2
g_far  = (R_i+d)/(rho+d)^2
g_axis = R_i/rho^2.
```

For both displaced coefficients to exceed g_axis would require both

```
rho*(2*R_i-rho) > R_i*d
rho*(rho-2*R_i) > R_i*d,
```

which is impossible for d>0. At least one radial direction gets worse. The tangential stretch toward the nearer side, (R_i-d)/(rho-d), is also smaller than R_i/rho when rho>R_i. Therefore a displaced source cannot improve the worst of the radial and tangential stretches around the full circle at fixed h. The nearest-side upper-collar clearance also cannot allow a larger h than the concentric source, and the mechanical ceiling is unchanged.

This establishes the on-axis minimax choice for that symmetric field. An asymmetric SVG occupying only a restricted angular sector could benefit from an off-axis source. Such an artwork-specific, unrestricted optimization is **outside this generator's scope**; setting x and y to zero must not be interpreted as having performed it.

## 4. Height optimization

Let rho_max=k*L bound the artwork, where L is its longest dimension. Direct SVG mode uses k=sqrt(2)/2, which bounds a centred square of side L. The helper evaluates k=max(sqrt(x_i²+y_i²)) over the normalized polygon vertices. A convex norm attains its maximum on each straight polygon edge at an endpoint, so this is a valid bound for OpenSCAD's flattened geometry. The demo has k=1/2.

The source must clear the **back of a possible next module**, rather than borrowing cavity space inside the removable cover:

```
h_ceiling = z0 + p - 1.5.
```

To reach rho_max through the front collar:

```
h <= B/(1-R_f/rho_max),           when rho_max>R_f.
```

To leave at least some possible artwork beyond the pillar shadow along the longest dimension:

```
h <= e*(L/2 - minimum_cut - epsilon)/r_p.
```

The selected h is the minimum of those upper bounds. The code subsequently checks the lower hardware and rear-rim clearances. Within these constraints, larger h increases radial aperture size, improves axial-source blur and reduces the rear-rim shadow. The explicit pillar constraint prevents increasing h until its shadow swallows the whole field.

This maximizes the local resolution estimate for the supported field. It is not an optimization of total luminous flux, subjective image quality, occluded image area or manufacturing cost. If the SVG has no filled region in the reachable annulus, the envelope test alone cannot detect that; the helper's geometry/mesh inspection and the preview remain necessary.

## 5. How detail compresses onto the shell

Parameterize the inner shell by arc length s=R_i*theta and height z=h(1-R_i/rho). A tangential wall displacement rho*dtheta becomes R_i*dtheta, and a radial displacement d(rho) becomes (h*R_i/rho²)*d(rho). The local scale factors are:

```
sigma_t = R_i/rho
sigma_r = h*R_i/rho^2
sigma_min = min(sigma_t, sigma_r).
```

For a declared important wall detail f=alpha*L, use the conservative outer-radius estimate:

```
w_estimate = f * min(R_i/rho_max, h*R_i/rho_max^2).
```

The radial direction is often much worse than the tangential one. At constant fractional detail alpha and envelope k, radial cut size varies approximately as h/L. Merely making the requested wall image bigger does not make it easier to print.

For h=24, R_i=48, rho_max=150 and f=15, the estimate is 0.768 mm. For the direct square bound of a 1,000 mm image, rho_max=707.107 and f=50, it is about 0.115 mm: below a selected 0.4 mm cut limit.

### 5a. What a standoff buys, and what it costs

Raising the module by S raises the admissible source height by very nearly S: the collar
constraint h = B/(1-R_f/rho_max) is linear in B, and B grows with S. sigma_r = h*R_i/rho_max^2
is linear in h, so radial resolution improves in direct proportion.

The hidden centre moves the other way. In rho_dead = R*h/(h-A) both h and A grow by S, so the
numerator grows while the denominator barely moves and the occluded disc widens roughly
linearly in S. Measured on the default 100 x 30 mm module at L=300:

| Standoff S | Source h | Cut estimate | Hidden radius |
|---:|---:|---:|---:|
| 0 mm | 24 mm | 0.768 mm | 64.9 mm |
| 20 mm | 44 mm | 1.408 mm | 118.9 mm |
| 50 mm | 74 mm | 2.368 mm | 200.0 mm |

A standoff therefore does not simply make images bigger: it trades a wider dead centre for
sharper detail, a net gain only if the image grows with it. At S=50 the feasibility test
L/2 > rho_dead + w_min fails outright for L=300, while L=600 passes with a 1.184 mm cut
estimate -- a length the flush module cannot reach at all.

This is a **local first-order feature estimate**, not an exact minimum-thickness computation on every curve, ligament or oblique channel. Sharp tips naturally approach zero width. What counts as an important feature must be specified by the designer. The helper detects disconnected components but does not certify every ligament's width or printer capability.

### 5c. A bounded lit field

A dark silhouette normally subtracts the artwork from a disc of radius k*L + border. The
light limit replaces that disc with a bounded region D, so the lit field is D minus the
artwork. Three choices of D:

```
Same as shadow:  D = artwork (+) disk(T)        rho_max = k*L + T
Circle:          D = disk(k*L + T)              rho_max = k*L + T
Rectangle:       D = box(w*L/2 + T, h*L/2 + T)  rho_max = hypot(w*L/2 + T, h*L/2 + T)
```

where (+) is Minkowski addition, w and h are the artwork's extents as fractions of its
longest side, and T is the band width on the wall. The rectangle reaches furthest at its
corner, which is what rho_max must use; taking its half-width instead understates the
envelope by up to sqrt(2) and lets an infeasible request pass.

The band width is the one wall feature whose size is known rather than declared, so its
slot in the shell follows directly from section 5:

```
w_band = T * min(R_i/rho_max, h*R_i/rho_max^2).
```

Since rho_max itself contains T, the thinnest band that still opens a w_min slot has no
closed form; the generator settles it by repeated substitution. At h=24, R_i=48, k=0.5 and
L=300 the fixed point is T = 8.8 mm for w_min = 0.4 mm. A standoff raises h and so lowers
that floor: 4.5 mm at S=20.

### 5d. Bounding one side of a closed outline

Minkowski addition moves every boundary of A outwards, which for a hole means inwards. On a
closed outline the enclosed interior is a hole, so `A (+) disk(T)` shrinks it by T and the
interior goes dark. Bounding the outside without touching the inside needs the silhouette

```
F = fill(A),   A's outermost contours with every hole filled,
```

and then the field splits at F:

```
outside = (disk(beam) - F)  intersect  (bounded ? D : everything)
inside  = F                 intersect  (bounded ? A (+) disk(T) : everything)
D_total = outside union inside,     lit = D_total - A.
```

All four on/off combinations fall out of this, and both switches off reproduce the plain
dark silhouette exactly. fill(A) is not obtainable from A by morphology -- a closing fills
holes only up to its own radius and rounds everything else on the way -- so it comes from
contour topology instead: flatten the SVG, count how many contours of the same path contain
each contour, and keep those at even-odd depth zero. That is a property of the path data, not
of the rendered region, so it is available to the preparation helper and not to `import()`.

When the silhouette cannot be measured -- a direct `import()`, and so every MakerWorld
upload -- fill(A) is approximated by a morphological closing with a mitred structuring
element of half-width S:

```
fill(A) ~= erode(dilate(A, S), S).
```

Dilation followed by erosion returns a convex boundary to where it started and closes any
enclosed area or concave pocket narrower than 2S, so the error is confined to outer pockets
narrower than the span. Measured against the exact silhouette of the Monza outline at
L=300 mm, where the true fill is 19,304 mm^2:

| S | closing | missing | extra | error |
|---:|---:|---:|---:|---:|
| 40 mm | 7,800 | 11,573 | 69 | 60.3% |
| 60 mm | 19,420 | 2 | 117 | 0.62% |
| 120 mm | 19,509 | 3 | 208 | 1.10% |
| 200 mm | 19,308 | 141 | 144 | 1.48% |
| 450 mm | 21,882 | 8 | 2,586 | 13.4% |

The usable window is broad: anything from just over half the enclosed width up to roughly the
artwork's own length agrees with the exact silhouette to within about 1.5%. Below that it
under-fills sharply, and far above it the result drifts toward the convex hull, which for this
outline is 28,628 mm^2. Rounded joins were rejected: `offset(r=)` pulls the outer boundary in
during erosion, whereas mitred joins restore it exactly.

The construction says nothing about connectivity. D minus artwork is an annular region
whenever the artwork lies inside D, so every enclosed shape is a separate component of the
opaque stencil. That is already true of the unbounded disc and is not made worse here, but
it is structural rather than incidental: no choice of T avoids it.

## 6. Finite LED size and blur

At a fixed aperture point (Q_xy,z), the wall point from a source with transverse location S_xy is

```
P_xy = S_xy + h/(h-z)*(Q_xy-S_xy).
M = h/(h-z) = rho/R_i.
```

Differentiate with respect to the source position while holding the aperture fixed:

```
|dP/dS_xy| = M-1
|dP/dh|   = (M-1)*rho/h.
```

For effective transverse source diameter d_xy and axial extent d_z, the sum

```
b_estimate = (rho_max/R_i - 1) * (d_xy + d_z*rho_max/h)
```

is a conservative first-order extent estimate. Axial thickness is especially costly at grazing angles. With a planar source, transverse blur is independent of h at fixed cylinder and image radii: a taller cylinder alone cannot fix an overly wide source. Lens optics, angular emission, vignetting, scattering and diffraction are not simulated. A finite source also shifts the effective aperture visibility, so this scalar estimate is not a rendered penumbra.

For illustration, an isotropic point source of radiant intensity I produces wall irradiance

```
E(rho) = I*h/(rho^2+h^2)^(3/2).
```

The extra cosine factor from the grazing wall angle means far-wall brightness falls approximately as rho^-3 in this shallow geometry. A wall-facing Lambertian emitter adds another cosine factor. Without the LED's angular intensity distribution and power, the script cannot infer usable brightness or exposure.

## 7. Feasibility and closest alternatives

The solver requires valid mechanical dimensions, a valid source position, some potential field outside the central obstruction, the local cut estimate above the chosen threshold, and estimated blur below the chosen maximum. It does not invent a universal maximum image size from cylinder height alone.

On failure in automatic mode, it searches H upward in 1 mm steps to min(300,max(160,3*H_requested)). At each height it finds the largest qualifying L no greater than the requested length, using a binary search on the monotone quality limits, followed by the mechanical/visible-field checks. It rounds L downward to 0.1 mm. Candidate pairs minimize

```
cost = ((H-H_requested)/H_requested)^2
     + ((L-L_requested)/L_requested)^2.
```

Equal relative changes have equal weight. The script additionally reports holding the requested H fixed or holding L fixed. If no candidate exists, it states that the selected search range/assumptions have no solution and suggests changing diameter, required detail or source extent. It does not label that as a proof of physical impossibility under all possible designs.

## 8. Structural and optical compromises

Closed luminous outlines can leave opaque material floating inside an opening. Fixed spokes cannot retain every arbitrary island. The helper exports the real body and identifies disconnected surface components. It now places vertical ribs under the lowest face of each substantial floating component, stopping inside the island. With surface cleanup enabled, detached specks below `Minimum_web_width^3` cubic millimetres are removed through their projected convex footprints and recorded explicitly in the JSON. It rerenders and checks again, up to eight attempts. Unresolved failures are reported.

Connectivity does not establish ligament strength or physical printability. Bridges necessarily alter the original light pattern. A fully exact SVG containing floating opaque islands needs another support architecture, such as a separate transparent mask substrate, and cannot be promised by a single-material carved shell.

Stacking adds an absolute offset to every ray calculation. Equal-diameter lower modules are behind the current module's rear plate and within its central occlusion envelope. Larger lower modules, external brackets, exposed electronics and light leakage through open cable/screw holes require additional occlusion modelling. Generate each equal-diameter module for its own index and use independent, properly shielded sources.

## 9. Rectangular housing and bounded design study

The cone remains `P(t) = (t*x, t*y, h*(1-t))`; only the housing intersection
changes. For a face at X=a, a wall point (x,y) maps to `(a, a*y/x, h*(1-a/x))`.
The inverse is the same perspective projection as for the cylinder. Flat faces
introduce shear, so using only radial and tangential cylindrical scales would
overstate the rectangular worst-direction resolution.

For the face map `(x,y) -> (a*y/x, h*(1-a/x))`,
`|det J| / ||J||F = a*h/(|x|*sqrt(x*x+y*y+h*h))` is a lower bound on the least
singular value. The implementation conservatively substitutes the minimum inner
face distance for a and the maximum artwork radius for |x| and hypot(x,y).
The upper-collar/source bound and blur estimate use the minimum inner radius.
These are conservative envelope bounds, not an artwork-specific flat-face optimum.

The lower aperture obstruction is the **actual outer footprint**, scaled by
`h/(h-bottom_absolute)`, combined with the circular pillar obstruction. The
upper clipping footprint uses the inset front collar. The reported rectangular
dead radius is a corner envelope; the preview does not black out that full circle.
Joints and cover use the same rectangular inset profiles as the body.

The standoff enters `off(H) = standoff + module_index*pitch` and the cone origin,
source, lower and upper aperture planes, body placement and projection. Its
integration was already correct. The stack display now also offsets lower
module envelopes by the standoff.

For a fixed total depth, transferring depth from standoff to optical body lowers
the absolute rear aperture while keeping the ceiling nearly fixed. It can shrink
the hidden centre markedly. Thus optimizing body height alone encourages an
unhelpfully tall standoff. `compare_designs.py` counts **body height + standoff**
and measures filled-SVG area outside the actual footprint. It samples a declared
finite grid and ranks an explicit compactness/visibility score. Neither the
score nor the 85% area threshold proves an artistic or global optimum.

## 10. Developed-surface preparation and verification

`--minimum-web` samples light on the developed inner shell at approximately
0.06 mm pitch, wraps around the seam, and closes narrow opaque slivers there.
Rectangle faces unroll with their physical perimeter lengths. Only correction
regions, with one cell of overlap, are mapped back to wall coordinates. The
original vector light is retained. A small 0.01 mm wall-space closing removes
numerical tangencies before oblique extrusion. These operations simplify dark
detail instead of shrinking every bright contour by a worst-case global offset.

Finite ribs extend from the rear collar to their stored local Z. Their maximum
wall extent is the outer footprint scaled by `h/(h-off-z_top)` (including the
small Boolean overlap). This keeps the preview consistent with their truncated
height rather than displaying full-length spokes.

Opening the sampled light mask with a 0.4 mm kernel provides a **small-feature
screen**, reported as a fraction of inner-shell light area. Corners contribute to
that fraction; it is not an exact stroke-width measurement, lost-wall area or a
slicer prediction. The user confirmed a 0.4 mm nozzle. A 0.9 mm rib is a useful
starting point for two roughly 0.45 mm extrusion lines, consistent with
[Prusa's line-width guidance](https://help.prusa3d.com/article/layers-and-perimeters_1748).
Actual line width, layer height, material, overhangs and the LED still need testing.

The surface filter cannot certify minimum neck thickness, self-supporting layers
or mechanical strength. Connectivity is checked on the final mesh. Export-only
coincident vertices are welded at 0.000001 mm, with collapsed triangles removed;
the mesh is then required to have exactly two incident triangles per edge and
one connected surface. This tiny numerical cleanup is separate from deliberate
removal of small stencil specks.

`inspect_projection.py` translates STL vertices by the actual body wall offset
before projecting opaque triangles. It supports both housings, stacked modules
and both standoff modes. It reports original-area retention, added light,
support/clipping loss, and STL/analytic intersection-over-union separately.
Narrow outlines are sensitive to raster edge coverage; inspect the images and
record resolution alongside the numerical agreement.
