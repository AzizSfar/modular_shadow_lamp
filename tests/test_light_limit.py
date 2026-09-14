"""Checks for the dark-silhouette light limit: the band it draws and the slot it opens."""
from pathlib import Path
import math
import re
import subprocess
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_svg import find_openscad, run_scad, mesh_report, embedded_module, read_flat_svg

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "output" / "light_limit_tests"
SOURCE = ROOT / "modular_shadow_lamp.scad"
DARK = ['Artwork_mode="Dark silhouette"']


def setUpModule():
    WORK.mkdir(parents=True, exist_ok=True)


def diagnostics(name, *definitions):
    return run_scad(find_openscad(), SOURCE, WORK / (name + ".csg"),
                    ['Output="Diagnostics"'] + list(definitions))


def probe(name, geometry, *definitions):
    """Render one 2D module from the generator on its own, so assertions see only it."""
    body = SOURCE.read_text(encoding="utf-8").split('\nif(Output=="Cover")')[0]
    path = WORK / (name + ".scad")
    path.write_text(body + "\nlinear_extrude(1) %s;\n" % geometry, encoding="utf-8")
    stl = WORK / (name + ".stl")
    run_scad(find_openscad(), path, stl, list(definitions))
    return mesh_report(stl)


def field(name, *definitions):
    """The lit region as the generator will actually cut it."""
    return probe(name, "intended_light()", *definitions)


def area(report):
    """The probes are extruded 1 mm, so the signed volume is the area in mm^2."""
    return report["signed_volume_mm3"]


def reach(log):
    return float(re.search(
        r'"Conservative artwork radius / smallest declared detail mm", \[([-\d.eE]+)', log).group(1))


def slot(log):
    match = re.search(r'"Light limit shape / band mm / slot in shell mm", '
                      r'\["[^"]*", [-\d.eE]+, ([-\d.eE]+)\]', log)
    if not match:
        raise AssertionError("no light-limit slot reported")
    return float(match.group(1))


class FieldShapeTests(unittest.TestCase):
    """Default artwork spans 300 mm, so its half-extent is 150 mm and k*L is 150 mm."""
    T = 25

    def test_off_is_unchanged_by_the_feature(self):
        plain = field("off_plain", *DARK)
        explicit = field("off_explicit", *DARK, "Light_limit=false")
        self.assertAlmostEqual(plain["signed_volume_mm3"], explicit["signed_volume_mm3"], places=6)

    def test_a_band_lights_less_wall_than_the_unlimited_disc(self):
        disc = area(field("bounded_off", *DARK))
        band = area(field("bounded_on", *DARK, "Light_limit=true", "Light_limit_thickness=10"))
        self.assertLess(band, disc)
        self.assertGreater(band, 0)

    def test_the_band_is_exactly_the_artwork_grown_by_the_thickness(self):
        """The identity the feature rests on, checked against the two halves separately."""
        limited = ["Light_limit=true", "Light_limit_thickness=25",
                   'Light_limit_shape="Same as shadow"']
        band = area(field("identity_band", *DARK, *limited))
        grown = area(probe("identity_grown",
                           "offset(r=25,$fn=min(Cylinder_facets,64)) target_artwork()",
                           *DARK, *limited))
        shadow = area(probe("identity_shadow", "target_artwork()", *DARK, *limited))
        self.assertAlmostEqual(band, grown - shadow, delta=max(1.0, 0.001 * grown))

    def test_separate_shapes_keep_separate_halos_until_the_thickness_merges_them(self):
        """Widening the band silently fuses nearby artwork; Diagnostics cannot see this."""
        limited = ["Light_limit=true", 'Light_limit_shape="Same as shadow"']
        narrow = area(field("merge_narrow", *DARK, *limited, "Light_limit_thickness=10"))
        wide = area(field("merge_wide", *DARK, *limited, "Light_limit_thickness=50"))
        # Fusing costs area relative to two independent bands, so growth is sub-quadratic.
        self.assertGreater(wide, narrow)
        self.assertLess(wide / narrow, 25)

    def test_each_shape_reaches_exactly_as_far_as_its_geometry_predicts(self):
        for shape, expected in (("Circle", 150 + 25), ("Same as shadow", 150 + 25),
                                ("Rectangle", 150 + 25)):
            with self.subTest(shape=shape):
                r = field("reach_" + shape.replace(" ", "_"), *DARK, "Light_limit=true",
                          "Light_limit_thickness=25", 'Light_limit_shape="%s"' % shape)
                half = max(r["bounds_mm"][0][1], r["bounds_mm"][1][1])
                self.assertAlmostEqual(half, expected, delta=0.6)

    def test_a_rectangle_reaches_further_than_a_circle_because_of_its_corners(self):
        """The optics must use the corner, not the side, or the envelope is understated."""
        circle = reach(diagnostics("reach_circle", *DARK, "Light_limit=true",
                                   "Light_limit_thickness=25", 'Light_limit_shape="Circle"'))
        rect = reach(diagnostics("reach_rect", *DARK, "Light_limit=true",
                                 "Light_limit_thickness=25", 'Light_limit_shape="Rectangle"'))
        self.assertAlmostEqual(circle, 175, delta=0.01)
        self.assertAlmostEqual(rect, math.hypot(175, 175), delta=0.01)

    def test_a_thicker_band_lights_more_wall(self):
        previous = 0
        for thickness in (10, 25, 50):
            lit = area(field("grow_%d" % thickness, *DARK, "Light_limit=true",
                             "Light_limit_thickness=%d" % thickness))
            self.assertGreater(lit, previous)
            previous = lit

    def test_a_band_detaches_what_it_encircles_exactly_as_the_disc_already_did(self):
        """Not a new defect: dark silhouette always strands islands, limited or not.

        Recorded here so nobody blames the light limit for needing bridges, and so a
        regression that made it worse would show up as a rising component count.
        """
        counts = {}
        for label, extra in (("unlimited", []),
                             ("limited", ["Light_limit=true", "Light_limit_thickness=25"])):
            stl = WORK / ("islands_" + label + ".stl")
            run_scad(find_openscad(), SOURCE, stl,
                     ['Output="Body"', "Support_bridges=false"] + DARK + extra)
            counts[label] = mesh_report(stl)["surface_components"]
        self.assertGreater(counts["limited"], 1)
        self.assertEqual(counts["limited"], counts["unlimited"])


