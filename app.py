import streamlit as st
import google.generativeai as genai
import pandas as pd

# ==============================================================================
# --- KNOWLEDGE BASE: REFERENCE DOCUMENT TEXT ---
# ==============================================================================
# This section contains the official Youngevity documentation that the AI will reference

COMPENSATION_PLAN_TEXT = """
GLOBAL RESIDUAL COMPENSATION PLAN

QUALIFICATIONS
- Must be an active Youngevity Distributor
- Must maintain minimum Personal Qualifying Volume (PQV) requirements
- Must meet specific rank advancement criteria

COMPENSATION PLAN SUMMARY
- Multiple ways to earn including retail profits, unilevel commissions, and bonuses
- Rank advancement based on personal volume and team building
- Special bonuses for fast starts and team building
"""

GLOSSARY_TEXT = """
MEMBERSHIP AFFILIATION TYPES:
- Retail Customer: Purchases at retail prices, not enrolled
- Preferred Customer: Enjoys wholesale pricing, not a business builder
- Distributor: Can build a business and earn commissions

VOLUME TYPES:
- PQV: Personal Qualifying Volume - counts toward rank advancement
- GQV: Group Qualifying Volume - team volume that counts toward rank
- BV: Bonus Volume - used to calculate commission payouts
"""

POLICIES_TEXT = """
POLICIES & PROCEDURES

1. CODE OF ETHICS
- Conduct business with integrity
- Make no misleading income claims
- Follow all company policies and procedures

2. SPONSORING
- Must properly train and support downline
- Cannot engage in cross-line recruiting
- Must provide accurate business information

3. COMPLIANCE
- Must follow all applicable laws and regulations
- Must submit required documentation
- Must maintain good standing with the company
"""

