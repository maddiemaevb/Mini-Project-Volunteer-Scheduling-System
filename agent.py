
import json
from openai import OpenAI
import scheduler

#connect to the locally running Qwen model
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

MODEL = "qwen3:8b"

#python tools available to the AI agent
functions = {
    "list_volunteers": scheduler.list_volunteers,
    "list_shifts": scheduler.list_shifts,
    "check_availability": scheduler.check_availability,
    "check_conflict": scheduler.check_conflict,
    "propose_assignment": scheduler.propose_assignment,
    "get_assignments": scheduler.get_assignments
}

#describe the tools to the language model
tools = []

for name in functions:
    needs_ids = name in [
        "check_availability",
        "check_conflict",
        "propose_assignment"
    ]

    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    if needs_ids:
        parameters["properties"] = {
            "volunteer_id": {"type": "string"},
            "shift_id": {"type": "string"}
        }
        parameters["required"] = [
            "volunteer_id",
            "shift_id"
        ]

    tools.append({
        "type": "function",
        "function": {
            "name": name,
            "description": {
                "list_volunteers": "List volunteers and their available times.",
                "list_shifts": "List shifts that need volunteers.",
                "check_availability": "Check if a volunteer is available for a shift.",
                "check_conflict": "Check for scheduling conflicts.",
                "propose_assignment": "Attempt to assign a volunteer to a shift.",
                "get_assignments": "Show currently accepted assignments."
            }[name],
            "parameters": parameters
        }
    })


def run_agent():
    #clear assignments before starting
    scheduler.assignments.clear()

    messages = [
        {
            "role": "system",
            "content": """
You are an autonomous volunteer scheduling agent.

Your job is to assign volunteers to all three shifts.

You must complete the scheduling process before giving
your final response.

Follow these rules:

1. First, inspect the volunteers and shifts.
2. For each shift, select a volunteer to investigate.
3. Use check_availability to verify their availability.
4. Use check_conflict to check for scheduling conflicts.
5. If both checks pass, use propose_assignment.
6. If a volunteer is unavailable or the assignment fails,
   try another volunteer.
7. If nobody can cover a shift, report it as unfilled.
8. Continue until all three shifts have been considered.
9. Use get_assignments to review accepted assignments.
10. Only then provide a final summary.

You must make the decisions about which volunteers to try.
Do not assume a volunteer is available without checking.
Do not claim an assignment succeeded unless the tool confirms it.
"""
        },
        {
            "role": "user",
            "content": "Plan volunteer assignments for all three shifts."
        }
    ]

    print("\n=== VOLUNTEER PLANNING AGENT ===")

    #allow the model to make multiple decisions
    for step in range(30):

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        #handles a response without tool calls
        if not message.tool_calls:

            #if Qwen returns nothing, ask it to continue
            if not message.content or not message.content.strip():
                print("\nModel returned an empty response. Retrying...")

                messages.append({
                    "role": "user",
                    "content": (
                        "You have not finished the task. "
                        "Continue using the available tools to assign "
                        "volunteers to all three shifts. "
                        "If a shift cannot be filled, report why."
                    )
                })

                continue

            print("\n=== AGENT FINAL RESPONSE ===")
            print(message.content)
            break

        #save the model's tool requests
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                call.model_dump()
                for call in message.tool_calls
            ]
        })

        #execute each tool requested by the model
        for call in message.tool_calls:
            name = call.function.name

            try:
                arguments = json.loads(
                    call.function.arguments or "{}"
                )

                if name not in functions:
                    raise ValueError("Unknown tool")

                result = functions[name](**arguments)

            except Exception as error:
                result = f"Tool error: {error}"

            print(f"\nTOOL: {name}")
            print(f"ARGUMENTS: {call.function.arguments}")
            print(f"RESULT: {result}")

            #return the observation to the model
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)
            })

    else:
        print("\nAgent reached the tool-call limit.")

    #display assignments and independently check the availability
    print("\n=== VERIFIED ASSIGNMENTS ===")

    for shift_id, shift in scheduler.shifts.items():
        volunteer_id = scheduler.assignments.get(shift_id)

        if volunteer_id is None:
            print(f"{shift_id}: UNFILLED")
            continue

        volunteer = scheduler.volunteers[volunteer_id]

        availability = scheduler.check_availability(
            volunteer_id, shift_id
        )

        status = (
            "VERIFIED" if availability == "Available"
            else "INVALID"
        )

        print(
            f"{shift_id}: {volunteer['name']} - {status}"
        )


if __name__ == "__main__":
    run_agent()