class SlotWidthTests(unittest.TestCase):
    def test_the_reported_slot_scales_with_the_band(self):
        thin = slot(diagnostics("slot_10", *DARK, "Light_limit=true", "Light_limit_thickness=10"))
        thick = slot(diagnostics("slot_50", *DARK, "Light_limit=true", "Light_limit_thickness=50"))
        self.assertGreater(thick, thin)
        self.assertAlmostEqual(thin, 0.45, delta=0.02)

    def test_a_band_too_fine_to_print_warns_and_still_builds(self):
        log = diagnostics("slot_5", *DARK, "Light_limit=true", "Light_limit_thickness=5")
        self.assertIn("WARNING", log)
        self.assertIn("Building anyway", log)
        self.assertLess(slot(log), 0.4)
        # Warn-only means the request still passes and still produces geometry.
        self.assertIn("OPTICAL ENVELOPE PASSES", log)
        self.assertGreater(area(field("slot_5_field", *DARK, "Light_limit=true",
                                      "Light_limit_thickness=5")), 0)

    def test_the_suggested_minimum_actually_clears_the_limit(self):
        log = diagnostics("needed", *DARK, "Light_limit=true", "Light_limit_thickness=5")
        needed = float(re.search(r"About ([\d.]+) mm would clear it", log).group(1))
        self.assertGreaterEqual(slot(diagnostics("needed_check", *DARK, "Light_limit=true",
                                                 "Light_limit_thickness=%s" % needed)), 0.4)

    def test_no_slot_is_reported_when_the_limit_is_off(self):
        with self.assertRaises(AssertionError):
            slot(diagnostics("no_slot", *DARK))


class MeasuredExtentTests(unittest.TestCase):
    def test_the_helper_measures_the_artwork_proportions(self):
        """Rectangle needs the true box; the helper is the only thing that can measure it."""
        exe = find_openscad()
        svg = (ROOT / "examples" / "two_rings.svg").resolve()
        importer = WORK / "extent_import.scad"
        importer.write_text('import(file="%s",center=true,dpi=96,$fn=180);\n' % svg.as_posix(),
                            encoding="utf-8")
        flat = WORK / "extent_flat.svg"
        run_scad(exe, importer, flat)
        _, _, size, _ = embedded_module(read_flat_svg(flat))
        extent = [round(v / max(size), 4) for v in size]
        # two_rings is a tall stack of two circles: three times taller than wide.
        self.assertAlmostEqual(extent[1], 1.0, places=4)
        self.assertAlmostEqual(extent[0], 1 / 3, places=2)


