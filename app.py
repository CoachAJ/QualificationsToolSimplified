import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- Helper function to build prompt consistently ---
def preprocess_data(gvd_df, agr_df):
    """
    Pre-processes and summarizes the genealogy and volume data to create a concise
    summary for the AI, avoiding token limits.

    Args:
        gvd_df (DataFrame): Group Volume Details dataframe, with 'PQV' pre-calculated.
        agr_df (DataFrame): Advanced Genealogy Report dataframe.

    Returns:
        dict: A summary dictionary containing key stats for the prompt, or None on error.
    """
    try:
        # Ensure required columns are of the correct type
        agr_df['Level'] = pd.to_numeric(agr_df['Level'], errors='coerce')
        agr_df['ID#'] = agr_df['ID#'].astype(str)
        gvd_df['Associate #'] = gvd_df['Associate #'].astype(str)
        if 'Enroller ID' in agr_df.columns:
            agr_df['Enroller ID'] = agr_df['Enroller ID'].astype(str)

        # Merge the two dataframes
        merged_df = pd.merge(agr_df, gvd_df[['Associate #', 'PQV', 'Volume']], left_on='ID#', right_on='Associate #', how='left')
        merged_df['PQV'] = merged_df['PQV'].fillna(0)
        merged_df['Volume'] = merged_df['Volume'].fillna(0)

        # Identify the user (Level 0)
        user_row = merged_df[merged_df['Level'] == 0]
        if user_row.empty:
            st.error("❌ Could not identify the user (Level 0) in the Advanced Genealogy Report.")
            return None
        user_row = user_row.iloc[0]
        user_id = user_row['ID#']
        user_name = user_row['Name']
        user_pqv = user_row['PQV']

        # Calculate total group volume
        total_gv = merged_df['Volume'].sum()

        # Identify frontline distributors (Level 1 and not PCUST)
        frontline_df = merged_df[(merged_df['Level'] == 1) & (merged_df['Title'] != 'PCUST')]

        frontline_summary = []
        for _, distributor in frontline_df.iterrows():
            dist_id = distributor['ID#']
            
            # Find this distributor's direct downline (enrolled by them)
            downline_df = merged_df[merged_df['Enroller ID'] == dist_id]
            
            # Count downline members with 50+ PQV
            downline_50pqv_count = downline_df[downline_df['PQV'] >= 50].shape[0]

            frontline_summary.append({
                "name": distributor['Name'],
                "id": dist_id,
                "pqv": distributor['PQV'],
                "downline_50pqv_count": downline_50pqv_count
            })

        summary = {
            "user_name": user_name,
            "user_id": user_id,
            "user_pqv": user_pqv,
            "total_gv": total_gv,
            "frontline": frontline_summary
        }
        return summary
    except Exception as e:
        st.error(f"❌ An error occurred during data pre-processing: {e}")
        return None

