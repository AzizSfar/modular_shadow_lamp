// Artwork is embedded. To replace it, select Artwork_source = SVG file, or rerun prepare_svg.py.
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
Bridge_width = 0.9; // [0.4:0.1:2]
Bridge_rotation = 15; // [0:1:180]
// Helper mode disables the regular spokes and retains only mesh-detected repairs.
Automatic_bridges_only = true;
// Simplify narrow opaque strips in wall space using a conservative shell scale.
// 0 preserves the original geometry. This changes the shadow; inspect Projection.
Minimum_web_width = 0.6; // [0:0.1:2]

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
Embedded_artwork = true;
Embedded_radius_factor = 0.5;
// Extra bridge angles added by the helper after checking the actual exported mesh.
Embedded_bridge_angles = [];
// [angle, local top Z] vertical ribs added only as far as a floating island.
Embedded_bridge_segments = [[89.99857,9.172509999999999],[269.99857,9.172509999999999]];
Embedded_removed_islands = [];
Embedded_surface_repair = true;
Embedded_surface_signature = [100,80,100,30,0,0,300,0,0,0,0.6,24,3,8,2,2.5,2,"Automatic","Light shapes",3,"Cylinder"];
// BEGIN EMBEDDED PRINT LIGHT
module embedded_print_light() { polygon(points=[[42.011102,73.186171],[41.919831,73.238488],[41.828495,73.290691],[41.737093,73.34278],[41.92091,73.665793],[42.106352,73.991663],[42.293443,74.320429],[42.386062,74.267645],[42.478616,74.214746],[42.571104,74.161732],[42.382785,73.833668],[42.196125,73.508494],[43.632892,75.792439],[43.53837,75.846775],[43.443781,75.900994],[43.349124,75.955095],[43.547012,76.301829],[43.746715,76.651743],[43.948259,77.004881],[44.044224,76.950032],[44.14012,76.895064],[44.235948,76.839977],[44.033086,76.487595],[43.832075,76.13843],[21.100984,91.921075],[20.986373,91.947309],[20.87173,91.973401],[20.757054,91.999349],[20.859275,92.452417],[20.962509,92.909969],[21.06677,93.372072],[21.172073,93.838795],[21.278433,94.310207],[21.385868,94.78638],[21.494394,95.267386],[21.604026,95.753298],[21.714782,96.244192],[21.82668,96.740146],[21.939738,97.241238],[22.053972,97.747547],[22.175813,97.719978],[22.29762,97.692256],[22.419392,97.664382],[22.303265,97.158503],[22.424371,97.130623],[22.308817,96.630102],[22.194447,96.134712],[22.314277,96.106968],[22.200463,95.616774],[22.087804,95.131554],[21.976283,94.651235],[21.865882,94.175741],[21.756585,93.705001],[21.639749,93.732051],[21.53212,93.265859],[21.425556,92.804281],[21.309844,92.830919],[21.2049,92.373757],[4.373376,120.915018],[4.222633,120.920377],[4.071882,120.925547],[3.921126,120.930529],[3.770363,120.935323],[3.619594,120.93993],[3.642495,121.705088],[3.665687,122.479989],[3.689176,123.264821],[3.842843,123.260126],[3.996504,123.25524],[4.150158,123.250161],[4.303806,123.244892],[4.457448,123.239431],[4.429067,122.45476],[4.401046,121.680018],[18.301092,144.578151],[18.120838,144.600854],[17.940555,144.623332],[17.760245,144.645585],[17.895758,145.749255],[18.033356,146.869896],[18.173085,148.007903],[18.357587,147.985132],[18.542061,147.962132],[18.726505,147.938901],[18.58252,146.801424],[18.440733,145.681305],[-20.148648,89.824215],[-20.260613,89.799027],[-20.372546,89.773699],[-20.484448,89.748232],[-20.582903,90.179592],[-20.682309,90.615118],[-20.78268,91.054872],[-20.669149,91.08071],[-20.555586,91.106407],[-20.441991,91.131962],[-20.343266,90.691836],[-20.245489,90.255941],[-20.974516,92.42634],[-21.089724,92.40012],[-21.2049,92.373757],[-21.320042,92.34725],[-21.425556,92.804281],[-21.53212,93.265859],[-21.648375,93.238943],[-21.756585,93.705001],[-21.865882,94.175741],[-21.976283,94.651235],[-22.087804,95.131554],[-22.200463,95.616774],[-22.314277,96.106968],[-22.429265,96.602215],[-22.308817,96.630102],[-22.424371,97.130623],[-22.541129,97.636357],[-22.419392,97.664382],[-22.29762,97.692256],[-22.175813,97.719978],[-22.060948,97.213811],[-21.947266,96.71286],[-21.83475,96.217047],[-21.723381,95.726291],[-21.613143,95.240515],[-21.504018,94.759646],[-21.39599,94.283607],[-21.289041,93.812328],[-21.183157,93.345736],[-21.07832,92.883763],[-3.619594,120.93993],[-3.770363,120.935323],[-3.921126,120.930529],[-4.071882,120.925547],[-4.222633,120.920377],[-4.373376,120.915018],[-4.524113,120.909472],[-4.552736,121.674437],[-4.581724,122.449143],[-4.611083,123.233778],[-4.457448,123.239431],[-4.303806,123.244892],[-4.150158,123.250161],[-3.996504,123.25524],[-3.842843,123.260126],[-3.689176,123.264821],[-3.665687,122.479989],[-3.642495,121.705088],[-39.563856,69.725917],[-39.65075,69.67654],[-39.737582,69.627055],[-39.824353,69.577461],[-39.990941,69.868509],[-40.158929,70.162001],[-40.328334,70.45797],[-40.240465,70.508191],[-40.152534,70.558303],[-40.06454,70.608304],[-39.896243,70.311704],[-39.729354,70.017585],[-42.386062,74.267645],[-42.478616,74.214746],[-42.571104,74.161732],[-42.663525,74.108603],[-42.853938,74.439358],[-43.046057,74.773078],[-43.239907,75.109805],[-43.146237,75.163652],[-43.052499,75.217383],[-42.958695,75.270996],[-42.766106,74.933547],[-42.575236,74.59911],[-44.044224,76.950032],[-44.14012,76.895064],[-44.235948,76.839977],[-44.331707,76.784769],[-44.536891,77.140158],[-44.743982,77.498851],[-44.953009,77.860896],[-44.855908,77.916876],[-44.758737,77.972736],[-44.661496,78.028475],[-44.453825,77.665651],[-44.248077,77.306185],[-42.102308,-73.133741],[-42.011102,-73.186171],[-41.919831,-73.238488],[-41.828495,-73.290691],[-42.012713,-73.613474],[-42.198562,-73.939113],[-42.386062,-74.267645],[-42.478616,-74.214746],[-42.571104,-74.161732],[-42.663525,-74.108603],[-42.474798,-73.780774],[-42.287733,-73.455832],[-43.92696,-76.083727],[-43.832075,-76.13843],[-43.737122,-76.193015],[-43.642101,-76.247481],[-43.84224,-76.597146],[-44.044224,-76.950032],[-44.248077,-77.306185],[-44.344417,-77.250963],[-44.440688,-77.19562],[-44.536891,-77.140158],[-44.331707,-76.784769],[-44.128406,-76.432641],[-21.320042,-92.34725],[-21.2049,-92.373757],[-21.089724,-92.40012],[-20.974516,-92.42634],[-21.07832,-92.883763],[-21.183157,-93.345736],[-21.289041,-93.812328],[-21.39599,-94.283607],[-21.504018,-94.759646],[-21.613143,-95.240515],[-21.723381,-95.726291],[-21.83475,-96.217047],[-21.947266,-96.71286],[-22.060948,-97.213811],[-22.175813,-97.719978],[-22.29762,-97.692256],[-22.419392,-97.664382],[-22.541129,-97.636357],[-22.424371,-97.130623],[-22.308817,-96.630102],[-22.429265,-96.602215],[-22.314277,-96.106968],[-22.200463,-95.616774],[-22.319648,-95.589023],[-22.206384,-95.103944],[-22.094264,-94.623764],[-21.98327,-94.148408],[-21.865882,-94.175741],[-21.756585,-93.705001],[-21.648375,-93.238943],[-21.53212,-93.265859],[-21.425556,-92.804281],[20.757054,-91.999349],[20.87173,-91.973401],[20.986373,-91.947309],[21.100984,-91.921075],[21.2049,-92.373757],[21.309844,-92.830919],[21.425556,-92.804281],[21.53212,-93.265859],[21.639749,-93.732051],[21.756585,-93.705001],[21.865882,-94.175741],[21.976283,-94.651235],[22.087804,-95.131554],[22.200463,-95.616774],[22.314277,-96.106968],[22.194447,-96.134712],[22.308817,-96.630102],[22.424371,-97.130623],[22.303265,-97.158503],[22.419392,-97.664382],[22.29762,-97.692256],[22.175813,-97.719978],[22.053972,-97.747547],[21.939738,-97.241238],[21.82668,-96.740146],[21.714782,-96.244192],[21.604026,-95.753298],[21.494394,-95.267386],[21.385868,-94.78638],[21.278433,-94.310207],[21.172073,-93.838795],[21.06677,-93.372072],[20.962509,-92.909969],[20.859275,-92.452417],[9.375203,-119.123247],[9.523702,-119.111467],[9.672187,-119.099501],[9.820656,-119.087351],[9.882013,-119.831373],[9.944141,-120.584751],[10.007055,-121.347661],[9.855767,-121.360043],[9.704465,-121.372235],[9.553147,-121.384239],[9.493086,-120.621098],[9.433776,-119.867494],[40.234263,-70.907418],[40.322629,-70.857204],[40.410933,-70.80688],[40.499174,-70.756446],[40.671468,-71.057462],[40.845234,-71.36105],[41.020491,-71.667244],[40.931114,-71.718327],[40.841674,-71.769298],[40.75217,-71.820158],[40.578059,-71.513312],[40.40543,-71.209076],[41.195191,-72.390519],[41.285406,-72.339106],[41.375556,-72.287581],[41.465642,-72.235944],[41.645882,-72.549933],[41.827695,-72.866663],[42.011102,-73.186171],[41.919831,-73.238488],[41.828495,-73.290691],[41.737093,-73.34278],[41.554882,-73.022588],[41.374255,-72.70518],[44.044224,-76.950032],[44.14012,-76.895064],[44.235948,-76.839977],[44.331707,-76.784769],[44.536891,-77.140158],[44.743982,-77.498851],[44.953009,-77.860896],[44.855908,-77.916876],[44.758737,-77.972736],[44.661496,-78.028475],[44.453825,-77.665651],[44.248077,-77.306185]],paths=[[0,1,2,3,4,5,6,7,8,9,10,11],[12,13,14,15,16,17,18,19,20,21,22,23],[24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57],[58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73],[74,75,76,77,78,79,80,81,82,83,84,85],[86,87,88,89,90,91,92,93,94,95,96,97],[98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127],[128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145],[146,147,148,149,150,151,152,153,154,155,156,157],[158,159,160,161,162,163,164,165,166,167,168,169],[170,171,172,173,174,175,176,177,178,179,180,181],[182,183,184,185,186,187,188,189,190,191,192,193],[194,195,196,197,198,199,200,201,202,203,204,205],[206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237],[238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271],[272,273,274,275,276,277,278,279,280,281,282,283],[284,285,286,287,288,289,290,291,292,293,294,295],[296,297,298,299,300,301,302,303,304,305,306,307],[308,309,310,311,312,313,314,315,316,317,318,319]],convexity=40); }
// END EMBEDDED PRINT LIGHT
// BEGIN EMBEDDED ARTWORK
module embedded_artwork() {
    union() {
        polygon(points=[[0.037086792,0.170845417],[0.07231375,0.183171667],[0.103915,0.203027917],[0.130305417,0.229418333],[0.15016125,0.261019167],[0.162487917,0.296246667],[0.166666667,0.333333333],[0.162487917,0.37042],[0.15016125,0.405647083],[0.130305417,0.43725],[0.103915,0.4636375],[0.07231375,0.483495833],[0.037086792,0.495820833],[0.0,0.5],[-0.037086792,0.495820833],[-0.07231375,0.483495833],[-0.103915,0.4636375],[-0.130305417,0.43725],[-0.15016125,0.405647083],[-0.162487917,0.37042],[-0.166666667,0.333333333],[-0.162487917,0.296246667],[-0.15016125,0.261019167],[-0.130305417,0.229418333],[-0.103915,0.203027917],[-0.07231375,0.183171667],[-0.037086792,0.170845417],[0.0,0.166666667],[-0.016689042,0.26021375],[-0.032541292,0.265760417],[-0.046761667,0.274695833],[-0.0586375,0.286571667],[-0.0675725,0.300792083],[-0.073119583,0.316644167],[-0.075,0.333333333],[-0.073119583,0.3500225],[-0.0675725,0.365874583],[-0.0586375,0.380095],[-0.046761667,0.391970833],[-0.032541292,0.400905833],[-0.016689042,0.406452917],[0.0,0.408333333],[0.016689042,0.406452917],[0.032541292,0.400905833],[0.046761667,0.391970833],[0.0586375,0.380095],[0.0675725,0.365874583],[0.073119583,0.3500225],[0.075,0.333333333],[0.073119583,0.316644167],[0.0675725,0.300792083],[0.0586375,0.286571667],[0.046761667,0.274695833],[0.032541292,0.265760417],[0.016689042,0.26021375],[0.0,0.258333333],[0.037086792,-0.495820833],[0.07231375,-0.483495833],[0.103915,-0.4636375],[0.130305417,-0.43725],[0.15016125,-0.405647083],[0.162487917,-0.37042],[0.166666667,-0.333333333],[0.162487917,-0.296246667],[0.15016125,-0.261019167],[0.130305417,-0.229418333],[0.103915,-0.203027917],[0.07231375,-0.183171667],[0.037086792,-0.170845417],[0.0,-0.166666667],[-0.037086792,-0.170845417],[-0.07231375,-0.183171667],[-0.103915,-0.203027917],[-0.130305417,-0.229418333],[-0.15016125,-0.261019167],[-0.162487917,-0.296246667],[-0.166666667,-0.333333333],[-0.162487917,-0.37042],[-0.15016125,-0.405647083],[-0.130305417,-0.43725],[-0.103915,-0.4636375],[-0.07231375,-0.483495833],[-0.037086792,-0.495820833],[0.0,-0.5],[-0.016689042,-0.406452917],[-0.032541292,-0.400905833],[-0.046761667,-0.391970833],[-0.0586375,-0.380095],[-0.0675725,-0.365874583],[-0.073119583,-0.3500225],[-0.075,-0.333333333],[-0.073119583,-0.316644167],[-0.0675725,-0.300792083],[-0.0586375,-0.286571667],[-0.046761667,-0.274695833],[-0.032541292,-0.265760417],[-0.016689042,-0.26021375],[0.0,-0.258333333],[0.016689042,-0.26021375],[0.032541292,-0.265760417],[0.046761667,-0.274695833],[0.0586375,-0.286571667],[0.0675725,-0.300792083],[0.073119583,-0.316644167],[0.075,-0.333333333],[0.073119583,-0.3500225],[0.0675725,-0.365874583],[0.0586375,-0.380095],[0.046761667,-0.391970833],[0.032541292,-0.400905833],[0.016689042,-0.406452917],[0.0,-0.408333333]],
            paths=[[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27],[28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55],[56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83],[84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111]],convexity=30);
    }
}
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

