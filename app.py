import streamlit as st
import google.generativeai as genai
import pandas as pd

# ==============================================================================
# --- KNOWLEDGE BASE: REFERENCE DOCUMENT TEXT ---
# ==============================================================================
# This section contains the official Youngevity documentation that the AI will reference

COMPENSATION_PLAN_TEXT = """
GLOBAL RESIDUAL COMPENSATION PLAN

1. EARNING OPPORTUNITIES:
   - Retail Profits: 20-50% markup on product sales
   - Unilevel Commissions: 5-20% on 7-10 levels deep
   - Fast Start Bonuses: $50-500 for new enrollments
   - Rank Advancement Bonuses: $100-10,000
   - Leadership Pools: 2-5% of company volume
   - Car Bonus: $500-1,500/month for qualified executives
   - Luxury Trips: All-expense paid vacations

2. RANK ADVANCEMENT REQUIREMENTS:
   - **1 Star Executive (1SE):** 250 PQV + 3 Qualified Legs + 5,400 total Group Volume
   - **2 Star Executive (2SE):** 300 PQV + 3 Individual 1 Star Legs + 7,500 total Group Volume
   - **3 Star Executive (3SE):** 300 PQV + 5 Individual 1 Star Legs + 10,500 total Group Volume
   - **4 Star Executive (4SE):** 300 PQV + 6 Individual 1 Star Legs + 27,000 total Group Volume
   - **5 Star Executive (5SE):** 300 PQV + 9 Individual 1 Star Legs + 43,200 total Group Volume

3. QUALIFIED LEG REQUIREMENTS:
   - Must be a Frontline Distributor (not PCUST)
   - Minimum 150 PQV
   - Must have 3 downline members with 50+ PQV each
   - Volume must be from qualified sales (no self-purchases)

4. CAR BONUS QUALIFICATIONS (1SE+):
   - 3 personally enrolled distributors with 100+ PQV each
   - Must maintain 250 PQV personal volume
   - $5,000 in group volume required
   - Qualify for 3 consecutive months
"""

GLOSSARY_TEXT = """
MEMBERSHIP AFFILIATION TYPES:
- Retail Customer: Purchases at retail prices, not enrolled in compensation plan
- Preferred Customer (PCUST): 
  * Enjoys wholesale pricing (20-30% off), not a business builder
  * Not considered distributors or leg builders
  * Cannot be counted as qualified legs for rank advancement
  * Identified by 'PCUST' in the Title column of the Advanced Genealogy Report
  * All PCUST volume counts towards group volume
  * PCUSTs on level 1 (direct enrollments) within last 60 days can be moved to other distributors
  * When moved, only their non-autoship volume for that calendar month moves with them
  * Volume from autoship orders (as indicated in Group Volume Details CSV) cannot be moved
- Distributor (DIST): Can build a business and earn commissions, $49.95 enrollment
- 1-5 Star Executive: Achieved rank status with increasing benefits and bonuses

VOLUME TYPES & HANDLING:
- PQV (Personal Qualifying Volume): Counts toward rank advancement, 1:1 with BV
- GQV (Group Qualifying Volume): Team volume that counts toward rank requirements
- BV (Bonus Volume): Used to calculate commission payouts, 1:1 with PQV
- OV (Organization Volume): Total volume in your entire organization
- Volume Calculation Rules:
  * Only volume from the Group Volume Details CSV is considered valid
  * Volume is associated with accounts using the ID# from the Group Volume Details CSV
  * Organization levels are determined by the Advanced Genealogy Report:
    - Level 0: Sheet owner
    - Level 1: Direct enrollments (one level below)
    - Level 2: Two levels below, and so on

BUSINESS BUILDING TERMS:
- Frontline: Direct referrals in your first level
- Leg: A branch of your organization
- Depth: Number of levels in an organization
- Width: Number of frontline distributors
- Spillover: Volume that flows down from your upline
- Breakage: Volume that doesn't qualify for commissions

RANK ACRONYMS:
- SAA: Silver Achievement Award (pre-1SE)
- 1SE: 1 Star Executive
- 2SE: 2 Star Executive
- 3SE: 3 Star Executive
- 4SE: 4 Star Executive
- 5SE: 5 Star Executive
"""