def build_prompt(target_rank_value, data_summary):
    """Build a complete prompt using the pre-processed data summary.

    Args:
        target_rank_value (str): The selected target rank.
        data_summary (dict): The dictionary containing summarized data.

    Returns:
        str: The complete prompt for the AI.
    """
    # Create a string representation of the frontline summary
    frontline_str = "\n".join([
        f"  - Name: {f['name']}, ID: {f['id']}, PQV: {f['pqv']:.2f}, Downline (50+ PQV): {f['downline_50pqv_count']}"
        for f in data_summary['frontline']
    ])

    # The main prompt structure that now takes the summary
    prompt = f"""
# TASK: Analyze the following business summary and create a strategic plan to help the user achieve the '{target_rank_value}' rank.

# 1. BUSINESS OVERVIEW
- **User Name:** {data_summary['user_name']}
- **User ID:** {data_summary['user_id']}
- **Current Personal Qualifying Volume (PQV):** {data_summary['user_pqv']:.2f}
- **Total Group Volume (GV):** {data_summary['total_gv']:.2f}

# 2. FRONTLINE TEAM SUMMARY
{frontline_str}

# 3. REFERENCE: YOUNGEVITY COMPENSATION PLAN & RULES
{COMPENSATION_PLAN_TEXT}

{GLOSSARY_TEXT}

{POLICIES_TEXT}

# 4. YOUR ANALYSIS & ACTION PLAN
Based on the business overview and the official rules, provide a detailed, multi-step action plan. The plan must be structured exactly as follows:

**OUTPUT STEP 1: INITIAL ASSESSMENT & GAP ANALYSIS**
1.  **State the Goal:** Clearly state the core goal (achieving {target_rank_value}) and the secondary goal (car bonus).
2.  **User PQV Analysis:** Compare the user's current PQV to the required PQV for {target_rank_value}. State the deficit or surplus.
3.  **Group Volume Analysis:** Compare the user's current Group Volume to the required GV for {target_rank_value}.
4.  **Frontline Legs Analysis:** Analyze the frontline summary provided. Determine how many distributors currently meet the 'Qualified Leg' requirements for {target_rank_value}. State how many are qualified and how many more are needed.
5.  **Gap Analysis Summary:** Summarize the key gaps in PQV, GV, and Qualified Legs.

**OUTPUT STEP 2: PRIORITIZED ACTION PLAN**
Provide a numbered list of the most critical actions the user should take. For each action, explain *why* it's important and what the *expected outcome* is. Focus on the most efficient path to the goal.

   *Example Action:*
   1.  **Develop [Distributor Name] into a Qualified Leg:** This is the top priority as they are closest to qualifying. 
       - *Action:* Help them sign up one more person with 50 PQV.
       - *Expected Outcome:* This will complete one of the three required legs.

**OUTPUT STEP 3: FINAL RECOMMENDATIONS**
1.  **Key Strategies:** Provide 2-3 high-level strategic recommendations for long-term, sustainable growth.
2.  **Risk Assessment:** Identify 1-2 potential risks (e.g., a key leg falling out of qualification) and suggest mitigation strategies.
3.  **Next Steps:** List the three most immediate, concrete actions the user should take in the next 72 hours.
"""
    return prompt

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
# --- LEGACY SYSTEM PROMPT (NOT USED - REPLACED BY build_prompt FUNCTION) ---
# ==============================================================================
# This section is kept for reference but is not used in the current implementation.
# The build_prompt() function above handles all prompt construction with proper variable substitution.

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
# Initialize all required session state variables
if "api_response" not in st.session_state:
    st.session_state.api_response = "### Your Strategic Plan Will Appear Here\n\n*Please fill in all the fields above and click 'Generate Plan' to begin.*"
if "target_rank" not in st.session_state:
    st.session_state.target_rank = "1 Star Executive"
if "full_initial_prompt" not in st.session_state:
    st.session_state.full_initial_prompt = ""
