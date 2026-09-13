// Modular shadow lamp — millimetres. Read README.md and OPTICS.md.
// Self-contained OpenSCAD 2021.01 / MakerWorld Parametric Model Maker.
// The wall is XY at z=0; +z points into the room. Filled SVG areas transmit light.

/* [View] */
Output = "Assembly"; // [Assembly,Projection,Body,Cover,Cover base,Cover artwork,Standoff,Print layout,Stack preview,Diagnostics]
Show_rays = false;
Show_report = true;
Cover_preview = "Exploded"; // [Exploded,Fitted,Hidden]
// Wall coordinates in mm: cylinder centre = (0,0), X right, Y up.
Show_grid = false;
Grid_spacing = 25; // [5:5:100]

/* [Artwork] */
// Automatic uses a changed file path first, then embedded artwork, then the demo.
// Choose SVG file explicitly if MakerWorld keeps the uploaded filename default.svg.
Artwork_source = "Automatic"; // [Automatic,SVG file,Built-in demo,Embedded artwork]
// MakerWorld recognizes this variable as an SVG upload control.
Svg_file = "default.svg";
// Select the LONGER artwork axis. The other axis scales proportionally.
Svg_long_axis = "Y"; // [X,Y]
// Longest dimension of the complete artwork BEFORE central occlusion, in mm.
Shadow_length = 300; // [100:5:1500]
// Light shapes matches luminous outlines in the reference photo.
Artwork_mode = "Light shapes"; // [Light shapes,Dark silhouette]
// Small lit border around the dark silhouette field; avoids tangential, invalid cuts.
Dark_field_border = 3; // [0.5:0.5:20]
Artwork_rotation = 0; // [-180:1:180]
Shadow_x = 0; // [-1000:1:1000]
Shadow_y = 0; // [-1000:1:1000]
// Smallest IMPORTANT line or gap, as % of the artwork's longest dimension.
// This is a declared design requirement, NOT an automatic SVG measurement.
Smallest_detail_percent = 5; // [0.1:0.1:20]

/* [Cylinder] */
Housing_shape = "Cylinder"; // [Cylinder,Rectangle]
Rectangle_width = 80; // [40:1:250]
Rectangle_depth = 100; // [40:1:250]
Cylinder_diameter = 100; // [60:1:250]
// Total closed depth of one module, including its fitted cover.
Cylinder_height = 30; // [18:0.5:200]
Wall_thickness = 2; // [1.2:0.1:4]
// 0 = first module at wall; 1 = second module, etc. Recompute each module.
Module_index = 0; // [0:1:8]

/* [LED and optical quality] */
LED_position = "Automatic"; // [Automatic,Manual height]
// Height of the EMITTING CENTRE above this module's back, not package bottom.
Manual_LED_height = 24; // [0:0.1:200]
// Width of the actual emitting area, not the plastic lens or LED package.
Emitter_diameter = 0.2; // [0:0.01:5]
// Axial thickness of the emitting area. 0 assumes a planar emitter parallel to wall.
Emitter_axial_depth = 0; // [0:0.01:2]
Maximum_blur = 2; // [0.1:0.1:20]
Minimum_cut_width = 0.4; // [0.15:0.05:2]
// Emitting centre above the end of the printed pillar; measure your LED assembly.
Emitter_above_pillar = 3; // [1:0.1:10]
Pillar_diameter = 8; // [4:0.5:20]
// Continuous empty passage through the rear floor and the whole pillar, in mm.
Pillar_wire_bore = 3; // [1:0.1:6]

/* [Stencil supports] */
// Spokes interrupt light but can connect otherwise floating opaque islands.
// They do NOT guarantee connectivity for arbitrary artwork; run prepare_svg.py.
Support_bridges = true;
Support_layout = "Radial"; // [Radial,Manual XY,Radial and XY]
Bridge_count = 12; // [3:1:48]
Bridge_width = 0.8; // [0.4:0.1:2]
Bridge_rotation = 15; // [0:1:180]
// Helper mode disables the regular spokes and retains only mesh-detected repairs.
Automatic_bridges_only = false;
// Simplify narrow opaque strips in wall space using a conservative shell scale.
// 0 preserves the original geometry. This changes the shadow; inspect Projection.
Minimum_web_width = 0; // [0:0.1:2]

/* [Manual XY supports] */
// Segments are specified on the WALL grid. Width is the dark strip width on the wall.
// Enable Manual XY or Radial and XY in Support_layout to use these segments.
Support_1_enabled = true;
Support_1_start = [0,0];
Support_1_end = [0,200];
Support_1_width = 8; // [0.5:0.5:50]
Support_2_enabled = false;
Support_2_start = [0,0];
Support_2_end = [200,0];
Support_2_width = 8; // [0.5:0.5:50]
Support_3_enabled = false;
Support_3_start = [0,0];
Support_3_end = [0,-200];
Support_3_width = 8; // [0.5:0.5:50]
Support_4_enabled = false;
Support_4_start = [0,0];
Support_4_end = [-200,0];
Support_4_width = 8; // [0.5:0.5:50]

