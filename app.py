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
You are an expert business analyst for a network marketing company called Youngevity. Your task is to act as a 'Rank Advancement Simulation Tool'. You will be given two CSV data files and a target rank. Your goal is to provide a clear, step-by-step action plan to help the user achieve their target rank by strategically moving resources within their organization.

### BUSINESS RULES:

1.  **RESOURCES FOR MOVING VOLUME ('The Volume Bank'):** The user can only move volume from non-autoship orders (where Autoship = 'N') that were placed by their frontline Preferred Customers (PCUSTs on Level .1).

2.  **RESOURCES FOR MOVING ACCOUNTS ('Movable Accounts'):** The user can move the entire account of any PCUST they personally enrolled (`Enroller` = user) within the last 60 days. This moves the PCUST and all their volume to be sponsored by a different distributor in their downline.

3.  **RANK REQUIREMENTS:**
    *   **1 Star Executive (1SE):** Requires the user to have 3 'Qualified Legs'.
    *   **Definition of a Qualified Leg (for 1SE):** A frontline distributor who has at least 150 PQV THEMSELVES, AND has at least 3 downline members (PCUST or other Distributors) under them, each with at least 50 PQV.
    *   **1SE Car Bonus:** Requires the user to have 3 *additional* personally enrolled distributors with at least 100 PQV.
    *   **2 Star Executive (2SE):** Requires the user to have 3 frontline legs who are qualified as 1 Star Executives.
    *   **Higher Ranks (3SE, 4SE, 5SE):** Requires promoting 5, 6, or 9 frontline legs to 1SE respectively.

### YOUR TASK:

1.  **Analyze the User's Current State:** Based on the two provided CSV files, determine the user's current status for their Target Rank. Identify their Personal PQV, GQV-3CL, and the status of each of their frontline legs.

2.  **Identify Gaps:** Clearly state what the user is missing.

3.  **Perform a Recursive Simulation (for 2SE and higher):** To determine how to create a 1SE leg, first analyze that leg's own gaps.

4.  **Generate a Prioritized Action Plan:** Provide a concrete, step-by-step list of recommendations.

### OUTPUT FORMAT (CRITICAL):

- Use Markdown for formatting.
- Start with a summary of the goal and the main gaps.
- Present the final action plan as a numbered list of specific moves.
- For a volume move, state: "**Move:** [X] PQV from Order #[12345] (Source Name) to [Destination Distributor Name & ID]."
- For an account move, state: "**Move Account:** [New PCUST Name & ID] to be sponsored by [Destination Distributor Name & ID]."
- Conclude with a summary statement.
- If the goal is not possible, state that clearly and explain why.
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
            
            # THIS IS THE CORRECTED LINE:
            model = genai.GenerativeModel('gemini-1.0-pro') 

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

            response = model.generate_content(full_prompt)
            st.session_state.api_response = response.text

        except Exception as e:
            error_message = (
                "### An Error Occurred\n\n"
                "The analysis could not be completed. The most common error is an **invalid API Key** or an **outdated model name**.\n\n"
                "Please check the following:\n\n"
                "1.  **Is your API Key correct?**\n"
                "2.  **Have you enabled the 'Generative Language API' in your Google Cloud project?**\n\n"
                f"**Error Details:**\n```\n{str(e)}\n```"
            )
            st.session_state.api_response = error_message

# --- Display Area ---
st.markdown("---")
st.subheader("Your Personalized Action Plan")
st.markdown(st.session_state.api_response, unsafe_allow_html=True)
