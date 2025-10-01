import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import os
import uuid
import io

st.set_page_config(page_title="Project Ksheersagar Survey", layout="wide")

# --- Global Configuration and State Initialization ---
if "step" not in st.session_state:
    st.session_state["step"] = 1
if "responses" not in st.session_state:
    st.session_state["responses"] = {}

CSV_FILE = "responses.csv"
responses = st.session_state["responses"]
MAX_STEP = 5  # Total number of form steps before the Confirmation/Review step

def safe_index(options, value, default_index=0):
    """Safely gets the index of a value in a list, returning a default if not found."""
    try:
        if value is None:
            return default_index
        val_to_check = str(value) if isinstance(value, (date, time)) else value
        options_str = [str(o) for o in options]
        if str(val_to_check) in options_str:
            return options_str.index(str(val_to_check))
        return default_index
    except (ValueError, TypeError):
        return default_index

def get_time_value(key):
    """Retrieves time value from responses, handling string format if present."""
    val = responses.get(key)
    if isinstance(val, time):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%H:%M:%S").time()
        except ValueError:
            pass
    return time(datetime.now().hour, datetime.now().minute)

def display_progress_indicator(current_step):
    """Displays a simple progress indicator."""
    if 1 < current_step < MAX_STEP:
        st.info(f"**Progress:** Section {current_step - 1} of {MAX_STEP - 1}")

# -----------------------------------------------------------------------------
# Section 1: Consent (Step 1)
# -----------------------------------------------------------------------------
if st.session_state["step"] == 1:
    st.title("Project Ksheersagar Survey")
    st.header("1. Informed Consent")
    with st.form("consent_form"):
        responses["consent"] = st.radio(
            "Do you **agree to participate** in this survey?",
            ["Yes", "No"],
            index=safe_index(["Yes", "No"], responses.get("consent")),
            key="consent_radio"
        )
        responses["photo_permission"] = st.radio(
            "Do you give **permission for taking pictures**?",
            ["Yes", "No"],
            index=safe_index(["Yes", "No"], responses.get("photo_permission")),
            key="photo_permission_radio"
        )
        responses["respondent_signature"] = st.text_input(
            "Respondent **Signature**",
            value=responses.get("respondent_signature", ""),
            key="respondent_signature_input"
        )
        responses["interviewer_signature"] = st.text_input(
            "Interviewer **Signature**",
            value=responses.get("interviewer_signature", ""),
            key="interviewer_signature_input"
        )
        responses["consent_date"] = st.date_input(
            "Date",
            value=responses.get("consent_date", date.today()),
            key="consent_date_input"
        )
        if st.form_submit_button("Next"):
            if responses["consent"] == "Yes":
                if responses["respondent_signature"] and responses["interviewer_signature"]:
                    st.session_state["step"] = 2
                    st.rerun()
                else:
                    st.error("Please provide both respondent and interviewer signatures to proceed.")
            else:
                st.warning("You must agree to participate to proceed. Survey terminated.")
                st.stop()

