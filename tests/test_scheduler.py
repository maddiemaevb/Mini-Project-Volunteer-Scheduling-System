import unittest
import scheduler


class TestScheduler(unittest.TestCase):
    def setUp(self):
        #clear assignments before each test
        scheduler.assignments.clear()

    def tearDown(self):
        #clear assignments after each test
        scheduler.assignments.clear()
        scheduler.shifts.pop("S4", None)

    #test 1: list volunteers
    def test_list_volunteers(self):
        volunteers = scheduler.list_volunteers()

        self.assertIsInstance(volunteers, dict)
        self.assertEqual(len(volunteers), 5)
        self.assertIn("V1", volunteers)

    #test 2: list shifts
    def test_list_shifts(self):
        shifts = scheduler.list_shifts()

        self.assertIsInstance(shifts, dict)
        self.assertEqual(len(shifts), 3)
        self.assertIn("S1", shifts)

    #test 3: available volunteer
    def test_available_volunteer(self):
        result = scheduler.check_availability("V1", "S1")

        self.assertEqual(result, "Available")

    #test 4: unavailable volunteer
    def test_unavailable_volunteer(self):
        result = scheduler.check_availability("V2", "S1")

        self.assertEqual(result, "Not available")

    #test 5: no scheduling conflict
    def test_no_conflict(self):
        result = scheduler.check_conflict("V1", "S1")

        self.assertEqual(result, "No conflict")

    #test 6: successful assignment
    def test_successful_assignment(self):
        result = scheduler.propose_assignment("V1", "S1")

        self.assertEqual(result, "Assignment successful")
        self.assertEqual(scheduler.assignments["S1"], "V1")

    #test 7: reject unavailable volunteer
    def test_unavailable_assignment(self):
        result = scheduler.propose_assignment("V5", "S3")

        self.assertIn("Assignment failed", result)
        self.assertNotIn("S3", scheduler.assignments)

    #test 8: prevent double booking a shift
    def test_shift_already_assigned(self):
        scheduler.propose_assignment("V1", "S1")

        result = scheduler.propose_assignment("V4", "S1")

        self.assertIn("Shift already assigned", result)

    #test 9: prevent overlapping shifts
    def test_overlapping_shifts(self):
        scheduler.shifts["S4"] = {
            "name": "Temporary Test Shift",
            "day": "Monday",
            "start": 10,
            "end": 12
        }

        scheduler.propose_assignment("V4", "S1")

        result = scheduler.propose_assignment("V4", "S4")

        self.assertIn("Scheduling conflict", result)
        self.assertNotIn("S4", scheduler.assignments)

    #test 10: allow non-overlapping shifts
    def test_non_overlapping_shifts(self):
        result1 = scheduler.propose_assignment("V4", "S1")
        result2 = scheduler.propose_assignment("V4", "S2")

        self.assertEqual(result1, "Assignment successful")
        self.assertEqual(result2, "Assignment successful")

    #test 11: invalid volunteer
    def test_invalid_volunteer(self):
        result = scheduler.check_availability("V99", "S1")

        self.assertEqual(result, "Invalid volunteer or shift.")

    #test 12: invalid shift
    def test_invalid_shift(self):
        result = scheduler.propose_assignment("V1", "S99")

        self.assertIn("Assignment failed", result)
        self.assertEqual(scheduler.assignments, {})

    #test 13: retrieve assignments
    def test_get_assignments(self):
        scheduler.propose_assignment("V1", "S1")

        assignments = scheduler.get_assignments()

        self.assertIsInstance(assignments, dict)
        self.assertEqual(assignments, {"S1": "V1"})

    #test 14: nobody available for evening shift
    def test_evening_shift_unavailable(self):
        for volunteer_id in scheduler.volunteers:
            result = scheduler.check_availability(
                volunteer_id, "S3"
            )

            self.assertEqual(result, "Not available")


if __name__ == "__main__":
    unittest.main()
