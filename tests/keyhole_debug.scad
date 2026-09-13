// Modular shadow lamp — millimetres. Read README.md and OPTICS.md.
// Self-contained OpenSCAD 2021.01 / MakerWorld Parametric Model Maker.
// The wall is XY at z=0; +z points into the room. Filled SVG areas transmit light.

/* [View] */
Output = "Assembly"; // [Assembly,Projection,Body,Cover,Print layout,Stack preview,Diagnostics]
Show_rays = false;
Show_report = true;

/* [Artwork] */
Use_svg = false;
// MakerWorld recognizes this variable as an SVG upload control.
Svg_file = "default.svg";
// Select the LONGER artwork axis. The other axis scales proportionally.
Svg_long_axis = "Y"; // [X,Y]
// Longest dimension of the complete artwork BEFORE central occlusion, in mm.
Shadow_length = 300; // [100:5:1500]
// Light shapes matches luminous outlines in the reference photo.
Artwork_mode = "Light shapes"; // [Light shapes,Dark silhouette]
Artwork_rotation = 0; // [-180:1:180]
// Smallest IMPORTANT line or gap, as % of the artwork's longest dimension.
// This is a declared design requirement, NOT an automatic SVG measurement.
Smallest_detail_percent = 5; // [0.1:0.1:20]

/* [Cylinder] */
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
Pillar_wire_bore = 3; // [1:0.1:6]

/* [Stencil supports] */
// Spokes interrupt light but can connect otherwise floating opaque islands.
// They do NOT guarantee connectivity for arbitrary artwork; run prepare_svg.py.
Support_bridges = true;
Bridge_count = 12; // [3:1:48]
Bridge_width = 0.8; // [0.4:0.1:2]
Bridge_rotation = 0; // [0:1:180]

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
$fn = Cylinder_facets;
eps = 0.02;
// prepare_svg.py replaces this block with normalized, embedded SVG geometry.
Embedded_artwork = false;
Embedded_radius_factor = 0.7071067811865476;
// Extra bridge angles added by the helper after checking the actual exported mesh.
Embedded_bridge_angles = [];
// BEGIN EMBEDDED ARTWORK
module embedded_artwork() { square(1, center=true); }
// END EMBEDDED ARTWORK

R = Cylinder_diameter/2;
Ri = R-Wall_thickness;
frame_width = max(4, Wall_thickness+2);
Rf = R-frame_width;
rear_floor = Joint_depth + 2;
rear_guard = 1;
front_guard = 3;
cover_depth = Joint_depth + Cover_plate;
pitch = Cylinder_height-cover_depth;
wall_offset = Module_index*pitch;
aperture_bottom = rear_floor+rear_guard;
aperture_top = pitch-front_guard;
tongue_outer = R-1.4;
tongue_inner = tongue_outer-1.6;
// A square's diagonal gives a conservative envelope for direct SVG import.
// The helper calculates a tighter radius from the actual polygon vertices.
k = Embedded_artwork ? Embedded_radius_factor : (Use_svg ? sqrt(2)/2 : 0.5);
detail_fraction = Smallest_detail_percent/100;
r_far = k*Shadow_length;

function off(H) = Module_index*(H-cover_depth);
function top(H) = off(H)+H-cover_depth-front_guard;
function bottom(H) = off(H)+aperture_bottom;
function ceiling(H) = off(H)+H-Cover_plate-1.5;
// Upper collar is thicker than the optical sidewall, hence Rf, not Ri.
function auto_source(H,L) = min(ceiling(H),
    k*L>Rf ? top(H)/(1-Rf/(k*L)) : ceiling(H));
function source(H,L) = LED_position=="Manual height" ? off(H)+Manual_LED_height : auto_source(H,L);
function dead_radius(H,L) = let(h=source(H,L))
    h>bottom(H) ? max(R*h/(h-bottom(H)), Pillar_diameter/2*h/Emitter_above_pillar) : 1e12;
// Least local stretch from wall artwork to inner cylindrical surface.
function cut_estimate(H,L) = let(h=source(H,L), r=k*L)
    detail_fraction*L*min(Ri/r,h*Ri/(r*r));
// Conservative sum of transverse and axial geometric source blur.
function blur_estimate(H,L) = let(h=source(H,L),r=k*L)
    max(0,r/Ri-1)*(Emitter_diameter+Emitter_axial_depth*r/max(h,eps));
function mechanical_ok(H,L) =
    H-cover_depth-front_guard > aperture_bottom+1 &&
    Ri>Pillar_diameter/2+5 && Rf>tongue_inner-3 &&
    tongue_inner-Joint_clearance>Rf &&
    tongue_outer+Joint_clearance+0.4<R-0.5 &&
    Pillar_wire_bore<Pillar_diameter-1.6 &&
    Screw_pilot_diameter<Joint_depth &&
    source(H,L)-off(H)-Emitter_above_pillar>rear_floor+1;
function quality_ok(H,L) = cut_estimate(H,L)>=Minimum_cut_width-1e-9 &&
    blur_estimate(H,L)<=Maximum_blur+1e-9;
