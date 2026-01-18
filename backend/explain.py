import datetime

def explain_step(agent, context_pkg):

    print("="*70)
    print(f"AGENT: {agent['id'].upper()}")
    print("="*70)

    print("ROLE  :", agent["role"])
    print("GOAL  :", agent["goal"])
    print("MODEL :", agent.get("model","gpt"))

    print("\nCONTEXT SEEN")
    print("-"*60)

    if context_pkg["text"]:
        print(context_pkg["text"][:500])
    else:
        print("(no previous context)")

    print("\nNOTE:")
    print(context_pkg["note"])

    print("\nNEXT USE")
    print("- Result flows to next agent")

    print("\nTIME:", datetime.datetime.now().strftime("%H:%M:%S"))