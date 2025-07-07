import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Youngevity Rank Up Blueprint",
    page_icon="🚀"
)

# --- The "Brain": The Detailed System Prompt ---
SYSTEM_PROMPT = """
You are an expert business analyst for a network marketing company called Youngevity. Your task is to act as a 'Rank Advancement Simulation Tool'. Your goal is to provide the most EFFICIENT and LOGICALLY sound step-by-step action plan to help a user achieve their target rank and any associated bonuses.

### CORE PRINCIPLES & DEFINITIONS
1.  **PRINCIPLE OF MINIMUM SUFFICIENT ACTION:** Your absolute highest priority is efficiency. Use the smallest amount of resources necessary to meet any single requirement. The moment a distributor or leg meets a requirement (e.g., 150 PQV, 50 PQV sub-leg), STOP allocating resources to them. DO NOT "gold-plate" or make any leg "stronger" if they are already qualified. Immediately move on to the next deficit.
2.  **Distributor vs. PCUST:** A "Leg" for rank advancement can ONLY be built under a frontline **Distributor**. A **PCUST** (Preferred Customer) CANNOT be a leg.
3.  **The "User"**: The main account holder, identified as Level 0 in the genealogy report.

### BUSINESS RESOURCES
1.  **Resource A: "Volume Bank"**: Volume from non-autoship orders belonging to the user's frontline PCUSTs.
2.  **Resource B: "Movable Accounts"**: The entire account of a PCUST personally enrolled by the user within the last 60 days.
3.  **Resource C: "User's Surplus Volume"**: Volume from the user's own orders, ONLY IF the user's remaining Personal Qualifying Volume (PQV) stays above their required minimum.
4.  **Resource D: "Volume Pull-Up"**: If the user's PQV is deficient, volume can be moved from a frontline member's non-autoship order UP to the user.

### UNIVERSAL STRATEGIC PATTERN
The primary strategy is to use the "Volume Bank" (Resource A) to move volume from non-qualifying PCUSTs DOWN to frontline DISTRIBUTORS to meet their PQV goals or to their downline members to create sub-legs.

---
### MULTI-STEP ANALYSIS & JUSTIFICATION (Follow these steps exactly and show your work)

**OUTPUT STEP 1: INITIAL ASSESSMENT & GAP ANALYSIS**
- **State the Core Goal:** "Core Goal: Achieve [Target Rank] for [User Name & ID]."
- **State the Secondary Goal:** "Secondary Goal: Achieve the 1SE Car Bonus."
- **Analyze User PQV:** State the user's current PQV, the requirement, and the deficit. If a deficit exists, state that Action #1 will be to fix it.
- **Analyze Rank Legs:**
    - List every frontline DISTRIBUTOR.
    - For each one, perform a full "Qualified Leg" check (150 PQV self, 3x sub-legs w/ 50 PQV).
    - **Conclusion:** "The user currently has [Y] of 3 required Qualified Legs."
- **Analyze Car Bonus Legs:**
    - List every personally enrolled DISTRIBUTOR.
    - Check if they have 100+ PQV.
    - **Conclusion:** "The user currently has [A] of 3 required Car Bonus Legs."
- **State the Overall Gap:** "Summary of Gaps: User needs [Z] more Rank Legs and [B] more Car Bonus Legs."

**OUTPUT STEP 2: RESOURCE INVENTORY**
- Briefly state the total volume available in the "Volume Bank" and if any "Movable Accounts" are available.

**OUTPUT STEP 3: PRIORITIZED ACTION PLAN**
- **Action #1 (If Necessary): Fix User's PQV:** Detail the "Volume Pull-Up" (Resource D) needed. Justify your choice of source.
- **Action #2 onwards (Constructing Rank & Bonus Legs):**
    - Address the remaining gaps (Rank Legs and Car Bonus Legs) one by one. Prioritize building the rank legs first.
    - **A. State the Target:** "Constructing Rank Leg #[N] (Candidate: [Distributor Name])" or "Qualifying Car Bonus Leg #[M] (Candidate: [Distributor Name])".
    - **B. Justify Your Choice:** Explain *why* you chose this distributor (e.g., "Chosen because they are the most resource-efficient path to qualification.").
    - **C. Detail the MINIMUM Moves:** List the specific, minimal volume moves or account moves needed to meet the requirement. For example, if a sub-leg needs 50 PQV, move exactly 50 PQV if possible, not more.
    - **D. State the Result:** "Result: [Distributor Name] is now a QUALIFIED RANK LEG." or "Result: This distributor now qualifies as a CAR BONUS LEG."
    - **Immediately stop and move to the next gap.**

**OUTPUT STEP 4: FINAL SUMMARY**
- Provide a concise list of all the recommended moves.
- State the final outcome: "By executing this efficient plan, the user will successfully achieve [Target Rank] AND the 1SE Car Bonus."
- If a goal is not possible, state exactly why (e.g., "Goal not achievable: The 'Volume Bank' is insufficient to create the final sub-leg needed.").
"""