# ==============================================================================
# --- THE AI "BRAIN": THE SYSTEM PROMPT ---
# ==============================================================================
SYSTEM_PROMPT = f"""
You are an expert business analyst for Youngevity, a network marketing company. Your task is to act as a 'Rank Advancement Simulation Tool'. Your goal is to provide a meticulously detailed, efficient, and LOGICALLY FLAWLESS step-by-step action plan based on the official company documents and the user's current data.

---
### OFFICIAL KNOWLEDGE BASE (Source of Truth)
Before you do anything, you MUST consult this knowledge base. The rules and definitions here override any prior knowledge.

**1. Official Compensation Plan:**
{COMPENSATION_PLAN_TEXT}

**2. Official Glossary of Terms:**
{GLOSSARY_TEXT}

**3. Official Policies & Procedures:**
{POLICIES_TEXT}

### CORE DEFINITIONS & UNBREAKABLE RULES
1. **DATA UNIFICATION RULE (CRITICAL FIRST STEP):** Before any analysis, you MUST mentally join the two data sources. The 'ID#' column in 'AdvancedGenealogyReport.csv' corresponds to the 'Associate #' column in 'Group Volume Details.csv'.

2. **DISTRIBUTOR CLASSIFICATION:** After unifying the data, classify each person:
   - If 'Title' is 'PCUST' → CUSTOMER (cannot be a leg)
   - If 'Title' is anything else (SAA, SRA, 1SE, BRA, DIST, etc.) → DISTRIBUTOR (can be a leg)

3. **PRINCIPLE OF MINIMUM SUFFICIENT ACTION:** Use the smallest amount of resources necessary to meet requirements. Once a distributor or leg is qualified, STOP allocating resources to them.

4. **VOLUME SOURCE:** All volume data comes from the 'Volume' column in 'Group Volume Details.csv'.

### BUSINESS RESOURCES
1. **Volume Bank:** Non-autoship orders from frontline PCUSTs
2. **Movable Accounts:** PCUST accounts enrolled within last 60 days
3. **User's Surplus Volume:** User's excess volume above rank requirements
4. **Volume Pull-Up:** Move volume from frontline members to user if needed

### RANK REQUIREMENTS
* **1 Star Executive (1SE):** 250 PQV + 3 Qualified Legs
* **Qualified Leg:** Frontline Distributor with 150+ PQV AND 3 downline members with 50+ PQV each
* **1SE Car Bonus:** 3 additional personally enrolled Distributors with 100+ PQV each

---
### MULTI-STEP ANALYSIS & JUSTIFICATION

**OUTPUT STEP 1: INITIAL ASSESSMENT & GAP ANALYSIS**
- **State the Goal:** "Core Goal: Achieve 1 Star Executive for [User Name]." and "Secondary Goal: Achieve the 1SE Car Bonus."
- **Analyze User PQV:** State the user's current total PQV (summed from Group Volume Details), the 250 PQV requirement, and the deficit/surplus.
- **Analyze Frontline Legs:**
    - Using the unified data, list every frontline **DISTRIBUTOR**.
    - For each Distributor, perform a full "Qualified Leg" check (150+ PQV, 3x sub-legs w/ 50+ PQV).
    - Conclude: "The user currently has [Y] of 3 required Qualified Legs."
- **Analyze Car Bonus Legs:**
    - Using the unified data, list every personally enrolled **DISTRIBUTOR**.
    - Check if they have 100+ PQV.
    - Conclude: "The user currently has [A] of 3 required Car Bonus Legs."
- **State the Overall Gap:** "Summary of Gaps: User needs [Z] more Rank Legs and [B] more Car Bonus Legs."

**OUTPUT STEP 2: RESOURCE INVENTORY**
- Briefly state the total volume available in the "Volume Bank" and if any "Movable Accounts" are available.

**OUTPUT STEP 3: PRIORITIZED ACTION PLAN**
- **Action #1 (If Necessary): Fix User's PQV:** Detail the "Volume Pull-Up" (Resource D) needed.
- **Action #2 onwards (Constructing Legs):**
    - For each leg you need to build, create a dedicated section.
    - **A. State the Target:** "Constructing Rank Leg #[N] (Candidate: [Distributor Name])". Justify your choice based on efficiency (who is closest to qualifying).
    - **B. Detail the MINIMUM Moves:** List the specific, minimal moves needed to get this leg fully qualified.
    - **C. State the Result:** "Result: [Distributor Name] is now a QUALIFIED RANK LEG."
    - **Immediately stop and move to the next gap.**

**OUTPUT STEP 4: FINAL SUMMARY**
- Provide a concise list of all the recommended moves.
- State the final outcome. If a goal is not possible, state exactly why.
"""