# -----------------------------------------------------------------------------
# Section 2: Identification (Step 2)
# -----------------------------------------------------------------------------
elif st.session_state["step"] == 2:
    display_progress_indicator(st.session_state["step"])
    st.header("2. Block 1: Identification")
    responses["bmc_name"] = st.text_input("Name of the **BMC/MCC**", value=responses.get("bmc_name", ""), key="bmc_name_input")
    responses["year_establishment"] = st.number_input(
        "Year of **establishment**", 1900, datetime.today().year, step=1,
        value=responses.get("year_establishment", 2000), key="year_establishment_input"
    )
    responses["bmc_contact"] = st.text_input("BMC manager **contact**", value=responses.get("bmc_contact", ""), key="bmc_contact_input")
    responses["respondent_name"] = st.text_input("Respondent **name**", value=responses.get("respondent_name", ""), key="respondent_name_input")
    gender_options = ["Male", "Female", "Other"]
    responses["gender"] = st.radio(
        "**Gender**", gender_options,
        index=safe_index(gender_options, responses.get("gender")), key="gender_radio"
    )
    dairy_partner_options = ["Schreiber Dynamix", "Govid dairy", "Sunfresh dairy", "Parag Dairy", "Other"]
    responses["dairy_partner"] = st.selectbox(
        "**Dairy partner**", dairy_partner_options,
        index=safe_index(dairy_partner_options, responses.get("dairy_partner")), key="dairy_partner_select"
    )
    state_options = ["Maharashtra", "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Other"]
    responses["state"] = st.selectbox(
        "**State**", state_options,
        index=safe_index(state_options, responses.get("state")), key="state_select"
    )
    responses["district"] = st.text_input("**District**", value=responses.get("district", ""), key="district_input")
    responses["block"] = st.text_input("**Block**", value=responses.get("block", ""), key="block_input")
    centre_type_options = ["BMC", "VLC", "CC"]
    responses["centre_type"] = st.radio(
        "Type of **centre**", centre_type_options,
        index=safe_index(centre_type_options, responses.get("centre_type")), key="centre_type_radio"
    )
    responses["interview_date"] = st.date_input(
        "**Interview date**", value=responses.get("interview_date", date.today()), key="interview_date_input"
    )
    responses["start_time"] = st.time_input(
        "**Start time**", value=get_time_value("start_time"), key="start_time_input"
    )
    responses["end_time"] = st.time_input(
        "**End time**", value=get_time_value("end_time"), key="end_time_input"
    )
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Consent"):
            st.session_state["step"] = 1
            st.rerun()
    with col2:
        if st.button("Save and Next: BMC Operation"):
            st.session_state["step"] = 3
            st.rerun()

# -----------------------------------------------------------------------------
# Section 3: BMC Operation (Step 3)
# -----------------------------------------------------------------------------
elif st.session_state["step"] == 3:
    display_progress_indicator(st.session_state["step"])
    st.header("3. Block 2: BMC Operation")
    procurement_options = ["Producer-based", "Agent-based", "Institutional", "Other"]
    responses["procurement_model"] = st.radio(
        "**Procurement model**", procurement_options,
        index=safe_index(procurement_options, responses.get("procurement_model")), key="procurement_model_radio"
    )
    responses["agents_daily"] = st.number_input("Average number of **agents/farmers per day**", 0, step=1, value=responses.get("agents_daily", 0), key="agents_daily_input")
    responses["staff_count"] = st.number_input("Number of **staff**", 0, step=1, value=responses.get("staff_count", 0), key="staff_count_input")
    responses["agents_count"] = st.number_input("Number of **agents**", 0, step=1, value=responses.get("agents_count", 0), key="agents_count_input")
    responses["farmers_count"] = st.number_input("Number of **dairy farmers**", 0, step=1, value=responses.get("farmers_count", 0), key="farmers_count_input")

    # UPDATED/NEW: Split morning/evening farmers into Male/Female
    st.subheader("Farmers Pouring Milk")
    col_morn, col_even = st.columns(2)
    with col_morn:
        st.markdown("**Morning**")
        responses["morning_male_farmers"] = st.number_input("Number of **Male** farmers (Morning)", 0, step=1, value=responses.get("morning_male_farmers", 0), key="morning_male_farmers_input")
        responses["morning_female_farmers"] = st.number_input("Number of **Female** farmers (Morning)", 0, step=1, value=responses.get("morning_female_farmers", 0), key="morning_female_farmers_input")
    with col_even:
        st.markdown("**Evening**")
        responses["evening_male_farmers"] = st.number_input("Number of **Male** farmers (Evening)", 0, step=1, value=responses.get("evening_male_farmers", 0), key="evening_male_farmers_input")
        responses["evening_female_farmers"] = st.number_input("Number of **Female** farmers (Evening)", 0, step=1, value=responses.get("evening_female_farmers", 0), key="evening_female_farmers_input")

    st.markdown("---")
    # UPDATED: Options aligned with PDF
    plastic_options = ["10-30%", "40-50%", "More than 50%", "100%", "Do not know/can't say"]
    responses["plastic_containers"] = st.radio(
        "% using **plastic containers**", plastic_options,
        index=safe_index(plastic_options, responses.get("plastic_containers")), key="plastic_containers_radio"
    )
    # UPDATED: Options aligned with PDF
    cleaning_options = ["Only in the morning", "Only in the evening", "Both in the morning and evening", "Do not know/cannot say"]
    responses["cleaning_frequency"] = st.radio(
        "How often **accessories cleaned**", cleaning_options,
        index=safe_index(cleaning_options, responses.get("cleaning_frequency")), key="cleaning_frequency_radio"
    )
    yes_no_options = ["Yes", "No"]
    responses["milk_records"] = st.radio(
        "**Maintain milk records**?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("milk_records")), key="milk_records_radio"
    )
    # UPDATED: Options aligned with PDF
    payment_schedule_options = ["Every 10th day in a month", "Twice a month", "Once a month", "No specific schedule"]
    responses["payment_schedule"] = st.radio(
        "**Payment schedule**", payment_schedule_options,
        index=safe_index(payment_schedule_options, responses.get("payment_schedule")), key="payment_schedule_radio"
    )
    payment_method_options = ["Cash", "Bank transfer", "Both"]
    responses["payment_method"] = st.radio(
        "**Payment method**", payment_method_options,
        index=safe_index(payment_method_options, responses.get("payment_method")), key="payment_method_radio"
    )
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Identification"):
            st.session_state["step"] = 2
            st.rerun()
    with col2:
        if st.button("Save and Next: Observation Tool"):
            st.session_state["step"] = 4
            st.rerun()