if(Output=="Cover") printable_cover();
else if(Output=="Cover base") printable_cover("Base");
else if(Output=="Cover artwork") printable_cover("Artwork");
else if(Output=="Standoff") {
    assert(ring_standoff,
        "The Standoff part needs Wall_standoff > 0, Standoff_mode = Separate ring and Module_index = 0.");
    standoff_ring();
}
else if(Output=="Diagnostics") diagnostics();
else if(!valid) {
    if(Output=="Body" || Output=="Print layout")
        assert(false,str("Generation impossible. ",suggestion_text));
    else diagnostics();
} else if(Output=="Body") body();
else if(Output=="Print layout") {
    body();
    translate([2*Rx+10,0,0]) printable_cover();
    if(ring_standoff) translate([0,2*Ry+10,0]) standoff_ring();
} else if(Output=="Projection") {
    wall_preview();
    color([0.16,0.19,0.23]) prism(R,1);
    if(Show_report) translate([-view_extent,-view_extent-Grid_spacing-10,0]) diagnostics();
} else {
    wall_preview();
    if(ring_standoff) color([0.42,0.47,0.53]) standoff_ring();
    color([0.65,0.72,0.77]) translate([0,0,body_z]) body();
    // Exploded cover is display geometry only; optical preview assumes a fitted cover.
    if(Cover_preview!="Hidden") translate([Cover_preview=="Exploded" ? 2*Rx+10 : 0,0,
        wall_offset+pitch+(Cover_preview=="Exploded" ? 12 : 0)]) cover();
    led_marker();
    if(Show_rays) sample_rays();
    if(Output=="Stack preview") {
        // Lower modules are shown as opaque envelopes. Generate their own patterns separately.
        if(Module_index>0) for(i=[0:Module_index-1])
            color([0.25,0.3,0.35,0.5]) translate([0,0,stand+i*pitch]) ring(R,Ri,pitch);
    }
    if(Show_report) translate([-view_extent,-view_extent-Grid_spacing-10,0]) diagnostics();
}
