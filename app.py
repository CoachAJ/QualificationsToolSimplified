import streamlit as st
import google.generativeai as genai
import pandas as pd

# ==============================================================================
# --- THE NEW "BRAIN" v11.0: THE ALGORITHMIC PROMPT ---
# This prompt is a strict template. The AI's only job is to fill in the blanks
# based on the pre-processed data summary it receives.
# ==============================================================================
SYSTEM_PROMPT_TEMPLATE = """
You are an expert, ruthlessly efficient Youngevity business analyst. Your SOLE task is to complete the following rank advancement blueprint. Adhere to all rules without deviation.

### **Youngevity Rank Advancement Blueprint**

**User:** {user_name} (ID: {user_id})
**Target Rank:** {target_rank}

---
### **1. Initial Assessment & Gap Analysis**

*   **User PQV Status:**
    *   **Requirement:** {user_pqv_req} PQV
    *   **Current:** {user_pqv_current:.2f} PQV
    *   **Gap/Surplus:** {user_pqv_gap:.2f} PQV
    *   **Action Needed:** {user_pqv_action}

*   **Rank Leg Status:**
    *   **Requirement:** {legs_req} Qualified Legs
    *   **Currently Qualified:** {legs_current}
    *   **Gap:** {legs_gap} Legs
    *   **Analysis of Frontline DISTRIBUTORS:**
{frontline_leg_analysis}

*   **Car Bonus Leg Status:**
    *   **Requirement:** 3 Personally Enrolled Distributors with 100+ PQV
    *   **Currently Qualified:** {car_bonus_legs_current}
    *   **Gap:** {car_bonus_legs_gap} Legs
    *   **Analysis of Enrolled DISTRIBUTORS:**
{car_bonus_leg_analysis}

---
### **2. Resource Inventory**

*   **Volume Bank (Resource A):** A total of **{volume_bank_total:.2f} PQV** is available to move from the following frontline PCUST non-autoship orders:
{volume_bank_sources}
*   **Movable Accounts (Resource B):** {movable_accounts_status}
*   **User Surplus Volume (Resource C):** {user_surplus_status}

---
### **3. Prioritized Action Plan**

*Based on the gaps identified above, here is the most resource-efficient plan to achieve the dual goals of **{target_rank}** and the **1SE Car Bonus**.*

**Action #1: {action_1_title}**
- **Justification:** {action_1_justification}
- **Move(s):**
{action_1_moves}

**Action #2: {action_2_title}**
- **Justification:** {action_2_justification}
- **Move(s):**
{action_2_moves}

**Action #3: {action_3_title}**
- **Justification:** {action_3_justification}
- **Move(s):**
{action_3_moves}

*(...continue with more actions as needed...)*

---
### **4. Final Summary & Outcome**

*   **Outcome:** {final_outcome}
*   **Key Insight:** {key_insight}
"""

# ==============================================================================
# --- DATA PRE-PROCESSING & HELPER FUNCTIONS ---
# ==============================================================================

def get_rank_requirements(rank):
    """Returns a dictionary of requirements for a given rank."""
    reqs = {
        "1 Star Executive": {"pqv": 250, "legs": 3, "leg_type": "Qualified Leg"},
        "2 Star Executive": {"pqv": 300, "legs": 3, "leg_type": "1 Star Executive Leg"},
        "3 Star Executive": {"pqv": 300, "legs": 5, "leg_type": "1 Star Executive Leg"},
        "4 Star Executive": {"pqv": 300, "legs": 6, "leg_type": "1 Star Executive Leg"},
        "5 Star Executive": {"pqv": 300, "legs": 9, "leg_type": "1 Star Executive Leg"},
    }
    return reqs.get(rank, {"pqv": 0, "legs": 0, "leg_type": "N/A"})