if __name__ == "__main__":
    unittest.main()


def prepared(name, svg, *definitions):
    """A file carrying both the artwork and its measured silhouette, as the helper writes it.

    Built here rather than by a full preflight run, so the tests exercise the geometry
    without paying for a mesh check they are not asserting anything about.
    """
    from prepare_svg import embedded_module, outline_module, set_value
    exe = find_openscad()
    importer = WORK / (name + "_import.scad")
    importer.write_text('import(file="%s",center=true,dpi=96,$fn=180);\n'
                        % Path(svg).resolve().as_posix(), encoding="utf-8")
    flat = WORK / (name + "_flat.svg")
    run_scad(exe, importer, flat)
    groups = read_flat_svg(flat)
    artwork, radius, size, _ = embedded_module(groups)
    source = SOURCE.read_text(encoding="utf-8")
    source = re.sub(r"// BEGIN EMBEDDED ARTWORK.*?// END EMBEDDED ARTWORK",
                    "// BEGIN EMBEDDED ARTWORK\n" + artwork + "\n// END EMBEDDED ARTWORK",
                    source, flags=re.S)
    source = re.sub(r"// BEGIN ARTWORK SILHOUETTE.*?// END ARTWORK SILHOUETTE",
                    "// BEGIN ARTWORK SILHOUETTE\n" + outline_module(groups)
                    + "\n// END ARTWORK SILHOUETTE", source, flags=re.S)
    for key, value in (("Embedded_artwork", True), ("Embedded_outline", True),
                       ("Embedded_radius_factor", radius),
                       ("Embedded_extent", [size[0]/max(size), size[1]/max(size)]),
                       ("Artwork_mode", "Dark silhouette"), ("Light_limit", True)):
        source = set_value(source, key, value)
    path = WORK / (name + ".scad")
    path.write_text(source, encoding="utf-8")
    return path


def lit_area(scad, name, *definitions):
    body = scad.read_text(encoding="utf-8").split('\nif(Output=="Cover")')[0]
    path = WORK / (name + "_probe.scad")
    path.write_text(body + "\nlinear_extrude(1) intended_light();\n", encoding="utf-8")
    stl = WORK / (name + "_probe.stl")
    run_scad(find_openscad(), path, stl, list(definitions))
    return mesh_report(stl)["signed_volume_mm3"]


class SilhouetteTests(unittest.TestCase):
    """A closed outline such as a circuit map is the case offset() alone cannot serve."""

    @classmethod
    def setUpClass(cls):
        cls.scad = prepared("monza", ROOT / "examples" / "monza_example.svg")

    def test_only_the_outermost_contour_survives(self):
        from prepare_svg import silhouette_contours, contour_area, artwork_normalisation
        groups = read_flat_svg(WORK / "monza_flat.svg")
        _, _, longest = artwork_normalisation(groups)
        kept = silhouette_contours(groups, longest)
        # Monza is one closed ribbon: an outer boundary, the interior it encloses, and a
        # degenerate sliver. Only the boundary bounds solid area at depth zero.
        self.assertEqual(len(kept), 1)
        self.assertGreater(abs(contour_area(kept[0])),
                           sum(abs(contour_area(c)) for g in groups for c in g) / 2)

    def test_the_silhouette_shares_the_artwork_normalisation(self):
        """Both modules are scaled by Shadow_length, so a mismatch would offset the fill."""
        import json
        from prepare_svg import embedded_module, outline_module
        groups = read_flat_svg(WORK / "monza_flat.svg")
        def corners(scad_module):
            points = [p for block in re.findall(r"points=(\[\[.*?\]\])", scad_module)
                      for p in json.loads(block)]
            return (min(p[0] for p in points), max(p[0] for p in points),
                    min(p[1] for p in points), max(p[1] for p in points))
        artwork = corners(embedded_module(groups)[0])
        outline = corners(outline_module(groups))
        # Normalised to the longest side about the shared centre, so nothing exceeds a half.
        self.assertLessEqual(max(abs(v) for v in outline), 0.5 + 1e-6)
        # The silhouette wraps the artwork, so their extents must coincide exactly.
        for a, o in zip(artwork, outline):
            self.assertAlmostEqual(a, o, places=6)

    def test_unlimiting_the_inside_lights_the_enclosed_interior(self):
        both = lit_area(self.scad, "sides_both", "Light_limit_outside=true",
                        "Light_limit_inside=true")
        inside_free = lit_area(self.scad, "sides_in_off", "Light_limit_outside=true",
                               "Light_limit_inside=false")
        self.assertGreater(inside_free, both)

    def test_unlimiting_the_outside_lights_the_rest_of_the_beam(self):
        both = lit_area(self.scad, "sides_both2", "Light_limit_outside=true",
                        "Light_limit_inside=true")
        outside_free = lit_area(self.scad, "sides_out_off", "Light_limit_outside=false",
                                "Light_limit_inside=true")
        self.assertGreater(outside_free, both)

    def test_both_unlimited_is_the_plain_dark_silhouette(self):
        free = lit_area(self.scad, "sides_none", "Light_limit_outside=false",
                        "Light_limit_inside=false")
        off = lit_area(self.scad, "sides_off", "Light_limit=false")
        self.assertAlmostEqual(free, off, delta=max(1.0, 0.002 * off))

    def test_the_two_sides_are_independent(self):
        """Freeing each side separately must add up to freeing both."""
        area = lambda n, o, i: lit_area(self.scad, n, "Light_limit_outside=%s" % o,
                                        "Light_limit_inside=%s" % i)
        both = area("ind_both", "true", "true")
        no_in = area("ind_in", "true", "false")
        no_out = area("ind_out", "false", "true")
        neither = area("ind_none", "false", "false")
        self.assertAlmostEqual(neither - both, (no_in - both) + (no_out - both),
                               delta=max(1.0, 0.002 * neither))


