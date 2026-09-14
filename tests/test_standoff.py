"""Checks for the wall standoff: the optics it buys, the price it charges, the parts it makes."""
from pathlib import Path
import re
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_svg import find_openscad, run_scad, mesh_report

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "output" / "standoff_tests"
SOURCE = ROOT / "modular_shadow_lamp.scad"


def setUpModule():
    WORK.mkdir(parents=True, exist_ok=True)


def diagnostics(name, *definitions):
    return run_scad(find_openscad(), SOURCE, WORK / (name + ".csg"),
                    ['Output="Diagnostics"'] + list(definitions))


def part(name, output, *definitions):
    path = WORK / (name + ".stl")
    run_scad(find_openscad(), SOURCE, path, ['Output="%s"' % output] + list(definitions))
    return mesh_report(path)


def number(log, label, index=0):
    match = re.search(re.escape('ECHO: "' + label + '", ') + r"\[([^\]]*)\]", log)
    if not match:
        raise AssertionError(label + " not found in output")
    return float(match.group(1).split(",")[index])


class StandoffOpticsTests(unittest.TestCase):
    def test_source_rises_by_exactly_the_standoff(self):
        """Every mechanical plane moves with the module, so the solution just translates."""
        flush = diagnostics("optics_0", "Wall_standoff=0")
        lifted = diagnostics("optics_20", "Wall_standoff=20")
        self.assertAlmostEqual(number(lifted, "LED centre, wall XYZ mm", 2)
                               - number(flush, "LED centre, wall XYZ mm", 2), 20, places=6)
        # The local height, measured from the module's own back, is unchanged.
        self.assertAlmostEqual(number(lifted, "LED centre, local XYZ mm", 2),
                               number(flush, "LED centre, local XYZ mm", 2), places=6)

    def test_sharper_detail_is_paid_for_with_a_wider_hidden_centre(self):
        """Both halves of the trade-off, so neither can regress unnoticed."""
        previous_cut = previous_dead = 0
        for standoff in (0, 20, 50):
            log = diagnostics("tradeoff_%d" % standoff, "Wall_standoff=%d" % standoff)
            cut = number(log, "Estimated minimum cut / selected minimum mm")
            dead = float(re.search(r'"Central occlusion radius mm", ([-\d.eE]+)', log).group(1))
            self.assertGreater(cut, previous_cut)
            self.assertGreater(dead, previous_dead)
            previous_cut, previous_dead = cut, dead

    def test_a_standoff_reaches_a_length_the_flush_module_cannot(self):
        """The reason the feature exists: 600 mm is out of reach flush, and fine at 50 mm."""
        self.assertIn("BELOW QUALITY LIMITS",
                      diagnostics("reach_flush", "Wall_standoff=0", "Shadow_length=600"))
        self.assertIn("OPTICAL ENVELOPE PASSES",
                      diagnostics("reach_lifted", "Wall_standoff=50", "Shadow_length=600"))

    def test_a_standoff_too_small_for_its_own_image_is_refused(self):
        """50 mm of standoff hides a 200 mm radius, which swallows a 300 mm image."""
        self.assertIn("GENERATION NOT POSSIBLE",
                      diagnostics("reach_swallowed", "Wall_standoff=50", "Shadow_length=300"))


