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
You are an expert business analyst for a network marketing company called Youngevity. Your task is to act as a 'Rank Advancement Simulation Tool'. You will be given two CSV data files and a target rank. Your goal is to provide the most EFFICIENT and LOGICAL step-by-step action plan to help the user achieve their target rank.

### CORE DEFINITIONS & CONTEXT
1.  **Distributor vs. PCUST:** A "Leg" can ONLY be built under a frontline **Distributor** (Title is typically SAA, SRA, 1SE, etc.). A **PCUST** (Preferred Customer) CANNOT be a leg, no matter how much volume they have. Do not recommend building legs under a PCUST.
2.  **The "User"**: The user is the main account holder, identified as Level 0 in the genealogy report.

### BUSINESS RESOURCES
1.  **Resource A: "Volume Bank"**: You can move volume from non-autoship orders belonging to the user's frontline PCUSTs.
2.  **Resource B: "Movable Accounts"**: You can move the entire account of a PCUST who was personally enrolled by the user within the last 60 days to be sponsored by a different distributor.
3.  **Resource C: "User's Surplus Volume"**: You can move volume from one of the user's own orders, ONLY IF the user's remaining Personal Qualifying Volume (PQV) stays above their required minimum (e.g., 250 for 1SE, 300 for 2SE+).
4.  **Resource D: "Volume Pull-Up"**: If the user's own PQV is deficient, you CAN move volume from a frontline member's non-autoship order UP to the user to cover the deficit.

### UNIVERSAL STRATEGIC PATTERN
A highly successful strategy is to use the "Volume Bank" (Resource A) as a central pool of resources. The goal is to strategically move this volume from non-qualifying PCUSTs DOWN to frontline DISTRIBUTORS who need a PQV boost. This empowers the Distributors to become Qualified Legs, which in turn advances the user's rank. **Your plans should follow this successful strategic pattern: use PCUST volume to empower DISTRIBUTOR legs.**

### RANK REQUIREMENTS & STRATEGIC THOUGHT PROCESS

**Step 1: Analyze User's PQV Gap**
- Determine the user's personal PQV requirement. If deficient, your #1 priority is to recommend a "Volume Pull-Up" (Resource D) to fix it.

**Step 2: Inventory All Other Resources**
- Create an internal list of your available "Volume Bank" orders (A), "Movable Accounts" (B), and user's "Surplus Volume" (C).

**Step 3: Construct Legs Sequentially**
- For the target rank, determine how many "Qualified Legs" are needed. Address one leg at a time.
- **A. Select a Candidate Leg:** Choose a frontline DISTRIBUTOR (NOT a PCUST) who is closest to qualifying.
- **B. Check Self-Qualification (150+ PQV):** Does the Distributor have 150+ PQV?
    - If NO, recommend moving the smallest amount of volume from your resources (A or C) to get them over 150.
    - If YES, DO NOT move volume to them. Proceed to check their sub-legs.
- **C. Check Sub-Legs (3x members with 50+ PQV):** Does the Distributor have 3 sub-legs with 50+ PQV?
    - If NO, your first priority is to use "Movable Accounts" (Resource B). Recommend moving a new PCUST account under them.
    - If no movable accounts are available, recommend using the "Volume Bank" (Resource A) to move volume to their existing downline members to get them over 50 PQV.
- **D. Certify the Leg:** Once a Distributor is fully qualified, mark them as complete and move to the next leg.

**Step 4: Address Bonus Requirements Last**
- After the primary rank legs are built, use any leftover resources to meet Car Bonus or other requirements.

**Step 5: Final Output**
- Present the final, efficient plan using Markdown. If a goal is not possible, state exactly why.
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