def analyze_data_for_prompt(gvd_df, agr_df, target_rank):
    """
    Performs a deep, rule-based analysis of the data and formats it perfectly
    for the AI's "fill-in-the-blanks" prompt template.
    """
    try:
        # --- 1. Data Cleaning and Merging ---
        agr_df['ID#'] = agr_df['ID#'].astype(str).str.strip()
        gvd_df['Associate #'] = gvd_df['Associate #'].astype(str).str.strip()
        
        # Calculate total PQV for each person from the volume details
        pqv_summary = gvd_df.groupby('Associate #')['Volume'].sum().reset_index()
        pqv_summary.rename(columns={'Volume': 'PQV'}, inplace=True)

        # Merge the calculated PQV into the genealogy report
        merged_df = pd.merge(agr_df, pqv_summary, left_on='ID#', right_on='Associate #', how='left')
        merged_df['PQV'] = merged_df['PQV'].fillna(0)

        # --- 2. Identify User and Core Gaps ---
        user_row = merged_df[merged_df['Level'] == 0].iloc[0]
        user_id = user_row['ID#']
        rank_reqs = get_rank_requirements(target_rank)
        
        user_pqv_gap = rank_reqs['pqv'] - user_row['PQV']
        user_pqv_action = f"User needs to acquire {user_pqv_gap:.2f} more PQV. This is the first priority." if user_pqv_gap > 0 else "User's PQV requirement is met."

        # --- 3. Analyze Frontline DISTRIBUTORS for Rank Legs ---
        frontline_dist_df = merged_df[(merged_df['Level'] == 1) & (merged_df['Title'] != 'PCUST')]
        legs_qualified_count = 0
        frontline_leg_analysis_text = ""
        for _, dist in frontline_dist_df.iterrows():
            is_self_qualified = dist['PQV'] >= 150
            # Find their direct downline (sponsored by them)
            sub_legs_df = merged_df[merged_df['Sponsor ID'] == dist['ID#']]
            qualified_sub_legs = sub_legs_df[sub_legs_df['PQV'] >= 50].shape[0]
            is_leg_qualified = is_self_qualified and (qualified_sub_legs >= 3)
            
            if is_leg_qualified:
                legs_qualified_count += 1
            
            frontline_leg_analysis_text += (
                f"      - **{dist['Name']} (ID: {dist['ID#']})**: "
                f"PQV: {dist['PQV']:.2f} (Self-Qualified: {'Yes' if is_self_qualified else 'No'}). "
                f"Sub-Legs (50+ PQV): {qualified_sub_legs} of 3. "
                f"**Overall Status: {'QUALIFIED' if is_leg_qualified else 'NOT QUALIFIED'}**\n"
            )

        # --- 4. Analyze Personally Enrolled DISTRIBUTORS for Car Bonus ---
        enrolled_dist_df = merged_df[(merged_df['Enroller'] == user_id) & (merged_df['Title'] != 'PCUST')]
        car_bonus_legs_count = 0
        car_bonus_leg_analysis_text = ""
        for _, dist in enrolled_dist_df.iterrows():
            is_car_leg = dist['PQV'] >= 100
            if is_car_leg:
                car_bonus_legs_count += 1
            car_bonus_leg_analysis_text += f"      - **{dist['Name']} (ID: {dist['ID#']})**: PQV: {dist['PQV']:.2f}. **Status: {'QUALIFIED' if is_car_leg else 'NOT QUALIFIED'}**\n"
        
        # --- 5. Inventory Resources ---
        frontline_pcusts_df = merged_df[merged_df['Level'] == 1] # All frontline to find PCUSTs
        pcust_ids = frontline_pcusts_df[frontline_pcusts_df['Title'] == 'PCUST']['ID#'].tolist()
        volume_bank_df = gvd_df[(gvd_df['Associate #'].isin(pcust_ids)) & (gvd_df['Autoship'] == 'N')]
        
        volume_bank_total = volume_bank_df['Volume'].sum()
        volume_bank_sources_text = "\n".join([
            f"      - Order #{row['Order #']} from {row['Name']} ({row['Volume']:.2f} PQV)" 
            for _, row in volume_bank_df.head(10).iterrows() # Show top 10 sources
        ])

        # (Logic for movable accounts and user surplus would be added here)
        
        # --- 6. Format the final dictionary for the prompt ---
        prompt_data = {
            "user_name": user_row['Name'],
            "user_id": user_id,
            "target_rank": target_rank,
            "user_pqv_req": rank_reqs['pqv'],
            "user_pqv_current": user_row['PQV'],
            "user_pqv_gap": user_pqv_gap,
            "user_pqv_action": user_pqv_action,
            "legs_req": rank_reqs['legs'],
            "legs_current": legs_qualified_count,
            "legs_gap": rank_reqs['legs'] - legs_qualified_count,
            "frontline_leg_analysis": frontline_leg_analysis_text,
            "car_bonus_legs_current": car_bonus_legs_count,
            "car_bonus_legs_gap": 3 - car_bonus_legs_count,
            "car_bonus_leg_analysis": car_bonus_leg_analysis_text,
            "volume_bank_total": volume_bank_total,
            "volume_bank_sources": volume_bank_sources_text,
            "movable_accounts_status": "Not Implemented Yet", # Placeholder
            "user_surplus_status": "Not Implemented Yet"      # Placeholder
            # The AI will be asked to fill in the action plan based on this summary
        }
        return prompt_data

    except Exception as e:
        st.error(f"Error during data analysis: {e}")
        st.exception(e)
        return None