/* [Cover artwork and wiring] */
// White FLUSH inlay on the outward-facing circular cover; independent of shadow SVG.
Cover_artwork_source = "Automatic"; // [Automatic,None,SVG file,Embedded artwork]
Cover_svg_file = "default.svg";
Cover_svg_long_axis = "Y"; // [X,Y]
Cover_artwork_length = 65; // [5:1:240]
Cover_artwork_rotation = 0; // [-180:1:180]
Cover_artwork_depth = 0.6; // [0.2:0.1:1.2]
// Centre hole through both cover and inlay. Zero means a closed cover.
Cover_hole_diameter = 0; // [0:0.1:20]

/* [Mounting] */
// Clear gap held between the room wall and this module's back. 0 = flush to the wall.
// The gap is a closed compartment for the electronics. A standoff lifts the source,
// so the reachable image grows -- but the hidden centre widens at a similar rate.
Wall_standoff = 0; // [0:0.5:200]
// Separate ring prints the gap as its own part that plugs into the rear socket.
// Extended body grows the body backwards instead, as one piece with no extra joint.
Standoff_mode = "Separate ring"; // [Separate ring,Extended body]
// Back plate of the compartment. It carries the keyholes and the cable route.
Standoff_back = 3; // [1.5:0.1:8]

/* [Joints and cover] */
Joint_depth = 2.5; // [1.5:0.1:4]
Joint_clearance = 0.2; // [0.1:0.05:0.4]
Cover_plate = 2; // [1.5:0.1:3]
// Radial pilot holes in female collars for optional retaining screws.
Retaining_screws = true;
Screw_pilot_diameter = 2.1; // [1.5:0.1:3]

/* [Quality] */
Cylinder_facets = 180; // [72:12:360]

/* [Hidden] */
// Compatibility with older saved presets; Artwork_source overrides this control.
Use_svg = false;
$fn = Cylinder_facets;
eps = 0.02;
// prepare_svg.py replaces this block with normalized, embedded SVG geometry.
Embedded_artwork = false;
Embedded_radius_factor = 0.7071067811865476;
// Extra bridge angles added by the helper after checking the actual exported mesh.
Embedded_bridge_angles = [];
// [angle, local top Z] vertical ribs added only as far as a floating island.
Embedded_bridge_segments = [];
Embedded_removed_islands = [];
Embedded_surface_repair = false;
Embedded_surface_signature = [];
// BEGIN EMBEDDED PRINT LIGHT
module embedded_print_light() {}
// END EMBEDDED PRINT LIGHT
// BEGIN EMBEDDED ARTWORK
module embedded_artwork() { square(1,center=true); }
// END EMBEDDED ARTWORK
Embedded_cover_artwork = false;
// BEGIN EMBEDDED COVER ARTWORK
module embedded_cover_artwork() { square(1, center=true); }
// END EMBEDDED COVER ARTWORK

rectangular = Housing_shape=="Rectangle";
Rx = rectangular ? Rectangle_width/2 : Cylinder_diameter/2;
Ry = rectangular ? Rectangle_depth/2 : Cylinder_diameter/2;
R = min(Rx,Ry);
Rmax = rectangular ? norm([Rx,Ry]) : R;
Ri = R-Wall_thickness;
frame_width = max(4, Wall_thickness+2);
Rf = R-frame_width;
rear_floor = Joint_depth + 2;
rear_guard = 1;
front_guard = 3;
cover_depth = Joint_depth + Cover_plate;
pitch = Cylinder_height-cover_depth;
stand = Wall_standoff;
// A separate ring drives the standard keyed tongue into this module's rear socket.
// An extended body grows backwards and keeps the keyholes on its own back plate.
ring_standoff = Standoff_mode=="Separate ring" && stand>0 && Module_index==0;
body_base = Standoff_mode=="Extended body" && Module_index==0 ? stand : 0;
// Optical back of this module, measured from the room wall.
wall_offset = stand + Module_index*pitch;
// Where the printed body starts, which is the wall itself for an extended body.
body_z = wall_offset-body_base;
aperture_bottom = rear_floor+rear_guard;
aperture_top = pitch-front_guard;
tongue_outer = R-1.4;
tongue_inner = tongue_outer-1.6;
// A square's diagonal gives a conservative envelope for direct SVG import.
// The helper calculates a tighter radius from the actual polygon vertices.
active_artwork = Artwork_source=="Automatic" ?
    ((Use_svg || Svg_file!="default.svg") ? "SVG file" :
        (Embedded_artwork ? "Embedded artwork" : "Built-in demo")) : Artwork_source;
