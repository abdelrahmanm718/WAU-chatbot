import requests
import json

from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("AI_API_URL")
# Send message to API

def send_message(message):
    response = requests.get(API_URL, params={"a": message})
    return response.text

# Domain System Prompts
DOMAIN_PROMPTS = {
    "1": {
        "name": "Computer Science",
        "prompt": """You are Alex, a senior software engineer with 10 years of experience and a passionate CS mentor.
Your goal is to help a student discover if Computer Science is truly their passion — not just a trend they're following.
Ask practical questions, give real-world scenarios, and describe the real daily life of a developer honestly.
React to their answers and dig deeper. After 4-5 exchanges, start forming an opinion about their fit.
Tone: friendly, real, like a mentor over coffee. Not a textbook. Not a robot.
Language: respond in the same language the student uses (Arabic or English)."""
    },
    "2": {
        "name": "Medicine",
        "prompt": """You are Dr. Sara, a doctor with 8 years of experience and a mentor for aspiring medical students.
Your goal is to help a student discover if Medicine is truly their calling — not just family pressure.
Ask about how they feel around sick people, describe real scenarios like long shifts and emotional weight.
Be honest about the sacrifices. React to their answers and adapt accordingly.
Tone: warm, experienced, like a senior doctor giving real advice.
Language: respond in the same language the student uses (Arabic or English)."""
    },
    "3": {
        "name": "Engineering",
        "prompt": """You are Omar, a mechanical engineer turned entrepreneur, passionate about building things.
Your goal is to help a student discover if Engineering is truly where they belong.
Ask if they naturally notice how things work, give real engineering scenarios.
Talk about calculations, project management, physical results you can see.
Tone: direct, practical, energetic. Like a mentor who loves his field.
Language: respond in the same language the student uses (Arabic or English)."""
    },
    "4": {
        "name": "Business & Economics",
        "prompt": """You are Nour, a startup founder and business mentor who studied economics.
Your goal is to help a student discover if Business is truly their world.
Ask if they think about how money flows or how to sell ideas. Give startup scenarios.
Talk about real business life: negotiations, risk, failure, markets, leadership.
Tone: ambitious, sharp, like a mentor who's been through the startup grind.
Language: respond in the same language the student uses (Arabic or English)."""
    }
}

# Behavior Analysis
def analyze_behavior(domain_name, history):
    print("\n⏳ Analyzing your responses...\n")

    # Build conversation text
    conversation = ""
    for msg in history:
        role = "Student" if msg["role"] == "user" else "Mentor"
        conversation += f"{role}: {msg['content']}\n"

    analysis_prompt = f"""You are analyzing a conversation between a student and a mentor in {domain_name}.

Here is the full conversation:
{conversation}

Based on this conversation, evaluate the student and return ONLY a valid JSON object, nothing else. No markdown, no backticks, just raw JSON.

{{
  "passion_score": <number from 0 to 10>,
  "curiosity_level": "<low / medium / high>",
  "fit_for_domain": "<yes / maybe / no>",
  "strengths_observed": ["<strength1>", "<strength2>"],
  "concerns": ["<concern1>"],
  "recommendation": "<1-2 sentences about whether this field suits them>",
  "next_steps": ["<actionable step 1>", "<actionable step 2>", "<actionable step 3>"]
}}"""

    raw = send_message(analysis_prompt).strip()

    try:
        result = json.loads(raw)
        return result
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end != 0:
            try:
                result = json.loads(raw[start:end])
                return result
            except:
                return None
        return None

# Display Analysis Result
def display_analysis(domain_name, result):
    print("\n" + "="*50)
    print(f"📊 WAU ANALYSIS REPORT — {domain_name.upper()}")
    print("="*50)
    print(f"🔥 Passion Score:     {result.get('passion_score')}/10")
    print(f"🔍 Curiosity Level:   {result.get('curiosity_level').upper()}")
    print(f"✅ Fit for Domain:    {result.get('fit_for_domain').upper()}")

    print("\n💪 Strengths Observed:")
    for s in result.get("strengths_observed", []):
        print(f"   • {s}")

    print("\n⚠️  Concerns:")
    for c in result.get("concerns", []):
        print(f"   • {c}")

    print(f"\n💡 Recommendation:\n   {result.get('recommendation')}")

    print("\n🚀 Next Steps:")
    for i, step in enumerate(result.get("next_steps", []), 1):
        print(f"   {i}. {step}")

    print("="*50)

# ─────────────────────────────────────────
# Main Chat Loop
# ─────────────────────────────────────────
def start_chat():
    print("\n" + "="*50)
    print("        Welcome to WAU — Who Are You?")
    print("  Discover your real passion, not just a trend")
    print("="*50)

    print("\nChoose a field to explore:")
    for key, val in DOMAIN_PROMPTS.items():
        print(f"  {key}. {val['name']}")

    choice = input("\nEnter number (1-4): ").strip()

    if choice not in DOMAIN_PROMPTS:
        print("Invalid choice. Please restart.")
        return

    domain = DOMAIN_PROMPTS[choice]
    domain_name = domain["name"]
    system_prompt = domain["prompt"]

    print(f"\n✅ Starting simulation: {domain_name}")
    print("Type 'done' at any time to get your analysis report.")
    print("-"*50 + "\n")

    history = []
    turn_count = 0

    # Mentor opens the conversation
    opening_prompt = f"{system_prompt}\n\nA student just said: Hi, I want to explore this field.\nRespond as the mentor and open the conversation with one question."
    mentor_opening = send_message(opening_prompt)
    print(f"Mentor: {mentor_opening}\n")

    history.append({"role": "user", "content": "Hi, I want to explore this field"})
    history.append({"role": "assistant", "content": mentor_opening})

    # Conversation loop
    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "done":
            break

        # Build context for the API
        conversation_so_far = ""
        for msg in history:
            role = "Student" if msg["role"] == "user" else "Mentor"
            conversation_so_far += f"{role}: {msg['content']}\n"

        full_prompt = f"""{system_prompt}

This is the conversation so far:
{conversation_so_far}
Student: {user_input}

Now respond as the mentor (one reply only, stay in character):"""

        mentor_reply = send_message(full_prompt)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": mentor_reply})

        print(f"\nMentor: {mentor_reply}\n")

        turn_count += 1

        if turn_count == 5:
            print("─"*50)
            print("💬 You've had a good conversation! Type 'done' to get your analysis, or keep going.")
            print("─"*50 + "\n")

    # Run analysis
    if len(history) >= 4:
        result = analyze_behavior(domain_name, history)
        if result:
            display_analysis(domain_name, result)
        else:
            print("⚠️ Could not parse analysis. Raw response was returned.")
    else:
        print("⚠️ Not enough conversation to analyze. Try having at least 3 exchanges.")

if __name__ == "__main__":
    start_chat()