# -----------------------------------------------------------------------------
# Section 4: Observation Tool (Step 4)
# -----------------------------------------------------------------------------
elif st.session_state["step"] == 4:
    display_progress_indicator(st.session_state["step"])
    st.header("4. Observation Tool")
    yes_no_options = ["Yes", "No"]
    
    responses["fssai_certified"] = st.radio(
        "**FSSAI certification** available?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("fssai_certified")), key="fssai_certified_radio"
    )
    responses["sop_guidelines"] = st.radio(
        "**SOP guidelines** available (not less than 3 years old)?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("sop_guidelines")), key="sop_guidelines_radio"
    )
    responses["weigh_scale_cert"] = st.radio(
        "**Weigh scale certificate** available?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("weigh_scale_cert")), key="weigh_scale_cert_radio"
    )
    # UPDATED: Question and options aligned with PDF
    surroundings_options = ["No accumulation of water", "Accumulation of water"]
    responses["surroundings_clean"] = st.radio(
        "Are the surroundings of BMC/CC/VLC free from **waste and water accumulation**?", surroundings_options,
        index=safe_index(surroundings_options, responses.get("surroundings_clean")), key="surroundings_clean_radio"
    )
    # UPDATED: Descriptive ratings
    rating_1_5 = ["1 (Most Unclean)", "2", "3", "4", "5 (Very Clean)"]
    responses["bmc_cleanliness"] = st.radio(
        "**BMC cleanliness** (Rating 1=Most Unclean, 5=Very Clean)", rating_1_5,
        index=safe_index(rating_1_5, responses.get("bmc_cleanliness")), key="bmc_cleanliness_radio"
    )
    responses["cooler_temp"] = st.radio(
        "**Cooler** operating at 4°C or below?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("cooler_temp")), key="cooler_temp_radio"
    )
    # UPDATED: Descriptive ratings
    rating_1_3_clean = ["Very unclean", "Unclean", "Clean"]
    responses["churner_cleanliness"] = st.radio(
        "**Churner cleanliness** (Rating 1=Very unclean, 3=Clean)", rating_1_3_clean,
        index=safe_index(rating_1_3_clean, responses.get("churner_cleanliness")), key="churner_cleanliness_radio"
    )
    responses["accessories_cleanliness"] = st.radio(
        "**Accessories cleanliness** (Rating 1=Very unclean, 3=Clean)", rating_1_3_clean,
        index=safe_index(rating_1_3_clean, responses.get("accessories_cleanliness")), key="accessories_cleanliness_radio"
    )
    responses["cleaning_solution"] = st.radio(
        "**Cleaning solution** (detergent/disinfectant) available?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("cleaning_solution")), key="cleaning_solution_radio"
    )
    # UPDATED: Added "dippers"
    responses["samplers_clean"] = st.radio(
        "**Samplers/plungers/dippers clean**?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("samplers_clean")), key="samplers_clean_radio"
    )
    responses["hot_water"] = st.radio(
        "**Hot water** available for cleaning?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("hot_water")), key="hot_water_radio"
    )
    # UPDATED: Added "No, kept on the floor"
    samplers_shelves_options = ["Yes", "No", "No, kept on the floor"]
    responses["samplers_shelves"] = st.radio(
        "Samplers **kept on dedicated shelves**?", samplers_shelves_options,
        index=safe_index(samplers_shelves_options, responses.get("samplers_shelves")), key="samplers_shelves_radio"
    )
    responses["nylon_cloth_clean"] = st.radio(
        "**Nylon sieve/cloth clean**?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("nylon_cloth_clean")), key="nylon_cloth_clean_radio"
    )
    responses["operator_wash_hands"] = st.radio(
        "**Operator washes hands** routinely?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("operator_wash_hands")), key="operator_wash_hands_radio"
    )
    responses["chemicals_expiry"] = st.radio(
        "Are **chemicals within expiry** date?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("chemicals_expiry")), key="chemicals_expiry_radio"
    )
    responses["tank_clean"] = st.radio(
        "**Tank properly cleaned**?", yes_no_options,
        index=safe_index(yes_no_options, responses.get("tank_clean")), key="tank_clean_radio"
    )
    pump_leak_options = ["No leaking", "Yes, leaks"]
    responses["pump_leak"] = st.radio(
        "**Pump seal leaks**?", pump_leak_options,
        index=safe_index(pump_leak_options, responses.get("pump_leak")), key="pump_leak_radio"
    )
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to BMC Operation"):
            st.session_state["step"] = 3
            st.rerun()
    with col2:
        if st.button("Review & Submit"):
            st.session_state["step"] = 5
            st.rerun()