function feasible(H,L) = mechanical_ok(H,L) && quality_ok(H,L) &&
    source(H,L)>bottom(H)+1 && source(H,L)<=ceiling(H)+1e-9 &&
    source(H,L)<=auto_source(H,L)+1e-9 &&
    L/2>dead_radius(H,L)+Minimum_cut_width;
// Quality decreases monotonically with L in automatic mode. Search 0.01 mm.
function max_length(H,lo,hi,n=18) = n==0 ? lo :
    let(mid=(lo+hi)/2) quality_ok(H,mid) ? max_length(H,mid,hi,n-1) : max_length(H,lo,mid,n-1);
function length_at_height(H) = quality_ok(H,Shadow_length) ? Shadow_length :
    quality_ok(H,2*R+1) ? floor(max_length(H,2*R+1,Shadow_length)*10)/10 : 0;
function cost(pair) = pow((pair[0]-Cylinder_height)/Cylinder_height,2)+
    pow((pair[1]-Shadow_length)/Shadow_length,2);
function best_pair(a,i=0,b=undef) = i>=len(a) ? b :
    best_pair(a,i+1,is_undef(b) || cost(a[i])<cost(b) ? a[i] : b);

h = source(Cylinder_height,Shadow_length);
local_h = h-wall_offset;
dead = dead_radius(Cylinder_height,Shadow_length);
valid = feasible(Cylinder_height,Shadow_length);
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
assert(Smallest_detail_percent>0 && Minimum_cut_width>0 && Maximum_blur>0,"Quality limits must be positive.");
assert(Emitter_diameter>=0 && Emitter_axial_depth>=0,"Emitter sizes cannot be negative.");
assert(Module_index>=0 && Module_index==floor(Module_index),"Module index must be a non-negative integer.");
assert(Bridge_count>=1 && Joint_clearance>=0 && Emitter_above_pillar>0,"Invalid support/joint parameters.");

echo("STATUS", valid ? "OPTICAL ENVELOPE PASSES; SVG topology still requires checking" :
    "GENERATION NOT POSSIBLE under the selected limits");