# --- Page Configuration ---
st.set_page_config(
    page_title="Youngevity Rank Up Blueprint",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- App Title and Instructions ---
st.title("🚀 Youngevity Rank Advancement Blueprint")
st.markdown("""
Your personal AI analyst for strategic business growth. Follow these steps:
1. Enter your Google AI API key (get one from [Google AI Studio](https://aistudio.google.com/))
2. Upload your Group Volume Details and Advanced Genealogy Report CSVs
3. Select your target rank and generate your custom action plan
""")

# --- Session State Initialization ---
if "api_response" not in st.session_state:
    st.session_state.api_response = "### Your Strategic Plan Will Appear Here\n\n*Please fill in all the fields above and click 'Generate Plan' to begin.*"

# --- User Interface Components ---
with st.sidebar:
    with st.expander("🔑 Step 1: API Configuration", expanded=True):
        st.caption("You'll need a Google AI API key to use this tool.")
        api_key = st.text_input(
            "Enter Your Google AI API Key",
            type="password",
            help="Get a free key from Google AI Studio. Your key is not stored and is only used for this session.",
            placeholder="AIzaSy..."
        )
    
    with st.expander("📊 Step 2: Upload Your Data", expanded=True):
        st.caption("Upload both CSV files to analyze your network.")
        uploaded_gvd = st.file_uploader(
            "Group Volume Details CSV",
            type=['csv'],
            help="This file contains volume details for all associates in your organization."
        )
        uploaded_agr = st.file_uploader(
            "Advanced Genealogy Report CSV",
            type=['csv'],
            help="This file contains the hierarchical relationship data of your organization."
        )

    with st.expander("🎯 Step 3: Set Your Goal", expanded=True):
        st.caption("Select the rank you're working towards.")
        target_rank = st.selectbox(
            "Target Rank",
            ("1 Star Executive", "2 Star Executive", "3 Star Executive", "4 Star Executive", "5 Star Executive"),
            index=0,
            help="The rank you want to achieve next."
        )

    generate_button = st.button(
        "🚀 Generate Rank Up Plan",
        type="primary",
        use_container_width=True,
        help="Click to analyze your data and generate a customized action plan."
    )
    
    st.markdown("---")
    st.caption("💡 Tip: After generating your plan, use the chat below to ask follow-up questions!")

# --- Core Logic ---
if generate_button:
    if not api_key or not uploaded_gvd or not uploaded_agr:
        st.error("❌ Please provide your API Key and upload both CSV files before generating a plan.")
        st.stop()

    with st.spinner("🔍 The AI is analyzing your business structure... This may take a moment."):
        try:
            # Configure the API
            genai.configure(api_key=api_key)
            
            # Initialize the model with the latest version
            model = genai.GenerativeModel('gemini-1.5-flash-latest')

            # Read and validate the CSV files
            try:
                gvd_df = pd.read_csv(uploaded_gvd)
                agr_df = pd.read_csv(uploaded_agr)
                
                # Check for required columns
                required_gvd_columns = ['Associate #', 'PQV', 'Volume']
                required_agr_columns = ['ID#', 'Title', 'Enroller ID']
                
                missing_gvd = [col for col in required_gvd_columns if col not in gvd_df.columns]
                missing_agr = [col for col in required_agr_columns if col not in agr_df.columns]
                
                if missing_gvd or missing_agr:
                    error_msg = "❌ Error: Missing required columns in "
                    if missing_gvd:
                        error_msg += f"Group Volume Details: {', '.join(missing_gvd)}. "
                    if missing_agr:
                        error_msg += f"Advanced Genealogy Report: {', '.join(missing_agr)}. "
                    error_msg += "Please check your CSV files and try again."
                    st.error(error_msg)
                    st.stop()
                
                gvd_data = gvd_df.to_csv(index=False)
                agr_data = agr_df.to_csv(index=False)
                
            except Exception as e:
                st.error(f"❌ Error reading CSV files: {str(e)}. Please check the file format and try again.")
                st.stop()

            # Create the full prompt with the data
            full_prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Now, analyze the following data for the user targeting {target_rank}:\n\n"
                f"--- START OF Group Volume Details CSV (First 5 rows) ---\n{gvd_df.head().to_string()}\n...\n--- END OF Group Volume Details CSV ---\n\n"
                f"--- START OF Advanced Genealogy Report CSV (First 5 rows) ---\n{agr_df.head().to_string()}\n...\n--- END OF Advanced Genealogy Report CSV ---"
            )
            
            # Store the initial prompt and raw data for the chat session
            st.session_state.full_initial_prompt = full_prompt
            st.session_state.raw_data = {
                'gvd': gvd_data,
                'agr': agr_data,
                'target_rank': target_rank
            }
            
            # Clear previous chat messages when generating a new plan
            if "messages" in st.session_state:
                del st.session_state.messages

            # Generate the response
            response = model.generate_content(full_prompt)
            
            # Store the response
            if response.text:
                st.session_state.api_response = response.text
                st.session_state.last_analysis_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success("✅ Analysis complete!")
            else:
                st.error("❌ The AI response was empty. Please try again.")

        except Exception as e:
            error_message = (
                "### ❌ Error: Analysis Failed\n\n"
                "The analysis could not be completed. Here's what might be wrong:\n\n"
                "1. **API Key Issues**: Make sure your Google AI API key is valid and has access to the Gemini API.\n"
                "2. **API Quota**: Check if you've exceeded your API quota or if the service is temporarily unavailable.\n"
                "3. **Data Format**: Verify that your CSV files match the expected format.\n"
                "4. **Network Issues**: Check your internet connection.\n\n"
                f"**Technical Details:**\n```\n{str(e)}\n```\n\n"
                "If the problem persists, please try again later or contact support."
            )
            st.session_state.api_response = error_message
            st.error("An error occurred during analysis. Please see the detailed error message above.")