using_svg = active_artwork=="SVG file";
using_embedded = active_artwork=="Embedded artwork";
active_cover_artwork = Cover_artwork_source=="Automatic" ?
    (Cover_svg_file!="default.svg" ? "SVG file" :
        (Embedded_cover_artwork ? "Embedded artwork" : "None")) : Cover_artwork_source;
k = using_embedded ? Embedded_radius_factor : (using_svg ? sqrt(2)/2 : 0.5);
detail_fraction = Smallest_detail_percent/100;
shadow_offset = [Shadow_x,Shadow_y];
offset_radius = norm(shadow_offset);
function beam_radius(L) = k*L+(Artwork_mode=="Dark silhouette" ? Dark_field_border : 0);
function far_radius(L) = offset_radius+beam_radius(L);
// Potential outer reach, used only as an envelope test (not SVG content analysis).
function field_reach(L) = offset_radius+L/2;
r_far = far_radius(Shadow_length);
radial_supports = Support_bridges && !Automatic_bridges_only && Support_layout!="Manual XY";
xy_supports = Support_bridges && Support_layout!="Radial";
manual_supports = [
    [Support_1_enabled,Support_1_start,Support_1_end,Support_1_width],
    [Support_2_enabled,Support_2_start,Support_2_end,Support_2_width],
    [Support_3_enabled,Support_3_start,Support_3_end,Support_3_width],
    [Support_4_enabled,Support_4_start,Support_4_end,Support_4_width]];
// Added by mesh preflight even when only manual supports are selected.
repair_angles = Support_bridges && using_embedded ? Embedded_bridge_angles : [];
repair_segments = Support_bridges && using_embedded ? Embedded_bridge_segments : [];
manual_extent = xy_supports ? max(concat([0],[for(s=manual_supports) if(s[0])
    max(abs(s[1][0]),abs(s[1][1]),abs(s[2][0]),abs(s[2][1]))+s[3]])) : 0;
view_extent = max(Rmax*1.5,abs(Shadow_x)+Shadow_length*0.62,
    abs(Shadow_y)+Shadow_length*0.62,Show_grid ? manual_extent+10 : 0);

function off(H) = stand + Module_index*(H-cover_depth);
function top(H) = off(H)+H-cover_depth-front_guard;
function bottom(H) = off(H)+aperture_bottom;
// A following module has a solid back at the seating plane. Keep the LED below it.
function ceiling(H) = off(H)+H-cover_depth-1.5;
// Upper collar is thicker than the optical sidewall, hence Rf, not Ri.
function auto_source(H,L) = min(ceiling(H),
    far_radius(L)>Rf ? top(H)/(1-Rf/far_radius(L)) : ceiling(H),
    // Do not let the pedestal's shadow swallow the entire longest dimension.
    Emitter_above_pillar*(field_reach(L)-Minimum_cut_width-eps)/(Pillar_diameter/2));
function source(H,L) = LED_position=="Manual height" ? off(H)+Manual_LED_height : auto_source(H,L);
function dead_radius(H,L) = let(h=source(H,L))
    h>bottom(H) ? max(Rmax*h/(h-bottom(H)), Pillar_diameter/2*h/Emitter_above_pillar) : 1e12;
// For a flat face the inverse map has shear. det(J)/||J||F bounds its least
// singular value; using the nearest face and farthest artwork radius is safe.
function shell_scale(H,L) = let(h=source(H,L), r=far_radius(L))
    rectangular ? h*Ri/(r*sqrt(r*r+h*h)) : min(Ri/r,h*Ri/(r*r));
// Least local stretch from wall artwork to inner cylindrical surface.
function cut_estimate(H,L) = let(h=source(H,L), r=far_radius(L))
    detail_fraction*L*shell_scale(H,L);
// Conservative sum of transverse and axial geometric source blur.
function blur_estimate(H,L) = let(h=source(H,L),r=far_radius(L))
    max(0,r/Ri-1)*(Emitter_diameter+Emitter_axial_depth*r/max(h,eps));
function mechanical_ok(H,L) =
    H-cover_depth-front_guard > aperture_bottom+1 &&
    Ri>Pillar_diameter/2+5 && Rf>Pillar_diameter/2+5 &&
    tongue_inner-Joint_clearance>Rf &&
    tongue_outer+Joint_clearance+0.4<R-0.5 &&
    Pillar_wire_bore<Pillar_diameter-1.6 &&
    (!Retaining_screws || Screw_pilot_diameter<Joint_depth) &&
    source(H,L)-off(H)-Emitter_above_pillar>rear_floor+1;
function quality_ok(H,L) = cut_estimate(H,L)>=Minimum_cut_width-1e-9 &&
    blur_estimate(H,L)<=Maximum_blur+1e-9;
function feasible(H,L) = mechanical_ok(H,L) && quality_ok(H,L) &&
    source(H,L)>bottom(H)+1 && source(H,L)<=ceiling(H)+1e-9 &&
    source(H,L)<=auto_source(H,L)+1e-9 &&
    // A rectangle's corner radius is diagnostic only: light can pass its faces.
    field_reach(L)>max(R*source(H,L)/(source(H,L)-bottom(H)),
        Pillar_diameter/2*source(H,L)/Emitter_above_pillar)+Minimum_cut_width;
