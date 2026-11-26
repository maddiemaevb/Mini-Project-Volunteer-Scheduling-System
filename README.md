Volunteer shift planning agent

Name: Madison Van Buren


Overview: This volunteer shift planning agent helps a non-profit organization assign volunteers to shifts.

The project uses Qwen 8B running locally through Ollama in order to make decisions on scheduling. The language model uses python tools to inspect volunteer availability and check for scheduling conflicts and propose assignments.

The project uses a small dataset consisting of 5 fictional volunteers and 3 shifts keeping the problem manageable.


Tools:
list_volunteers() : retrieves volunteer names and availabilty
list_shifts() : retrieves the shifts requiring volunteers
check_availability() : checks whether a volunteer can cover an entire shift
check_conflict() : checks whether an assignment would cause a scheduling conflict
propose_assignment() : attempts to assign a volunteer to a shift
get_assignments() : retrieves the current accepted assignments


Setup:
Make sure to have ollama installed: ollama pull qwen3:8b
Install python dependency: python -m pip install openai

Run the agent using: python agent.py

Test it by running: python -m unittest discover -s tests -v

Example results for running agent.py should be: 
SHIFT                   ASSIGNED VOLUNTEER                  STATUS
s1 - food pantry            Alex - v1                      verified
s2 - donation sorting      Jordan - v2                     verified
s3 - evening cleanup       Unassigned                     unverified