# --- Display Area ---
st.markdown("---")

# Create two columns for the main content and sidebar
main_col, side_col = st.columns([0.7, 0.3])

with main_col:
    st.subheader("📋 Your Personalized Action Plan")
    
    # Add a status indicator
    if "api_response" in st.session_state and not st.session_state.api_response.startswith("### Your Strategic Plan"):
        st.success("✅ Analysis complete! Review your plan below.")
    
    # Display the main AI response
    with st.container(border=True):
        st.markdown(st.session_state.api_response, unsafe_allow_html=True)
    
    # Add a refresh button
    if st.button("🔄 Regenerate Plan", type="secondary"):
        st.rerun()

with side_col:
    st.subheader("📊 Quick Stats")
    with st.container(border=True, height=200):
        st.markdown("""
        - **Target Rank:** *Not set*
        - **PQV Required:** *Calculating...*
        - **Legs Needed:** *Calculating...*
        - **Car Bonus Legs:** *Calculating...*
        """)
    
    st.markdown("---")
    st.subheader("📚 Help & Resources")
    with st.container(border=True):
        st.page_link("https://www.youngevity.com", label="🌐 Youngevity Official Site", icon="")
        st.page_link("https://aistudio.google.com", label="🔑 Get API Key", icon="")
        st.page_link("https://youngevity.com/compensation-plan/", label="📈 View Full Compensation Plan", icon="")

# --- Interactive Follow-up Chat ---
st.markdown("---")
st.subheader("💬 Need Clarification? Ask Me Anything")
st.caption("Ask follow-up questions about your plan, like 'How can I qualify Leg #2 faster?' or 'What if I move volume from X to Y?'")

# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type your question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show a spinner while the AI generates a response
    with st.spinner("Analyzing your question..."):
        try:
            # Initialize the model
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Prepare the chat history with context
            chat_history = [
                {"role": "user", "parts": [st.session_state.get("full_initial_prompt", "")]},
                {"role": "model", "parts": [st.session_state.get("api_response", "")]}
            ]
            
            # Add previous chat messages to the context
            for msg in st.session_state.messages[:-1]:  # Exclude the current message
                chat_history.append({"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]})
            
            # Start a chat session with the full history
            chat = model.start_chat(history=chat_history)
            
            # Get the AI's response
            response = chat.send_message(prompt)
            
            # Get the AI's response text
            follow_up_response = response.text
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": follow_up_response})
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(follow_up_response)
                
            # Add a small delay for better UX
            import time
            time.sleep(0.5)

        except Exception as e:
            error_msg = f"⚠️ Sorry, I encountered an error: {str(e)}. Please check your API key and try again."
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Add a clear chat button
if st.session_state.messages:
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# --- Footer ---
st.markdown("---")
footer = """
<div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 2em;">
    <p>Youngevity Rank Up Blueprint v1.0.0 | 
    <a href="https://www.youngevity.com/privacy-policy" target="_blank">Privacy Policy</a> | 
    <a href="https://www.youngevity.com/terms" target="_blank">Terms of Service</a></p>
    <p>This tool is not affiliated with Youngevity International, Inc. All product and company names are trademarks™ or registered® trademarks of their respective holders.</p>
    <p>Having issues? <a href="mailto:support@example.com?subject=Rank%20Up%20Blueprint%20Feedback">Contact Support</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