// Quality decreases monotonically with L in automatic mode. Search 0.01 mm.
function max_length(H,lo,hi,n=18) = n==0 ? lo :
    let(mid=(lo+hi)/2) quality_ok(H,mid) ? max_length(H,mid,hi,n-1) : max_length(H,lo,mid,n-1);
// With an offset, feature quality need not be monotone in length. Use a bounded
// 1%-of-requested-length scan instead of the centred case's binary search.
function length_at_height(H) = offset_radius>eps ?
    let(candidates=[for(i=[1:100]) let(L=Shadow_length*i/100) if(feasible(H,L)) L])
        (len(candidates)>0 ? max(candidates) : 0) :
    (quality_ok(H,Shadow_length) ? Shadow_length :
        (quality_ok(H,2*R+1) ? floor(max_length(H,2*R+1,Shadow_length)*10)/10 : 0));
function cost(pair) = pow((pair[0]-Cylinder_height)/Cylinder_height,2)+
    pow((pair[1]-Shadow_length)/Shadow_length,2);
function best_pair(a,i=0,b=undef) = i>=len(a) ? b :
    best_pair(a,i+1,is_undef(b) || cost(a[i])<cost(b) ? a[i] : b);

h = source(Cylinder_height,Shadow_length);
local_h = h-wall_offset;
dead = dead_radius(Cylinder_height,Shadow_length);
valid = feasible(Cylinder_height,Shadow_length);
surface_signature = [Cylinder_diameter,Rectangle_width,Rectangle_depth,Cylinder_height,
    Wall_standoff,Module_index,Shadow_length,Shadow_x,Shadow_y,Artwork_rotation,
    Minimum_web_width,Manual_LED_height,Emitter_above_pillar,Pillar_diameter,
    Wall_thickness,Joint_depth,Cover_plate,LED_position,Artwork_mode,Dark_field_border,Housing_shape];
surface_repair_current = Embedded_surface_signature==surface_signature;
// Nearest means this explicitly weighted, bounded grid; never a global claim.
search_max = min(300,max(160,3*Cylinder_height));
suggestions = valid || LED_position!="Automatic" ? [] : [
    for(H=[Cylinder_height:1:search_max]) let(L=length_at_height(H))
        if(L>0 && feasible(H,L)) [H,L]
];
nearest = best_pair(suggestions);
same_height_L = valid ? Shadow_length : length_at_height(Cylinder_height);
same_length_options = valid ? [] : [for(H=[Cylinder_height:1:search_max])
    if(feasible(H,Shadow_length)) H];
same_length_H = len(same_length_options)>0 ? same_length_options[0] : undef;
suggestion_text = is_undef(nearest) ? "No candidate in search range; change diameter, detail or emitter." :
    str("Try height ",nearest[0]," mm, shadow ",nearest[1]," mm.");

assert(Cylinder_diameter>0 && Cylinder_height>0 && Shadow_length>0,"Dimensions must be positive.");
assert(Rectangle_width>0 && Rectangle_depth>0 && Minimum_web_width>=0,"Invalid housing or web dimensions.");
assert(Housing_shape=="Cylinder" || Housing_shape=="Rectangle","Unknown housing shape.");
assert(!(using_embedded && Embedded_surface_repair && !surface_repair_current &&
    (Output=="Body" || Output=="Print layout")),
    "Prepared surface stencil is stale. Rerun prepare_svg.py with the new dimensions before exporting.");
assert(Smallest_detail_percent>0 && Minimum_cut_width>0 && Maximum_blur>0,"Quality limits must be positive.");
assert(Emitter_diameter>=0 && Emitter_axial_depth>=0,"Emitter sizes cannot be negative.");
assert(Module_index>=0 && Module_index==floor(Module_index),"Module index must be a non-negative integer.");
assert(Bridge_count>=1 && Joint_clearance>=0 && Emitter_above_pillar>0,"Invalid support/joint parameters.");
assert(Wall_thickness>0 && Pillar_diameter>0 && Pillar_wire_bore>0 && Joint_depth>0 && Cover_plate>0,
    "Mechanical dimensions must be positive.");
assert(!using_embedded || Embedded_artwork,"This file has no embedded artwork. Select SVG file or Built-in demo.");
assert(active_cover_artwork!="Embedded artwork" || Embedded_cover_artwork,"No embedded cover SVG: select SVG file or None.");
assert(Cover_hole_diameter>=0 && Cover_hole_diameter/2<Rf-1,"Cover hole is negative or would damage the joint.");
assert(active_cover_artwork=="None" || (Cover_artwork_depth>0 && Cover_artwork_depth<Cover_plate-Joint_clearance-0.5),
    "Inlay must leave at least 0.5 mm of solid cover under it.");