# ==============================================================================
# --- STREAMLIT APPLICATION UI AND LOGIC ---
# ==============================================================================

st.set_page_config(page_title="Youngevity Rank Up Blueprint", page_icon="💡", layout="wide")

st.title("💡 Youngevity Rank Advancement Blueprint")
st.markdown("Your personal AI analyst for strategic business growth. Follow the steps in the sidebar to get your custom action plan.")

if "api_response" not in st.session_state:
    st.session_state.api_response = "### Your Strategic Plan Will Appear Here\n\n*Please fill in all the fields above and click 'Generate Plan' to begin.*"

with st.sidebar:
    st.header("Step 1: Configuration")
    api_key = st.text_input("Enter Your Google AI API Key", type="password", help="Get a free key from Google AI Studio. Your key is not stored or shared.")

    st.header("Step 2: Upload Data")
    uploaded_gvd = st.file_uploader("Upload Group Volume Details CSV", type=['csv'])
    uploaded_agr = st.file_uploader("Upload Advanced Genealogy Report CSV", type=['csv'])

    st.header("Step 3: Define Goal")
    target_rank = st.selectbox("Select Your Target Rank", ("1 Star Executive", "2 Star Executive", "3 Star Executive", "4 Star Executive", "5 Star Executive"))

    generate_button = st.button("Generate Rank Up Plan", type="primary", use_container_width=True)

st.subheader("Your Personalized Action Plan")
st.markdown(st.session_state.api_response, unsafe_allow_html=True)

if generate_button:
    if not api_key or not uploaded_gvd or not uploaded_agr:
        st.error("Please provide your API Key and upload both CSV files.")
        st.stop()

    with st.spinner("Performing deep analysis of your team structure... This may take a moment."):
        try:
            # Load data
            gvd_df = pd.read_csv(uploaded_gvd)
            agr_df = pd.read_csv(uploaded_agr)
            
            # Perform the new, advanced analysis
            prompt_data = analyze_data_for_prompt(gvd_df, agr_df, target_rank)

            if prompt_data:
                # The AI's job is now to fill in the action plan based on our analysis
                # We create a simplified request for the AI
                ai_task_prompt = f"""
                {SYSTEM_PROMPT_TEMPLATE.format(**prompt_data)}

                Based on the pre-calculated analysis above, your task is to fill in the "Prioritized Action Plan" and "Final Summary" sections. 
                
                - Create a logical, step-by-step plan.
                - Justify each choice.
                - Adhere strictly to the "Principle of Minimum Sufficient Action".
                - If the goal is not achievable with the available resources, state that clearly in the final summary.
                """

                # Configure and call the AI
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(ai_task_prompt)
                
                # Check for safety ratings and content
                if response.parts:
                    st.session_state.api_response = response.text
                else:
                    st.session_state.api_response = "### Analysis Blocked\n\nThe AI's response was blocked, possibly due to safety settings. Please try again."
                
                st.rerun() # Rerun to display the new result immediately
            else:
                st.error("Could not generate a plan due to an error in the data analysis phase.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.exception(e)