class MethodReportingTests(unittest.TestCase):
    def test_a_direct_import_honours_the_setting_and_names_its_method(self):
        log = diagnostics("method_direct", *DARK, "Light_limit=true", "Light_limit_inside=false")
        self.assertRegex(log, r'"Light limited outside / inside", \[true, false\]')
        self.assertIn("Interior closed at", log)
        self.assertIn("(automatic)", log)

    def test_a_set_span_is_reported_as_set(self):
        self.assertIn("(set)", diagnostics("method_set", *DARK, "Light_limit=true",
                                           "Light_limit_inside=false", "Interior_span=150"))

    def test_the_approximation_is_never_called_exact(self):
        log = diagnostics("method_approx", *DARK, "Light_limit=true", "Light_limit_inside=false")
        self.assertIn("an approximation", log)
        self.assertNotIn("measured silhouette.", log.split("approximation")[0])


class InteriorSpanTests(unittest.TestCase):
    """A directly imported SVG has no silhouette, so the interior is found by closing."""
    MONZA = ["Light_limit=true", "Light_limit_thickness=25", "Shadow_length=300",
             'Svg_file="%s"' % (ROOT / "examples" / "monza_example.svg").resolve().as_posix()]

    def lit(self, name, *extra):
        return field(name, *DARK, *self.MONZA, *extra)["signed_volume_mm3"]

    def test_zero_means_automatic_and_the_setting_takes_effect_unaided(self):
        """The whole point: inside OFF must work with nothing else configured."""
        limited = self.lit("span_on", "Light_limit_inside=true")
        self.assertGreater(self.lit("span_zero", "Light_limit_inside=false",
                                    "Interior_span=0"), limited)

    def test_the_automatic_span_matches_a_hand_picked_one(self):
        """Shadow_length cannot under-fill, so it must agree with any sufficient value."""
        auto = self.lit("span_auto", "Light_limit_inside=false")
        picked = self.lit("span_picked", "Light_limit_inside=false", "Interior_span=150")
        self.assertAlmostEqual(auto, picked, delta=max(1.0, 0.002 * auto))

    def test_a_span_wider_than_the_enclosed_area_lights_it(self):
        limited = self.lit("span_ref", "Light_limit_inside=true")
        opened = self.lit("span_120", "Light_limit_inside=false", "Interior_span=120")
        self.assertGreater(opened, limited)

    def test_the_closing_converges_once_the_span_clears_the_interior(self):
        """Above the enclosed width the answer stops moving: it has found the whole interior."""
        areas = [self.lit("conv_%d" % span, "Light_limit_inside=false",
                          "Interior_span=%d" % span) for span in (120, 150, 250)]
        for value in areas[1:]:
            self.assertAlmostEqual(value, areas[0], delta=max(1.0, 0.001 * areas[0]))

    def test_a_span_too_narrow_finds_less_than_the_full_interior(self):
        narrow = self.lit("span_narrow", "Light_limit_inside=false", "Interior_span=20")
        wide = self.lit("span_wide", "Light_limit_inside=false", "Interior_span=150")
        limited = self.lit("span_ref2", "Light_limit_inside=true")
        self.assertLessEqual(narrow, wide)
        self.assertGreaterEqual(narrow, limited - 1e-6)

    def test_the_approximation_is_declared_rather_than_passed_off_as_exact(self):
        log = diagnostics("span_note", *DARK, *self.MONZA, "Light_limit_inside=false",
                          "Interior_span=150")
        self.assertIn("an approximation", log)
        self.assertNotIn("NOTE: separate inside and outside limits", log)

    def test_a_measured_silhouette_is_used_in_preference_to_any_span(self):
        scad = prepared("span_prepared", ROOT / "examples" / "monza_example.svg")
        exact = lit_area(scad, "span_prep_exact", "Light_limit_inside=false", "Interior_span=0")
        with_span = lit_area(scad, "span_prep_span", "Light_limit_inside=false",
                             "Interior_span=250")
        self.assertAlmostEqual(with_span, exact, places=6)
        self.assertIn("measured silhouette",
                      run_scad(find_openscad(), scad, WORK / "span_prep.csg",
                               ['Output="Diagnostics"', "Light_limit_inside=false"]))


