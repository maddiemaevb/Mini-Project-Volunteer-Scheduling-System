#these are tools available for the agent to use
import json 
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "data.json"

#opening the file from the data folder and loading the data into a dictionary
with open(DATA_FILE, "r") as f:
    data = json.load(f)

#extracting volunteers and shifts from the loaded data
volunteers = data.get("volunteers", {})
shifts = data.get("shifts", {})

assignments = {}

#listng the volunteers and their available times
def list_volunteers():
    return volunteers

#listing the shifts that need volunteers
def list_shifts():
    return shifts

#checking if a volunteer is available for a specific shift
def check_availability(volunteer_id, shift_id):
    if volunteer_id not in volunteers or shift_id not in shifts:
        return "Invalid volunteer or shift."

    volunteer = volunteers[volunteer_id]
    shift = shifts[shift_id]

    available_times = volunteer["availability"].get(shift["day"], [])

    for start, end in available_times:
        if start <= shift["start"] and end >= shift["end"]:
            return "Available"

    return "Not available"

#checking for scheduling conflicts for a volunteer and a shift
def check_conflict(volunteer_id, shift_id):
    if volunteer_id not in volunteers or shift_id not in shifts:
        return "Invalid volunteer or shift."

    if shift_id in assignments:
        return "Shift already assigned."

    for assigned_shift_id, assigned_volunteer_id in assignments.items():
        if assigned_volunteer_id != volunteer_id:
            continue

        assigned_shift = shifts[assigned_shift_id]
        new_shift = shifts[shift_id]

        if assigned_shift["day"] != new_shift["day"]:
            continue

        # A conflict exists if the time ranges overlap.
        if (new_shift["start"] < assigned_shift["end"] and
                assigned_shift["start"] < new_shift["end"]):
            return "Scheduling conflict."

    return "No conflict"

#proposing an assignment of a volunteer to a shift if they are available and there are no conflicts
def propose_assignment(volunteer_id, shift_id):
    availability = check_availability(volunteer_id, shift_id)
    conflict = check_conflict(volunteer_id, shift_id)

    if availability == "Available" and conflict == "No conflict":
        assignments[shift_id] = volunteer_id
        return "Assignment successful"

    return f"Assignment failed: {availability}, {conflict}"

#getting the current assignments of volunteers to shifts
def get_assignments():
    return assignments