echo("LED centre, local XYZ mm",[0,0,local_h]);
echo("LED centre, wall XYZ mm",[0,0,h]);
echo("Closed first-module depth / stacking pitch mm",[Cylinder_height,pitch]);
echo("Central occlusion radius mm",dead);
echo("Conservative artwork radius / smallest declared detail mm",[r_far,detail_fraction*Shadow_length]);
echo("Estimated minimum cut / selected minimum mm",[cut_estimate(Cylinder_height,Shadow_length),Minimum_cut_width]);
echo("Estimated worst geometric blur / selected maximum mm",[blur_estimate(Cylinder_height,Shadow_length),Maximum_blur]);
echo("LED XY is the analytic minimax solution for a concentric 360-degree field; not an arbitrary-artwork optimum.");
echo("Preview is an ideal geometric footprint, not a photometric simulation. Source extent can only worsen it.");
echo("Centre is intentionally occluded; support spokes intentionally remove light. Floating islands are not auto-detected here.");
if(!valid) {
    echo("SUGGESTED sampled compromise [height,shadow] mm",nearest);
    echo("Keep height: shadow mm", feasible(Cylinder_height,same_height_L) ? same_height_L : "No feasible smaller length in range");
    echo("Keep shadow: height mm",is_undef(same_length_H) ? "No feasible height <= search limit" : same_length_H);
    echo("Search: height increases in 1 mm steps, <=300 mm; equal squared relative changes in height and shadow length.");
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
    if(Embedded_artwork) embedded_artwork();
    else if(Use_svg) {
        if(Svg_long_axis=="X") resize([1,0],auto=true) import(file=Svg_file,center=true,convexity=20);
        else resize([0,1],auto=true) import(file=Svg_file,center=true,convexity=20);
    } else demo_artwork();
}
module target_artwork() {
    rotate(Artwork_rotation) scale(Shadow_length) normalized_artwork();
}
module intended_light() {
    if(Artwork_mode=="Light shapes") target_artwork();
    else difference() { circle(r=r_far); target_artwork(); }
}
// A perspective cone. This cuts oblique tunnels through the FULL wall thickness.
// Cropping the extrusion just below its apex avoids degenerate mesh vertices.
module light_cone() {
    apex_gap = 0.05;
    translate([0,0,-wall_offset])
        linear_extrude(height=h-apex_gap,scale=apex_gap/h,convexity=30)
            intended_light();
}
// These wedges have constant angular width. Their shadows are exactly wedges.
module bridge_wedges_2d(radius) {
    angle = 2*asin(min(0.99,Bridge_width/(2*Ri)));
    angles = concat([for(a=[0:360/Bridge_count:360-360/Bridge_count]) a+Bridge_rotation],Embedded_bridge_angles);
    for(a=angles)
        rotate(a)
            polygon([[0,0],[radius*cos(angle/2),radius*sin(angle/2)],
                [radius*cos(angle/2),-radius*sin(angle/2)]]);
}
module optical_cutters() {
    difference() {
        intersection() {
            light_cone();
            translate([0,0,aperture_bottom]) cylinder(r=R+1,h=aperture_top-aperture_bottom);
        }
        if(Support_bridges) translate([0,0,aperture_bottom-eps])
            linear_extrude(height=aperture_top-aperture_bottom+2*eps)
                bridge_wedges_2d(R+3);
    }
}
module ring(outer,inner,height) {
    difference() { cylinder(r=outer,h=height); translate([0,0,-eps]) cylinder(r=inner,h=height+2*eps); }
}
module tongue() {
    ring(tongue_outer,tongue_inner,Joint_depth);
    // Registration key; all modules and their artwork share an angular datum.
    translate([tongue_outer-0.3,-1,0]) cube([0.7,2,Joint_depth]);
}
module socket() {
    translate([0,0,-eps]) ring(tongue_outer+Joint_clearance,
        tongue_inner-Joint_clearance,Joint_depth+Joint_clearance+eps);
    translate([tongue_outer-0.3-Joint_clearance,-1-Joint_clearance,-eps])
        cube([0.7+2*Joint_clearance,2+2*Joint_clearance,Joint_depth+Joint_clearance+eps]);
}
module retaining_holes() {
    if(Retaining_screws) for(a=[60,180,300]) rotate([0,0,a])
        translate([R+eps,0,Joint_depth/2]) rotate([0,-90,0])
            cylinder(d=Screw_pilot_diameter,h=R-tongue_inner+eps,$fn=24);
}
module keyhole() {
    // Two 3.5 mm screw shafts, 7 mm entry heads. Insert then slide lamp down 5 mm.
    linear_extrude(height=rear_floor+2*eps) union() {
        circle(d=7,$fn=32);
        hull() { circle(d=3.5,$fn=24); translate([0,5]) circle(d=3.5,$fn=24); }
    }
}
module body() {
    difference() {
        union() {
            difference() {
                union() {
                    cylinder(r=R,h=rear_floor);
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
        socket();
        if(Module_index>0) retaining_holes();
        translate([0,0,-eps]) cylinder(d=Pillar_wire_bore,h=local_h+eps,$fn=32);
        if(Module_index==0) for(x=[-R/2,R/2]) translate([x,0,-eps]) keyhole();
        // Rear cable route, contained under the opaque rear floor.
        translate([-Pillar_wire_bore/2,-R-1,-eps]) cube([Pillar_wire_bore,R+1,1.2]);
    }
}
module cover() {
    difference() {
        cylinder(r=R,h=cover_depth);
        socket();
        // Electronics clearance under the opaque lid plate.
        translate([0,0,-eps]) cylinder(r=Rf,h=Joint_depth+Joint_clearance+eps);
        retaining_holes();
    }
}
module printable_cover() {
    translate([0,0,cover_depth]) rotate([180,0,0]) cover();
}
module projected_light() {
    difference() {
        intersection() {
            intended_light();
            // Outer opening edge clips rays when the source is above the aperture.
            circle(r=h>wall_offset+aperture_top ?
                Ri*h/(h-wall_offset-aperture_top) : max(Shadow_length*3,r_far*3));
            // Thicker front rim may clip earlier than the optical sidewall.
            circle(r=h>wall_offset+aperture_top ?
                Rf*h/(h-wall_offset-aperture_top) : max(Shadow_length*3,r_far*3));
        }
        circle(r=dead);
        if(Support_bridges) bridge_wedges_2d(max(Shadow_length*3,r_far*3));
    }
}
module led_marker() {
    translate([0,0,h]) color([1,0.62,0.12]) sphere(r=1.3,$fn=24);
}
module wall_preview() {
    extent = max(Shadow_length*0.62,R*1.5);
    color([0.055,0.066,0.08]) translate([-extent,-extent,-1.2]) cube([2*extent,2*extent,1]);
    color([1,0.83,0.42]) translate([0,0,-0.15]) linear_extrude(height=0.08) projected_light();
}
module sample_rays() {
    for(a=[15:60:315]) color([1,0.75,0.2,0.45]) hull() {
        translate([0,0,h]) sphere(r=0.2,$fn=8);
        translate([r_far*cos(a),r_far*sin(a),0]) sphere(r=0.2,$fn=8);
    }
}
module diagnostics() {
    lines = [valid ? "OPTICAL ENVELOPE: PASS" : "GENERATION NOT POSSIBLE",
        str("LED xyz = 0, 0, ",round(local_h*100)/100," mm (local)"),
        str("Centre hidden: radius ",round(dead*10)/10," mm"),
        str("Cut estimate: ",round(cut_estimate(Cylinder_height,Shadow_length)*1000)/1000," mm"),
        str("Blur estimate: ",round(blur_estimate(Cylinder_height,Shadow_length)*100)/100," mm"),
        valid ? "Check stencil connectivity before printing." : suggestion_text];
    for(i=[0:len(lines)-1]) translate([0,-i*6,0])
        color(valid ? [0.4,0.9,0.6] : [1,0.25,0.15])
            linear_extrude(height=0.6) text(lines[i],size=4);
}

keyhole();