# -----------------------------------------------------------------------------
# Section 5: Review and Final Submission (Step 5)
# -----------------------------------------------------------------------------
elif st.session_state["step"] == 5:
    st.header("5. Finalize and Submit")
    with st.form("final_submit_form"):
        st.subheader("Please review your responses before submitting: 👇")
        final_responses = st.session_state["responses"].copy()
        for key, value in final_responses.items():
            if isinstance(value, (datetime, date, time)):
                final_responses[key] = str(value)
        
        df_review = pd.DataFrame([final_responses]).T
        df_review.columns = ["Response"]
        df_review = df_review[df_review["Response"].astype(str).str.strip() != ""]
        st.dataframe(df_review, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Back to Observation Tool"):
                st.session_state["step"] = 4
                st.rerun()
        with col2:
            if st.form_submit_button("✅ Submit & Save Final"):
                responses["submission_id"] = str(uuid.uuid4())
                df = pd.DataFrame([final_responses])
                if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
                    try:
                        existing_df = pd.read_csv(CSV_FILE)
                        df = pd.concat([existing_df, df], ignore_index=True)
                    except pd.errors.EmptyDataError:
                        st.warning("Existing CSV file was empty. Overwriting with new data.")
                    except Exception as e:
                        st.error(f"Error reading existing CSV: {e}")
                
                df.to_csv(CSV_FILE, index=False)
                st.session_state["step"] = 6
                st.rerun()

# -----------------------------------------------------------------------------
# Section 6: Confirmation Page (Step 6)
# -----------------------------------------------------------------------------
elif st.session_state["step"] == 6:
    st.header("Thank you! 🙏")
    st.success("Your responses have been successfully submitted and saved.")
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        saved_df = pd.read_csv(CSV_FILE)
        st.subheader("All Submitted Responses (Last 5)")
        st.dataframe(saved_df.tail(5), use_container_width=True)
        
        csv_buffer = io.StringIO()
        saved_df.to_csv(csv_buffer, index=False)
        csv_download = csv_buffer.getvalue().encode("utf-8")
        
        st.download_button(
            "Download All Responses as CSV",
            csv_download,
            "ksheersagar_survey_responses.csv",
            "text/csv"
        )
        st.balloons()
    if st.button("Start New Survey"):
        for key in ["step", "responses"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