assert(Cover_artwork_length>0 && Grid_spacing>0,"Artwork length and grid spacing must be positive.");
assert(Dark_field_border>0,"The dark silhouette field needs a positive border for a valid stencil.");
assert(Wall_standoff>=0 && Standoff_back>0,"Standoff values must be valid.");
assert(!ring_standoff || Wall_standoff>=Standoff_back,
    "A separate standoff ring needs Wall_standoff >= Standoff_back.");
for(s=manual_supports) if(xy_supports && s[0]) {
    assert(len(s[1])==2 && len(s[2])==2 && s[3]>0,"Support requires two XY endpoints and positive width.");
    assert(norm(s[2]-s[1])>eps,"Support start and end must be different.");
}

echo("ACTIVE ARTWORK",active_artwork);
if(using_svg) echo("SVG PATH",Svg_file);
echo("COVER ARTWORK",active_cover_artwork);
echo("Shadow placement XY mm",shadow_offset);
echo("Pillar through-bore / cover hole mm",[Pillar_wire_bore,Cover_hole_diameter]);
echo("STATUS", valid ? "OPTICAL ENVELOPE PASSES; SVG topology still requires checking" :
    "GENERATION NOT POSSIBLE under the selected limits");
echo("LED centre, local XYZ mm",[0,0,local_h]);
echo("LED centre, wall XYZ mm",[0,0,h]);
echo("Closed first-module depth / stacking pitch mm",[Cylinder_height,pitch]);
echo("Central occlusion radius mm",dead);
echo("Housing shape / outer XY mm",[Housing_shape,2*Rx,2*Ry]);
if(using_embedded && Embedded_surface_repair && !surface_repair_current)
    echo("WARNING: surface stencil settings changed. Rerun prepare_svg.py before exporting this body.");
if(rectangular) echo("Occlusion radius is the corner envelope; Projection uses the actual rectangle.");
echo("Opaque web simplification target / wall-space width mm",[Minimum_web_width,
    Minimum_web_width/max(shell_scale(Cylinder_height,Shadow_length),0.000001)]);
echo("Wall standoff mm / optical back above wall mm",[stand,wall_offset]);
if(stand>0) echo("A standoff lifts the source and sharpens detail, and widens the hidden centre.");
echo("Conservative artwork radius / smallest declared detail mm",[r_far,detail_fraction*Shadow_length]);
echo("Estimated minimum cut / selected minimum mm",[cut_estimate(Cylinder_height,Shadow_length),Minimum_cut_width]);
echo("Estimated worst geometric blur / selected maximum mm",[blur_estimate(Cylinder_height,Shadow_length),Maximum_blur]);
echo(offset_radius<eps ? "LED XY is the minimax solution for a concentric 360-degree field." :
    "Translated artwork: LED stays on-axis; height uses a conservative shifted-field bound, not a global XYZ optimum.");
for(s=manual_supports) if(xy_supports && s[0]) {
    sr=max(norm(s[1]),norm(s[2]))+s[3]/2;
    estimate=s[3]*min(Ri/sr,h*Ri/(sr*sr));
    echo("Manual support: wall width / conservative local shell width mm",[s[3],estimate]);
    if(estimate<Minimum_cut_width) echo("WARNING: this manual support may be too thin; increase its wall width and run mesh preflight.");
}
echo("Preview is an ideal geometric footprint, not a photometric simulation. Source extent can only worsen it.");
echo("Centre is intentionally occluded; support spokes intentionally remove light. Floating islands are not auto-detected here.");
if(!valid) {
    echo("SUGGESTED sampled compromise [height,shadow] mm",nearest);
    echo("Keep height: shadow mm", feasible(Cylinder_height,same_height_L) ? same_height_L : "No feasible smaller length in range");
    echo("Keep shadow: height mm",is_undef(same_length_H) ? "No feasible height <= search limit" : same_length_H);
    echo("Search: height increases in 1 mm steps, <=300 mm; equal squared relative changes in height and shadow length.");
    if(offset_radius>eps) echo("Offset search keeps XY fixed and samples lengths in 1% steps; no continuous closest-point claim.");
    if(LED_position!="Automatic") echo("Switch LED_position to Automatic for reliable suggestions.");
}