if "raw_data" not in st.session_state:
    st.session_state.raw_data = {"target_rank": st.session_state.target_rank}

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

    with st.expander("🎯 Step 3: Set Target Rank", expanded=True):
        # Directly set target_rank in session state when the selection changes
        target_rank = st.selectbox(
            "Select your target rank:",
            ("1 Star Executive", "2 Star Executive", "3 Star Executive", "4 Star Executive", "5 Star Executive"),
            key="target_rank"  # This automatically stores the selection in st.session_state.target_rank
        )
        # Store the target rank in a variable for immediate use
        target_rank = st.session_state.target_rank

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

                # --- Start Validation ---
                required_gvd_cols = {'Associate #', 'Volume'}
                required_agr_cols = {'ID#', 'Title', 'Name', 'Level'}
                
                missing_gvd = list(required_gvd_cols - set(gvd_df.columns))
                missing_agr = list(required_agr_cols - set(agr_df.columns))

                # Handle flexible 'Enroller' column
                enroller_col = None
                if 'Enroller ID' in agr_df.columns:
                    enroller_col = 'Enroller ID'
                elif 'Enroller' in agr_df.columns:
                    enroller_col = 'Enroller'
                
                if not enroller_col:
                    missing_agr.append('Enroller ID or Enroller')

                if missing_gvd or missing_agr:
                    error_msg = "❌ Error: Missing required columns. "
                    if missing_gvd:
                        error_msg += f"In Group Volume Details, missing: **{', '.join(missing_gvd)}**. "
                    if missing_agr:
                        error_msg += f"In Advanced Genealogy Report, missing: **{', '.join(missing_agr)}**. "
                    st.error(error_msg + "Please check your files.")
                    st.stop()
                # --- End Validation ---

                # Standardize Enroller column before processing
                if enroller_col == 'Enroller':
                    agr_df.rename(columns={'Enroller': 'Enroller ID'}, inplace=True)

                # Calculate PQV
                st.info("📊 Processing data: Calculating PQV from Volume data by Associate Number...")
                gvd_df['PQV'] = gvd_df.groupby('Associate #')['Volume'].transform('sum').round(2)
                st.success("✅ CSV files validated and processed successfully!")

                # Pre-process data to create a compact summary
                st.info("📝 Summarizing data for AI analysis...")
                data_summary = preprocess_data(gvd_df, agr_df)
                if data_summary is None:
                    st.error("❌ Data summary failed. Cannot proceed with analysis.")
                    st.stop()
                st.success("✅ Data summarized successfully!")

            except Exception as e:
                st.error(f"❌ Error reading or processing CSV files: {e}")
                st.stop()

            # Build the prompt using the new summary
            full_prompt = build_prompt(st.session_state.target_rank, data_summary)
            
            # Store the initial prompt and raw data for the chat session
            st.session_state.full_initial_prompt = full_prompt
            st.session_state.raw_data = {
                'gvd': gvd_data,
                'agr': agr_data,
                'target_rank': st.session_state.target_rank
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
        # Display dynamic stats based on target_rank if available
        target_rank = st.session_state.target_rank
        
        # Set default values
        pqv_required = "*Calculating...*"
        legs_needed = "*Calculating...*"
        car_bonus_legs = "*Calculating...*"
        
        # Set requirements based on target rank
        if target_rank == "1 Star Executive":
            pqv_required = "250 PQV"
            legs_needed = "3 Qualified Legs"
            car_bonus_legs = "N/A"
        elif target_rank == "2 Star Executive":
            pqv_required = "300 PQV"
            legs_needed = "3 Individual 1 Star Legs"
            car_bonus_legs = "N/A"
        elif target_rank == "3 Star Executive":
            pqv_required = "300 PQV"
            legs_needed = "5 Individual 1 Star Legs"
            car_bonus_legs = "N/A"
        elif target_rank == "4 Star Executive":
            pqv_required = "300 PQV"
            legs_needed = "6 Individual 1 Star Legs"
            car_bonus_legs = "Car Eligible"
        elif target_rank == "5 Star Executive":
            pqv_required = "300 PQV"
            legs_needed = "9 Individual 1 Star Legs"
            car_bonus_legs = "Car Qualified"
            
        st.markdown(f"""
        - **Target Rank:** {target_rank}
        - **PQV Required:** {pqv_required}
        - **Legs Needed:** {legs_needed}
        - **Car Bonus Legs:** {car_bonus_legs}
        """)
    
    st.markdown("---")
    st.subheader("📚 Help & Resources")
    with st.container(border=True):
        st.page_link("https://www.youngevity.com", label="🌐 Youngevity Official Site")
        st.page_link("https://aistudio.google.com", label="🔑 Get API Key")
        st.page_link("https://youngevity.com/compensation-plan/", label="📈 View Full Compensation Plan")

# --- Interactive Follow-up Chat ---
st.markdown("---")
st.subheader("💬 Need Clarification? Ask Me Anything")
st.caption("Ask follow-up questions about your plan, like 'How can I qualify Leg #2 faster?' or 'What if I move volume from X to Y?'")

# Initialize chat history if it doesn't exist
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state or st.session_state.messages == []:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user questions
if prompt := st.chat_input("Ask a follow-up question about your rank advancement plan..."):
    # Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if a plan has been generated first
    if "raw_data" not in st.session_state or not st.session_state.raw_data:
        st.error("⚠️ Please generate a rank advancement plan first before asking questions.")
    else:
        # Process the AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Configure the API
                    api_key = st.session_state.get("api_key", "")
                    if not api_key:
                        st.error("⚠️ Please provide your API Key first.")
                        st.stop()
                    
                    # Setup AI model
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    
                    # Get previous messages to maintain context
                    chat_history = []
                    for msg in st.session_state.messages:
                        if msg["role"] == "user":
                            chat_history.append({"role": "user", "parts": [msg["content"]]})
                        else:
                            chat_history.append({"role": "model", "parts": [msg["content"]]})
                    
                    # Start a chat and get relevant data from session state
                    chat = model.start_chat(history=chat_history)
                    raw_data = st.session_state.raw_data
                    
                    # Access target_rank safely from session_state with fallback
                    current_target_rank = raw_data.get('target_rank', st.session_state.target_rank)
                    
                    # Construct a context for the follow-up question
                    context = (
                        f"The user is targeting the {current_target_rank} rank in Youngevity. "
                        "Remember the rank requirements and car bonus qualifications as specified in the knowledge base. "
                        "Base your answer on the previously analyzed data and the rank advancement plan you generated."
                    )
                    
                    # Send the message with context
                    complete_prompt = f"{context}\n\nUser's question: {prompt}"
                    response = chat.send_message(complete_prompt)
                    
                    # Process and display the response
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("❌ Received an empty response. Please try a different question.")
                
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