# --- App Title and Instructions ---
st.title("🚀 Youngevity Rank Advancement Blueprint")
st.markdown("Your personal AI analyst for strategic business growth. Follow the steps below to get your custom action plan.")

# --- Session State Initialization ---
if "api_response" not in st.session_state:
    st.session_state.api_response = "### Your Strategic Plan Will Appear Here\n\n*Please fill in all the fields above and click 'Generate Plan' to begin.*"

# --- User Interface Components ---
with st.sidebar:
    st.header("Step 1: Configuration")
    api_key = st.text_input("Enter Your Google AI API Key", type="password", help="Get a free key from Google AI Studio. Your key is not stored.")
    
    st.header("Step 2: Upload Your Data")
    uploaded_gvd = st.file_uploader("Upload Group Volume Details CSV", type=['csv'])
    uploaded_agr = st.file_uploader("Upload Advanced Genealogy Report CSV", type=['csv'])

    st.header("Step 3: Define Your Goal")
    target_rank = st.selectbox("Select Your Target Rank", ("1 Star Executive", "2 Star Executive", "3 Star Executive", "4 Star Executive", "5 Star Executive"))

    generate_button = st.button("Generate Rank Up Plan", type="primary", use_container_width=True)

# --- Core Logic ---
if generate_button:
    if not api_key or not uploaded_gvd or not uploaded_agr:
        st.error("Please provide your API Key and upload both CSV files before generating a plan.")
        st.stop()

    with st.spinner("The AI is analyzing your business structure... This may take a moment."):
        try:
            genai.configure(api_key=api_key)
            
            # ** FINAL CORRECTED MODEL NAME **
            model = genai.GenerativeModel('gemini-1.5-flash-latest') 

            gvd_df = pd.read_csv(uploaded_gvd)
            agr_df = pd.read_csv(uploaded_agr)
            gvd_data = gvd_df.to_csv(index=False)
            agr_data = agr_df.to_csv(index=False)

            full_prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Now, analyze the following data for the user:\n\n"
                f"--- START OF Group Volume Details CSV ---\n{gvd_data}\n--- END OF Group Volume Details CSV ---\n\n"
                f"--- START OF Advanced Genealogy Report CSV ---\n{agr_data}\n--- END OF Advanced Genealogy Report CSV ---\n\n"
                f"--- TARGET RANK ---\n{target_rank}\n--- END OF TARGET RANK ---"
            )
            
            # Store the initial prompt for the chat session
            st.session_state.full_initial_prompt = full_prompt
            
            # Clear previous chat messages when generating a new plan
            if "messages" in st.session_state:
                del st.session_state.messages

            response = model.generate_content(full_prompt)
            st.session_state.api_response = response.text

        except Exception as e:
            error_message = (
                "### An Error Occurred\n\n"
                "The analysis could not be completed. Please check the following:\n\n"
                "1.  **Is your API Key correct?** Invalid keys are the most common issue.\n"
                "2.  **Have you enabled the 'Generative Language API' in your Google Cloud project?**\n\n"
                f"**Error Details:**\n```\n{str(e)}\n```"
            )
            st.session_state.api_response = error_message

# --- Display Area ---
st.markdown("---")
st.subheader("Your Personalized Action Plan")
st.markdown(st.session_state.api_response, unsafe_allow_html=True)

# --- Part 2: Interactive Follow-up Chat ---
st.markdown("---")
st.subheader("Got Questions? Refine Your Plan")

# Use session state to store the conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# The user's chat input box
if prompt := st.chat_input("Ask a follow-up question... e.g., 'What if I move volume from X to Y instead?'"):
    # Add user's message to the history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show a spinner while the AI thinks about the follow-up
    with st.spinner("Thinking..."):
        try:
            # Re-initialize the model (important for chat)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Start a chat session with the full history
            chat = model.start_chat(
                history=[
                    {"role": "user", "parts": [st.session_state.get("full_initial_prompt", "")]},
                    {"role": "model", "parts": [st.session_state.get("api_response", "")]}
                ]
            )

            # Send the new follow-up question
            response = chat.send_message(prompt)
            
            # Get the AI's new response
            follow_up_response = response.text
            
            # Add the AI's response to history and display it
            st.session_state.messages.append({"role": "assistant", "content": follow_up_response})
            with st.chat_message("assistant"):
                st.markdown(follow_up_response)

        except Exception as e:
            st.error(f"An error occurred during the follow-up chat: {str(e)}")