// An original, open-aperture sunburst demo; no external file required.
module demo_artwork() {
    for(a=[0:30:330]) rotate(a)
        hull() {
            translate([0.24,0]) circle(r=0.038,$fn=16);
            translate([0.46,0]) circle(r=0.04,$fn=16);
        }
}
module normalized_artwork() {
    if(using_svg) {
        if(Svg_long_axis=="X") resize([1,0],auto=true) import(file=Svg_file,center=true,convexity=20);
        else resize([0,1],auto=true) import(file=Svg_file,center=true,convexity=20);
    } else if(using_embedded) embedded_artwork();
    else demo_artwork();
}
module target_artwork() {
    translate(shadow_offset) rotate(Artwork_rotation) scale(Shadow_length) normalized_artwork();
}
module raw_intended_light() {
    if(Artwork_mode=="Light shapes") target_artwork();
    else difference() { translate(shadow_offset) circle(r=beam_radius(Shadow_length)); target_artwork(); }
}
// Closing the light field removes hairline opaque slivers instead of narrowing
// every light stroke. Remaining detached solids get real ribs in mesh preflight.
// This deliberately simplifies dark detail; inspect the measured shadow change.
// A disk-based filter is not a minimum-neck-width or overhang certificate.
module intended_light() {
    w=Minimum_web_width/max(shell_scale(Cylinder_height,Shadow_length),0.000001);
    if(Minimum_web_width<=0) raw_intended_light();
    else if(using_embedded && Embedded_surface_repair && surface_repair_current)
        // Remove sub-0.02 mm wall-space tangencies before oblique extrusion.
        offset(delta=-0.01) offset(delta=0.01) union() {
            raw_intended_light();
            embedded_print_light();
            for(p=Embedded_removed_islands) offset(delta=0.02) polygon(p);
        }
    else union() {
        raw_intended_light();
        offset(r=-w/2,$fn=32) offset(r=w/2,$fn=32) raw_intended_light();
    }
}
// All mating profiles use the same physical inset, including rectangular joints.
module footprint(radius=R) {
    if(rectangular) square([2*(Rx-R+radius),2*(Ry-R+radius)],center=true);
    else circle(r=radius);
}
module prism(radius,height) { linear_extrude(height=height) footprint(radius); }
function wall_radius(a) = rectangular ? min(Rx/max(abs(cos(a)),1e-9),Ry/max(abs(sin(a)),1e-9)) : R;
// A perspective cone. This cuts oblique tunnels through the FULL wall thickness.
// Cropping the extrusion just below its apex avoids degenerate mesh vertices.
module perspective_cone() {
    apex_gap = 0.05;
    translate([0,0,-wall_offset])
        linear_extrude(height=h-apex_gap,scale=apex_gap/h,convexity=30)
            children();
}
module light_cone() { perspective_cone() intended_light(); }
// These wedges have constant angular width. Their shadows are exactly wedges.
module bridge_wedges_2d(radius, selected=undef) {
    angle = 2*asin(min(0.99,Bridge_width/(2*Ri)));
    angles = is_undef(selected) ? concat(radial_supports ? [for(a=[0:360/Bridge_count:360-360/Bridge_count]) a+Bridge_rotation] : [],repair_angles) : selected;
    for(a=angles)
        rotate(a)
            // Keep wedges disjoint at the axis: a shared zero-width edge is non-manifold.
            polygon([[0.1*cos(angle/2),0.1*sin(angle/2)],
                [radius*cos(angle/2),radius*sin(angle/2)],
                [radius*cos(angle/2),-radius*sin(angle/2)],
                [0.1*cos(angle/2),-0.1*sin(angle/2)]]);
}
module xy_support_shapes() {
    if(xy_supports) for(s=manual_supports) if(s[0]) hull() {
        translate(s[1]) circle(d=s[3],$fn=24);
        translate(s[2]) circle(d=s[3],$fn=24);
    }
}
module optical_cutters() {
    difference() {
        intersection() {
            light_cone();
            translate([0,0,aperture_bottom]) prism(R+1,aperture_top-aperture_bottom);
        }
        if(Support_bridges) translate([0,0,aperture_bottom-eps])
            linear_extrude(height=aperture_top-aperture_bottom+2*eps)
                bridge_wedges_2d(Rmax+3);
        if(xy_supports) perspective_cone() xy_support_shapes();
        for(s=repair_segments) translate([0,0,aperture_bottom-eps])
            linear_extrude(height=min(s[1],aperture_top)-aperture_bottom+2*eps)
                bridge_wedges_2d(Rmax+3,[s[0]]);
    }
}
module ring(outer,inner,height) {
    difference() { prism(outer,height); translate([0,0,-eps]) prism(inner,height+2*eps); }
}
module tongue() {
    ring(tongue_outer,tongue_inner,Joint_depth);
    // Registration key; all modules and their artwork share an angular datum.
    translate([Rx-1.4-0.3,-1,0]) cube([0.7,2,Joint_depth]);
}
module socket() {
    translate([0,0,-eps]) ring(tongue_outer+Joint_clearance,
        tongue_inner-Joint_clearance,Joint_depth+Joint_clearance+eps);
    translate([Rx-1.4-0.3-Joint_clearance,-1-Joint_clearance,-eps])
        cube([0.7+2*Joint_clearance,2+2*Joint_clearance,Joint_depth+Joint_clearance+eps]);
}
module retaining_holes() {
    if(Retaining_screws) for(a=[60,180,300]) rotate([0,0,a])
        translate([wall_radius(a)+eps,0,Joint_depth/2]) rotate([0,-90,0])
            cylinder(d=Screw_pilot_diameter,h=(R-tongue_inner+eps)*(rectangular ? sqrt(2) : 1),$fn=24);
}
module keyhole(plate=rear_floor) {
    // Two 3.5 mm screw shafts, 7 mm entry heads. Insert then slide lamp down 5 mm.
    linear_extrude(height=plate+2*eps) union() {
        circle(d=7,$fn=32);
        hull() { circle(d=3.5,$fn=24); translate([0,5]) circle(d=3.5,$fn=24); }
    }
}
module optical_body() {
    difference() {
        union() {
            difference() {
                union() {
                    prism(R,rear_floor);
                    ring(R,Ri,pitch);
                    translate([0,0,aperture_top]) ring(R,Rf,front_guard);
                    translate([0,0,pitch-eps]) tongue();
                }
                optical_cutters();
            }
            // Thin hollow pedestal. Emitting centre is Emitter_above_pillar higher.
            translate([0,0,rear_floor-eps])
                cylinder(d=Pillar_diameter,h=local_h-Emitter_above_pillar-rear_floor+eps);
        }
        // An extended body has no rear joint: a blind socket would seal a void inside it.
        if(body_base==0) socket();
        if(Module_index>0 || ring_standoff) retaining_holes();
        // The pillar is a tube: this bore runs the whole way to the rear cable route.
        translate([0,0,-eps]) cylinder(d=Pillar_wire_bore,h=local_h+eps,$fn=32);
        if(Module_index==0 && stand==0) for(x=[-Rx/2,Rx/2]) translate([x,0,-eps]) keyhole();
        // Rear cable route, contained under the opaque rear floor.
        translate([-Pillar_wire_bore/2,-Ry-1,-eps]) cube([Pillar_wire_bore,Ry+1,1.2]);
    }
}
// The electronics compartment between the room wall and the optical back. Its cavity
// vents through the pillar bore, so the assembly stays one connected surface.
module standoff_shell(with_tongue) {
    plate = min(stand,Standoff_back);
    cavity = min(Ri,tongue_inner-0.8);
    difference() {
        union() {
            prism(R,stand);
            if(with_tongue) translate([0,0,stand-eps]) tongue();
        }
        if(stand>plate+0.6) translate([0,0,plate]) prism(cavity,stand-plate+eps);
        for(x=[-Rx/2,Rx/2]) translate([x,0,-eps]) keyhole(plate);
        translate([0,0,-eps]) cylinder(d=Pillar_wire_bore,h=plate+2*eps,$fn=32);
        // Rear cable route, contained under the opaque back plate.
        translate([-Pillar_wire_bore/2,-Ry-1,-eps]) cube([Pillar_wire_bore,Ry+1,1.2]);
    }
}
module standoff_ring() { standoff_shell(true); }
module body() {
    if(body_base>0) { standoff_shell(false); translate([0,0,body_base]) optical_body(); }
    else optical_body();
}
module cover_artwork_2d() {
    difference() {
        intersection() {
            footprint(R-2);
            rotate(Cover_artwork_rotation) scale(Cover_artwork_length) {
                if(active_cover_artwork=="Embedded artwork") embedded_cover_artwork();
                else if(active_cover_artwork=="SVG file") {
                    if(Cover_svg_long_axis=="X") resize([1,0],auto=true) import(Cover_svg_file,center=true,convexity=20);
                    else resize([0,1],auto=true) import(Cover_svg_file,center=true,convexity=20);
                }
            }
        }
        if(Cover_hole_diameter>0) circle(d=Cover_hole_diameter,$fn=64);
    }
}
module cover_artwork() {
    if(active_cover_artwork!="None") translate([0,0,cover_depth-Cover_artwork_depth])
        linear_extrude(height=Cover_artwork_depth,convexity=20) cover_artwork_2d();
}
module cover_base() {
    difference() {
        prism(R,cover_depth);
        socket();
        // Electronics clearance under the opaque lid plate.
        translate([0,0,-eps]) prism(Rf,Joint_depth+Joint_clearance+eps);
        retaining_holes();
        if(Cover_hole_diameter>0) translate([0,0,-eps]) cylinder(d=Cover_hole_diameter,h=cover_depth+2*eps,$fn=64);
        if(active_cover_artwork!="None") translate([0,0,cover_depth-Cover_artwork_depth])
            linear_extrude(height=Cover_artwork_depth+eps,convexity=20) cover_artwork_2d();
    }
}
module cover() {
    color([0.23,0.29,0.36]) cover_base();
    color("white") cover_artwork();
}
module printable_cover(part="Both") {
    translate([0,0,cover_depth]) rotate([180,0,0]) {
        if(part=="Base") cover_base();
        else if(part=="Artwork") color("white") cover_artwork();
        else cover();
    }
}
module projected_light() {
    difference() {
        intersection() {
            intended_light();
            // Outer opening edge clips rays when the source is above the aperture.
            if(h>wall_offset+aperture_top)
                scale(h/(h-wall_offset-aperture_top)) footprint(Rf);
            else circle(r=max(Shadow_length*3,r_far*3));
        }
        scale(h/(h-wall_offset-aperture_bottom)) footprint();
        circle(r=Pillar_diameter/2*h/Emitter_above_pillar);
        if(Support_bridges) bridge_wedges_2d(max(Shadow_length*3,r_far*3));
        if(xy_supports) xy_support_shapes();
        for(s=repair_segments) intersection() {
            bridge_wedges_2d(max(Shadow_length*3,r_far*3),[s[0]]);
            if(h>wall_offset+min(s[1],aperture_top)+eps)
                scale(h/(h-wall_offset-min(s[1],aperture_top)-eps)) footprint();
            else circle(r=max(Shadow_length*3,r_far*3));
        }
    }
}
module led_marker() {
    translate([0,0,h]) color([1,0.62,0.12]) sphere(r=1.3,$fn=24);
}
module wall_preview() {
    extent = Show_grid ? ceil(view_extent/Grid_spacing)*Grid_spacing+Grid_spacing*0.7 : view_extent;
    color([0.055,0.066,0.08]) translate([-extent,-extent,-1.2]) cube([2*extent,2*extent,1]);
    color([1,0.83,0.42]) translate([0,0,-0.15]) linear_extrude(height=0.08) projected_light();
    if(Show_grid) coordinate_grid();
}
module coordinate_grid() {
    n=ceil(view_extent/Grid_spacing);
    e=n*Grid_spacing;
    line_width=max(0.35,Grid_spacing*0.025);
    label_every=max(1,ceil((2*n+1)/31));
    // Display geometry only; never called by the print outputs.
    for(i=[-n:n]) {
        color(i==0 ? [0.35,0.75,1] : [0.32,0.39,0.47,0.55])
            translate([i*Grid_spacing-line_width/2,-e,0.08]) cube([line_width,2*e,0.06]);
        color(i==0 ? [0.35,0.75,1] : [0.32,0.39,0.47,0.55])
            translate([-e,i*Grid_spacing-line_width/2,0.08]) cube([2*e,line_width,0.06]);
        if(i%label_every==0) color([0.7,0.82,0.9]) translate([i*Grid_spacing,-e-Grid_spacing*0.4,0.08])
            linear_extrude(0.08) text(str(i*Grid_spacing),size=Grid_spacing*0.2,halign="center");
        if(i%label_every==0) color([0.7,0.82,0.9]) translate([-e-Grid_spacing*0.15,i*Grid_spacing,0.08])
            linear_extrude(0.08) text(str(i*Grid_spacing),size=Grid_spacing*0.2,halign="right");
    }
    color("cyan") translate([e,2,0.08]) linear_extrude(0.08) text("+X",size=Grid_spacing*0.3);
    color("cyan") translate([2,e,0.08]) linear_extrude(0.08) text("+Y",size=Grid_spacing*0.3);
    if(xy_supports) for(i=[0:len(manual_supports)-1]) let(s=manual_supports[i]) if(s[0])
        for(j=[1:2]) color([1,0.4,0.4]) translate([s[j][0],s[j][1],0.2]) {
            linear_extrude(0.08) difference() { circle(r=2,$fn=24); circle(r=1.4,$fn=24); }
            translate([3,3,0]) linear_extrude(0.08) text(str(i+1,j==1 ? "A" : "B"),size=4);
        }
}
module sample_rays() {
    for(a=[15:60:315]) color([1,0.75,0.2,0.45]) hull() {
        translate([0,0,h]) sphere(r=0.2,$fn=8);
        translate([Shadow_x+beam_radius(Shadow_length)*cos(a),Shadow_y+beam_radius(Shadow_length)*sin(a),0]) sphere(r=0.2,$fn=8);
    }
}
module diagnostics() {
    lines = [str("Artwork: ",active_artwork),
        valid ? "OPTICAL ENVELOPE: PASS" : "GENERATION NOT POSSIBLE",
        str("Shadow XY: ",Shadow_x,", ",Shadow_y," mm; standoff ",stand," mm"),
        str("LED xyz = 0, 0, ",round(local_h*100)/100," mm (local)"),
        str("Centre hidden: radius ",round(dead*10)/10," mm"),
        str("Cut estimate: ",round(cut_estimate(Cylinder_height,Shadow_length)*1000)/1000," mm"),
        str("Blur estimate: ",round(blur_estimate(Cylinder_height,Shadow_length)*100)/100," mm"),
        valid ? "Check stencil connectivity before printing." : suggestion_text];
    for(i=[0:len(lines)-1]) translate([0,-i*6,0])
        color(valid ? [0.4,0.9,0.6] : [1,0.25,0.15])
            linear_extrude(height=0.6) text(lines[i],size=4);
}

printable_cover();