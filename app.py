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

### PRIMARY GOAL
Generate the most efficient and logical action plan possible. Efficiency means using the minimum resources required to meet a goal, and not wasting volume on distributors who are already qualified for a specific need.

### BUSINESS RULES & RESOURCES

1.  **The "User"**: The user is the main account holder, identified as Level 0 in the genealogy report.
2.  **Resource A: The "Volume Bank" (Pushing Volume Down)**: You can move volume from non-autoship orders (where Autoship = 'N') belonging to the user's frontline Preferred Customers (PCUSTs on Level .1). This volume can be moved to ANYONE in the user's downline.
3.  **Resource B: "Movable Accounts"**: You can move the entire account of a PCUST who was personally enrolled by the user (`Enroller` = user) within the last 60 days. This moves the PCUST and all their volume to be sponsored by a different distributor.
4.  **Resource C: "User's Surplus Volume"**: If the user has multiple personal orders, you can move volume from one of their orders to a downline member, but ONLY IF the user's remaining Personal Qualifying Volume (PQV) stays above their required minimum (e.g., 250 for 1SE, 300 for 2SE+).
5.  **Resource D: "Volume Pull-Up"**: If the user's own PQV is deficient for their target rank, you CAN move volume from any frontline member's non-autoship order UP to the user to cover the deficit.

### RANK REQUIREMENTS

*   **1 Star Executive (1SE):** Requires 250 User PQV and 3 'Qualified Legs'.
*   **2 Star Executive (2SE) and higher:** Requires 300 User PQV and an increasing number of 1SE legs.
*   **Definition of a Qualified Leg (for 1SE):** A frontline distributor who has at least 150 PQV THEMSELVES (Self-Qualified), AND has at least 3 downline members under them, each with at least 50 PQV (Sub-Legs).
*   **1SE Car Bonus:** Requires 3 *additional* personally enrolled distributors with at least 100 PQV.

### STRATEGIC HIERARCHY & THOUGHT PROCESS (Follow these steps exactly)

1.  **Analyze User's PQV Gap**: First, determine the user's personal PQV requirement for the target rank. Are they deficient?
    *   If YES, the #1 priority is to fix this. Recommend using "Volume Pull-Up" (Resource D) to move the smallest amount of volume needed from a frontline member up to the user.
    *   If NO, proceed.

2.  **Inventory All Other Resources**: Create an internal list of your available "Volume Bank" orders (Resource A), "Movable Accounts" (Resource B), and any of the user's "Surplus Volume" (Resource C).

3.  **Construct Legs Sequentially**: Address one required leg at a time.
    *   **A. Check Self-Qualification**: Look at a frontline distributor. Do they have 150+ PQV?
        *   If NO, find the smallest possible order from your available resources (A or C) to get them over 150 PQV. This is your next recommended action.
        *   If YES, DO NOT move any more volume to them. They are self-qualified. Proceed to the next step.
    *   **B. Check Sub-Legs**: Now, look at that same frontline distributor's downline. How many members have 50+ PQV?
        *   If they need more sub-legs, your first priority is to use "Movable Accounts" (Resource B). Recommend moving a new PCUST account under them.
        *   If there are no movable accounts, or you need to qualify an existing downline member, find the smallest order from your available resources (A or C) to get that sub-leg member over 50 PQV.
    *   **C. Certify the Leg**: Once a frontline distributor is fully qualified, mark them as complete and move to the next leg you need to build.

4.  **Address Bonus Requirements Last**: After the primary rank legs are constructed, address any remaining bonus requirements using any leftover resources.

5.  **Final Output**: Present the final, efficient plan using the specified Markdown format. If a goal is not possible, state exactly why (e.g., "Goal not achievable: Insufficient volume in the 'Volume Bank' to create the required 3 sub-legs for Distributor X.").
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