class StandoffPartTests(unittest.TestCase):
    def test_zero_standoff_leaves_the_body_byte_for_byte_alone(self):
        plain = part("body_flush", "Body")
        explicit = part("body_zero", "Body", "Wall_standoff=0")
        self.assertEqual(plain["triangles"], explicit["triangles"])
        self.assertAlmostEqual(plain["signed_volume_mm3"], explicit["signed_volume_mm3"], places=6)

    def test_every_standoff_part_is_one_closed_solid(self):
        parts = {"ring": part("ring", "Standoff", "Wall_standoff=20"),
                 "body_with_ring": part("body_ring", "Body", "Wall_standoff=20"),
                 "extended": part("body_extended", "Body", "Wall_standoff=20",
                                  'Standoff_mode="Extended body"')}
        for name, report in parts.items():
            with self.subTest(part=name):
                self.assertEqual(report["surface_components"], 1)
                self.assertTrue(report["closed_two_manifold_edges"])
                # Everything must sit on the bed as exported.
                self.assertAlmostEqual(report["bounds_mm"][2][0], 0, places=4)
        # The extended body is exactly the standoff taller than the plain one.
        self.assertAlmostEqual(parts["extended"]["bounds_mm"][2][1]
                               - parts["body_with_ring"]["bounds_mm"][2][1], 20, places=3)

    def test_the_compartment_is_hollow_and_vents_through_the_pillar(self):
        """A sealed cavity would show up as a second surface component."""
        solid = part("ring_solid", "Standoff", "Wall_standoff=3", "Standoff_back=3")
        hollow = part("ring_hollow", "Standoff", "Wall_standoff=25", "Standoff_back=3")
        # 22 mm more height, but far less than 22 mm of extra material: it is a shell.
        added = hollow["signed_volume_mm3"] - solid["signed_volume_mm3"]
        self.assertLess(added, 22 * 3.14159 * 50 ** 2 * 0.5)
        self.assertEqual(hollow["surface_components"], 1)

    def test_a_ring_thinner_than_its_own_back_plate_is_refused(self):
        with self.assertRaises(RuntimeError):
            diagnostics("ring_too_thin", "Wall_standoff=1", "Standoff_back=3")

    def test_the_standoff_part_is_refused_when_no_ring_is_configured(self):
        for definitions in (("Wall_standoff=0",),
                            ("Wall_standoff=20", 'Standoff_mode="Extended body"'),
                            ("Wall_standoff=20", "Module_index=1")):
            with self.subTest(definitions=definitions):
                with self.assertRaises(RuntimeError):
                    part("ring_refused", "Standoff", *definitions)


if __name__ == "__main__":
    unittest.main()


class QualityGateTests(unittest.TestCase):
    """Missing a print-quality limit builds and warns; broken geometry still refuses."""

    def status(self, log):
        for marker in ("OPTICAL ENVELOPE PASSES", "BELOW QUALITY LIMITS",
                       "GENERATION NOT POSSIBLE"):
            if marker in log:
                return marker
        raise AssertionError("no status reported")

    def test_a_coarse_but_buildable_request_now_builds(self):
        log = diagnostics("gate_coarse", "Shadow_length=600")
        self.assertEqual(self.status(log), "BELOW QUALITY LIMITS")
        self.assertIn("WARNING: this builds", log)
        report = part("gate_coarse_body", "Body", "Shadow_length=600")
        self.assertEqual(report["surface_components"], 1)
        self.assertTrue(report["closed_two_manifold_edges"])

    def test_refuse_restores_the_old_behaviour(self):
        with self.assertRaises(RuntimeError):
            part("gate_refused", "Body", "Shadow_length=600", 'Quality_limits="Refuse"')

    def test_broken_geometry_refuses_even_in_warn_mode(self):
        cases = {"swallowed": ("Shadow_length=100", "Wall_standoff=100"),
                 "source_below_pillar": ('LED_position="Manual height"', "Manual_LED_height=0")}
        for name, definitions in cases.items():
            with self.subTest(case=name):
                self.assertEqual(self.status(diagnostics("gate_" + name, *definitions)),
                                 "GENERATION NOT POSSIBLE")
                with self.assertRaises(RuntimeError):
                    part("gate_" + name + "_body", "Body", *definitions, 'Quality_limits="Warn"')

    def test_the_warning_names_the_number_that_failed(self):
        log = diagnostics("gate_numbers", "Shadow_length=600")
        self.assertRegex(log, r"smallest cut is [\d.]+ mm against a [\d.]+ mm minimum")

    def test_a_passing_design_says_nothing(self):
        log = diagnostics("gate_pass")
        self.assertEqual(self.status(log), "OPTICAL ENVELOPE PASSES")
        self.assertNotIn("WARNING: this builds", log)