class DeclaredAxisTests(unittest.TestCase):
    """resize() normalises the DECLARED axis, so naming the wrong one must not lie to the optics."""
    MONZA = ["Shadow_length=300",
             'Svg_file="%s"' % (ROOT / "examples" / "monza_example.svg").resolve().as_posix()]

    def artwork(self, name, axis):
        return probe(name, "target_artwork()", *DARK, *self.MONZA, 'Svg_long_axis="%s"' % axis)

    def reach(self, report):
        x, y, _ = report["bounds_mm"]
        return math.hypot(max(abs(x[0]), abs(x[1])), max(abs(y[0]), abs(y[1])))

    def test_the_correct_axis_is_left_untouched(self):
        """Monza is the taller way up, so Y is right and the clamp must do nothing."""
        report = self.artwork("axis_right", "Y")
        for low, high in report["bounds_mm"][:2]:
            self.assertLessEqual(max(abs(low), abs(high)), 150 + 1e-3)
        self.assertLess(self.reach(report), 300 * math.sqrt(2) / 2)

    def test_the_wrong_axis_is_clamped_instead_of_overshooting(self):
        wrong = self.artwork("axis_wrong", "X")
        for low, high in wrong["bounds_mm"][:2]:
            self.assertLessEqual(max(abs(low), abs(high)), 150 + 1e-3)
        # Whatever the declaration, the artwork stays inside the envelope k assumes.
        self.assertLessEqual(self.reach(wrong), 300 * math.sqrt(2) / 2 + 1e-3)

    def test_the_clamp_actually_removes_the_overshoot(self):
        """Compared against the raw resize, so the clamp cannot be a no-op that just passes."""
        raw = probe("axis_raw", 'scale(300) resize([1,0],auto=true) '
                    'import(file="%s",center=true,convexity=20)'
                    % (ROOT / "examples" / "monza_example.svg").resolve().as_posix())
        self.assertGreater(raw["bounds_mm"][1][1], 250)          # overshoots badly unclamped
        clamped = self.artwork("axis_wrong2", "X")
        self.assertLess(clamped["signed_volume_mm3"], raw["signed_volume_mm3"])
        self.assertAlmostEqual(clamped["bounds_mm"][1][1], 150, delta=0.01)

    def test_the_clamp_is_declared_on_screen(self):
        log = diagnostics("axis_note", *DARK, *self.MONZA, 'Svg_long_axis="X"')
        self.assertIn("clamped to", log)

    def test_prepared_artwork_is_not_clamped(self):
        """It carries its measured radius, so the square envelope does not apply to it."""
        scad = prepared("axis_prepared", ROOT / "examples" / "monza_example.svg")
        body = scad.read_text(encoding="utf-8").split('\nif(Output=="Cover")')[0]
        path = WORK / "axis_prepared_probe.scad"
        path.write_text(body + "\nlinear_extrude(1) target_artwork();\n", encoding="utf-8")
        stl = WORK / "axis_prepared_probe.stl"
        run_scad(find_openscad(), path, stl, ["Shadow_length=300"])
        # The measured artwork is taller than wide; a square clamp would have cut it to 150.
        self.assertGreater(mesh_report(stl)["bounds_mm"][1][1], 149)