POLICIES_TEXT = """
POLICIES & PROCEDURES

1. CODE OF ETHICS & CONDUCT
   - Uphold the highest standards of integrity and honesty
   - Never make exaggerated income claims or guarantees
   - Accurately represent products and business opportunity
   - Respect all company policies and procedures
   - Maintain professional conduct at all company events

2. SPONSORING & RECRUITING
   - Must provide proper training and support to all downline members
   - No cross-line recruiting or poaching of distributors
   - Must provide accurate and complete business information
   - No false or misleading representations about products or compensation
   - Must respect the chain of command in the organization

3. COMPLIANCE REQUIREMENTS
   - Must comply with all federal, state, and local laws
   - Submit required tax documentation (W-9, W-8BEN)
   - Maintain current contact information with the company
   - Adhere to social media and marketing guidelines
   - Complete required training for rank advancements

4. COMMISSION & BONUS POLICIES
   - Payments processed on the 15th of each month
   - Minimum $50 threshold for check payments
   - Direct deposit available with $25 minimum
   - 60-day chargeback period on all sales
   - Unresolved chargebacks may result in commission holds

5. RANK MAINTENANCE
   - Must maintain minimum monthly PQV requirements
   - 3-month rolling average for rank qualification
   - 30-day grace period for rank demotions
   - Special provisions for military deployment
   - Medical/family leave policies available

6. DISPUTE RESOLUTION
   - 30-day window to dispute commission payments
   - Must submit disputes in writing
   - Company's decision is final and binding
   - Arbitration required for legal disputes
   - No class action participation allowed

7. WEBSITE & MARKETING
   - Must use approved marketing materials
   - No unauthorized income claims
   - Social media guidelines must be followed
   - No spam or unsolicited messages
   - Respect intellectual property rights
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
1. **Volume Bank:** Non-autoship orders from frontline PCUSTs or Distributor volume over and above the required threshold found in additional orders in the same period
2. **Movable Accounts:** PCUST accounts enrolled within last 60 days
3. **User's Surplus Volume:** User's excess volume above rank requirements
4. **Volume Pull-Up:** Move volume from frontline members to user if needed

### RANK REQUIREMENTS (CRITICAL - MUST FOLLOW EXACTLY)
* **1 Star Executive (1SE):** 250 PQV + 3 Qualified Legs + 5,400 total Group Volume
* **2 Star Executive (2SE):** 300 PQV + 3 Individual 1 Star Legs + 7,500 total Group Volume
* **3 Star Executive (3SE):** 300 PQV + 5 Individual 1 Star Legs + 10,500 total Group Volume
* **4 Star Executive (4SE):** 300 PQV + 6 Individual 1 Star Legs + 27,000 total Group Volume
* **5 Star Executive (5SE):** 300 PQV + 9 Individual 1 Star Legs + 43,200 total Group Volume

*QUALIFIED LEG REQUIREMENTS (MUST MEET ALL):*
- Must be a Frontline Distributor (not PCUST)
- Minimum 150 PQV
- Must have 3 downline members with 50+ PQV each
- Volume is found from the uploaded Group Volume csv file

*CAR BONUS QUALIFICATIONS (1SE+):*
- 3 personally enrolled distributors with 100+ PQV each
- Must maintain 250 PQV personal volume
- $5,400 in group volume required
- Qualify for 3 consecutive months

---
### MULTI-STEP ANALYSIS & JUSTIFICATION

**OUTPUT STEP 1: INITIAL ASSESSMENT & GAP ANALYSIS**
1. **State the Goal:** 
   - "Core Goal: Achieve {{target_rank}} for [User Name]."
   - "Secondary Goal: Achieve the {{target_rank}} Car Bonus."

2. **User PQV Analysis:**
   - Current Total PQV: [X] (from Group Volume Details)
   - Required PQV: [Y] (based on target rank)
   - Deficit/Surplus: [Z] PQV needed/available

3. **Frontline Legs Analysis:**
   - List all Frontline DISTRIBUTORS with their current status:
     - [Distributor Name]: [PQV] PV | [Qualified Leg Status] | [Action Items]
   - Summary: "The user currently has [Y] of [X] required Qualified Legs for {target_rank}."

4. **Car Bonus Legs Analysis (if applicable):**
   - List all Personally Enrolled Distributors with 100+ PQV
   - Note: These are in addition to the distributors required for rank qualification
   - Summary: "The user currently has [A] of 3 required Car Bonus Legs (personally enrolled distributors with 100+ PQV, in addition to rank requirements)."

5. **Gap Analysis Summary:**
   - PQV Needed: [X] more to reach target
   - Qualified Legs Needed: [Y] more
   - Car Bonus Legs Needed: [Z] more (if applicable)

**OUTPUT STEP 2: RESOURCE INVENTORY**
1. **Volume Bank:** [X] PV available from non-autoship PCUST orders
2. **Movable Accounts:** [Y] PCUSTs enrolled in last 60 days
3. **Surplus Volume:** [Z] PV available from user's excess
4. **Volume Pull-Up Potential:** [A] PV available from frontline members

**OUTPUT STEP 3: PRIORITIZED ACTION PLAN**
1. **PQV Optimization (If Needed):**
   - Move [X] PV from Volume Bank
   - Activate [Y] Movable Accounts for [Z] PV
   - Pull up [A] PV from frontline members

2. **Leg Construction Plan:**
   For each leg needed (in order of priority):
   - **Target Leg #[N]:** [Distributor Name]
   - **Current Status:** [PQV] PV | [Sub-legs] with 50+ PV
   - **Action Plan:**
     1. [Specific action 1]
     2. [Specific action 2]
     3. [Specific action 3]
   - **Resources Needed:** [List resources required]
   - **Expected Outcome:** [Expected PV/leg status after actions]

3. **Car Bonus Leg Development (If Applicable):**
   - [Specific actions to develop/activate Car Bonus legs]
   - [Timeline and milestones]

**OUTPUT STEP 4: TIMELINE & MILESTONES**
1. **Immediate (0-30 days):**
   - [Action item 1]
   - [Action item 2]

2. **Short-term (1-3 months):**
   - [Action item 1]
   - [Action item 2]

3. **Medium-term (3-6 months):**
   - [Action item 1]
   - [Action item 2]

**OUTPUT STEP 5: FINAL RECOMMENDATIONS**
1. **Key Strategies:**
   - [Strategy 1]
   - [Strategy 2]
   - [Strategy 3]

2. **Risk Assessment:**
   - [Potential risk 1] - [Mitigation strategy]
   - [Potential risk 2] - [Mitigation strategy]

3. **Success Metrics:**
   - [Metric 1]: [Target] by [Date]
   - [Metric 2]: [Target] by [Date]

4. **Next Steps:**
   - [Immediate next step 1]
   - [Immediate next step 2]
   - [Immediate next step 3]

**IMPORTANT NOTES:**
- All recommendations must comply with Youngevity's Policies & Procedures
- Always prioritize ethical business practices
- Focus on sustainable growth, not just short-term gains
- Consider distributor development and team building
- Factor in training and support requirements
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

            # Build the prompt parts separately to avoid nesting issues
            # Part 1: Knowledge base
            knowledge_base = f"{COMPENSATION_PLAN_TEXT}\n\n{GLOSSARY_TEXT}\n\n{POLICIES_TEXT}"
            
            # Part 2: Core definitions
            core_definitions = (
                "### CORE DEFINITIONS & UNBREAKABLE RULES\n"
                "1. **DATA UNIFICATION RULE (CRITICAL FIRST STEP):** Before any analysis, you MUST mentally join the two data sources. The 'ID#' column in 'AdvancedGenealogyReport.csv' corresponds to the 'Associate #' column in 'Group Volume Details.csv'.\n\n"
                "2. **DISTRIBUTOR CLASSIFICATION:** After unifying the data, classify each person:\n   - If 'Title' is 'PCUST' → CUSTOMER (cannot be a leg)\n   - If 'Title' is anything else (SAA, SRA, 1SE, BRA, DIST, etc.) → DISTRIBUTOR (can be a leg)\n\n"
                "3. **PRINCIPLE OF MINIMUM SUFFICIENT ACTION:** Use the smallest amount of resources necessary to meet requirements. Once a distributor or leg is qualified, STOP allocating resources to them.\n\n"
                "4. **VOLUME SOURCE:** All volume data comes from the 'Volume' column in 'Group Volume Details.csv'.\n\n"
            )
            
            # Part 3: Business resources
            business_resources = (
                "### BUSINESS RESOURCES\n"
                "1. **Volume Bank:** Non-autoship orders from frontline PCUSTs or Distributor volume over and above the required threshold found in additional orders in the same period\n"
                "2. **Movable Accounts:** PCUST accounts enrolled within last 60 days\n"
                "3. **User's Surplus Volume:** User's excess volume above rank requirements\n"
                "4. **Volume Pull-Up:** Move volume from frontline members to user if needed\n\n"
            )
            
            # Part 4: Rank requirements
            rank_requirements = (
                "### RANK REQUIREMENTS (CRITICAL - MUST FOLLOW EXACTLY)\n"
                "* **1 Star Executive (1SE):** 250 PQV + 3 Qualified Legs + 5,400 total Group Volume\n"
                "* **2 Star Executive (2SE):** 300 PQV + 3 Individual 1 Star Legs + 7,500 total Group Volume\n"
                "* **3 Star Executive (3SE):** 300 PQV + 5 Individual 1 Star Legs + 10,500 total Group Volume\n"
                "* **4 Star Executive (4SE):** 300 PQV + 6 Individual 1 Star Legs + 27,000 total Group Volume\n"
                "* **5 Star Executive (5SE):** 300 PQV + 9 Individual 1 Star Legs + 43,200 total Group Volume\n\n"
                "*QUALIFIED LEG REQUIREMENTS (MUST MEET ALL):*\n"
                "- Must be a Frontline Distributor (not PCUST)\n"
                "- Minimum 150 PQV\n"
                "- Must have 3 downline members with 50+ PQV each\n"
                "- Volume is found from the uploaded Group Volume csv file\n\n"
                "*CAR BONUS QUALIFICATIONS (1SE+):*\n"
                "- 3 personally enrolled distributors with 100+ PQV each\n"
                "- Must maintain 250 PQV personal volume\n"
                "- $5,400 in group volume required\n"
                "- Qualify for 3 consecutive months\n\n"
            )
            
            # Part 5: Analysis section with target rank
            analysis_part1 = (
                "---\n"
                "### MULTI-STEP ANALYSIS & JUSTIFICATION\n\n"
                "**OUTPUT STEP 1: INITIAL ASSESSMENT & GAP ANALYSIS**\n"
                f"1. **State the Goal:** \n   - \"Core Goal: Achieve **{target_rank}** for [User Name].\"\n   - \"Secondary Goal: Achieve the **{target_rank}** Car Bonus.\"\n\n"
                "2. **User PQV Analysis:**\n   - Current Total PQV: [X] (from Group Volume Details)\n   - Required PQV: [Y] (based on target rank)\n   - Deficit/Surplus: [Z] PQV needed/available\n\n"
            )
            
            # Part 6: Analysis with target rank continued
            analysis_part2 = (
                f"3. **Frontline Legs Analysis:**\n   - List all Frontline DISTRIBUTORS with their current status:\n     - [Distributor Name]: [PQV] PV | [Qualified Leg Status] | [Action Items]\n   - Summary: \"The user currently has [Y] of [X] required Qualified Legs for **{target_rank}**.\"\n\n"
                f"4. **Car Bonus Legs Analysis (if applicable):**\n   - List all Personally Enrolled Distributors with 100+ PQV\n   - Note: These are in addition to the distributors required for rank qualification\n   - Summary: \"The user currently has [A] of 3 required Car Bonus Legs (personally enrolled distributors with 100+ PQV, in addition to rank requirements).\"\n\n"
            )
            
            # Part 7: Gap analysis and resource inventory
            gap_analysis = (
                "5. **Gap Analysis Summary:**\n   - PQV Needed: [X] more to reach target\n   - Qualified Legs Needed: [Y] more\n   - Car Bonus Legs Needed: [Z] more (if applicable)\n\n"
                "**OUTPUT STEP 2: RESOURCE INVENTORY**\n"
                "1. **Volume Bank:** [X] PV available from non-autoship PCUST orders\n"
                "2. **Movable Accounts:** [Y] PCUSTs enrolled in last 60 days\n"
                "3. **Surplus Volume:** [Z] PV available from user's excess\n"
                "4. **Volume Pull-Up Potential:** [A] PV available from frontline members\n\n"
            )
            
            # Part 8: Action plan
            action_plan = (
                "**OUTPUT STEP 3: PRIORITIZED ACTION PLAN**\n"
                "1. **PQV Optimization (If Needed):**\n   - Move [X] PV from Volume Bank\n   - Activate [Y] Movable Accounts for [Z] PV\n   - Pull up [A] PV from frontline members\n\n"
                "2. **Leg Construction Plan:**\n   For each leg needed (in order of priority):\n   - **Target Leg #[N]:** [Distributor Name]\n   - **Current Status:** [PQV] PV | [Sub-legs] with 50+ PV\n   - **Action Plan:**\n     1. [Specific action 1]\n     2. [Specific action 2]\n     3. [Specific action 3]\n   - **Resources Needed:** [List resources required]\n   - **Expected Outcome:** [Expected PV/leg status after actions]\n\n"
                "3. **Car Bonus Leg Development (If Applicable):**\n   - [Specific actions to develop/activate Car Bonus legs]\n   - [Timeline and milestones]\n\n"
            )
            
            # Part 9: Timeline and recommendations
            timeline = (
                f"**OUTPUT STEP 4: TIMELINE & MILESTONES**\n"
                f"1. **Immediate (0-30 days):**\n   - [Action item 1]\n   - [Action item 2]\n\n"
                f"2. **Short-term (1-3 months):**\n   - [Action item 1]\n   - [Action item 2]\n\n"
                f"3. **Medium-term (3-6 months):**\n   - [Action item 1]\n   - [Action item 2]\n\n"
            )
            
            # Part 10: Final recommendations
            recommendations = (
                f"**OUTPUT STEP 5: FINAL RECOMMENDATIONS**\n"
                f"1. **Key Strategies:**\n   - [Strategy 1]\n   - [Strategy 2]\n   - [Strategy 3]\n\n"
                f"2. **Risk Assessment:**\n   - [Potential risk 1] - [Mitigation strategy]\n   - [Potential risk 2] - [Mitigation strategy]\n\n"
                f"3. **Success Metrics:**\n   - [Metric 1]: [Target] by [Date]\n   - [Metric 2]: [Target] by [Date]\n\n"
                f"4. **Next Steps:**\n   - [Immediate next step 1]\n   - [Immediate next step 2]\n   - [Immediate next step 3]\n\n"
                f"**IMPORTANT NOTES:**\n- All recommendations must comply with Youngevity's Policies & Procedures\n- Always prioritize ethical business practices\n- Focus on sustainable growth, not just short-term gains\n- Consider distributor development and team building\n- Factor in training and support requirements"
            )
            
            # Assemble the full prompt
            full_prompt = (
                f"{knowledge_base}\n\n"
                f"{core_definitions}"
                f"{business_resources}"
                f"{rank_requirements}"
                f"{analysis_part1}"
                f"{analysis_part2}"
                f"{gap_analysis}"
                f"{action_plan}"
                f"{timeline}"
                f"{recommendations}\n\n"
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
    if not api_key:
        st.error("❌ Please enter your Google AI API key in the sidebar first.")
        st.stop()
        
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
                {
                    "role": "user", 
                    "parts": [f"Initial analysis request for {st.session_state.raw_data.get('target_rank', 'target rank')}:\n{st.session_state.get('full_initial_prompt', '')}"]
                },
                {"role": "model", "parts": [st.session_state.get("api_response", "")]}
            ]
            
            # Add previous chat messages to the context
            for msg in st.session_state.messages[:-1]:  # Exclude the current message
                chat_history.append({
                    "role": "user" if msg["role"] == "user" else "model", 
                    "parts": [msg["content"]]
                })
            
            # Add the current user's question with context
            context_prompt = f"""
            You are a Youngevity business analysis assistant. The user is working on achieving {st.session_state.raw_data.get('target_rank', 'their target rank')}.
            
            Previous analysis context:
            {st.session_state.get('api_response', 'No previous analysis available.')}
            
            User's question: {prompt}
            
            Please provide a detailed, helpful response that:
            1. Directly addresses the user's question
            2. References specific details from their business analysis when relevant
            3. Provides actionable advice based on Youngevity's compensation plan
            4. Asks clarifying questions if the request is ambiguous
            """
            
            # Start a chat session with the full history
            chat = model.start_chat(history=chat_history)
            
            # Get the AI's response
            response = chat.send_message(context_prompt)
            
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
            error_msg = f"""
            ⚠️ Sorry, I encountered an error: {str(e)}
            
            Please try the following:
            1. Check your internet connection
            2. Verify your API key is valid and has sufficient quota
            3. Try asking your question again
            4. If the problem persists, please contact support
            """
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
