import json
from datetime import date

import plotly.express as px
import streamlit as st

# Initialize session state
if "projects" not in st.session_state:
    st.session_state.projects = []

if "progress_data" not in st.session_state:
    st.session_state.progress_data = {
        "Element": ["Foundation", "Substructure", "Superstructure", "Finishes"],
        "Completion (%)": [0, 0, 0, 0],
        "Last Updated": ["-", "-", "-", "-"],
    }

if "financial_data" not in st.session_state:
    st.session_state.financial_data = {
        "Element": ["Foundation", "Substructure", "Superstructure", "Finishes"],
        "Claimable Amount (RM)": [0, 0, 0, 0],
        "Total Claimable (RM)": 0,
    }

# Convert to DataFrames
df_progress = pd.DataFrame(st.session_state.progress_data)
df_financial = pd.DataFrame(st.session_state.financial_data)

# Helper function to calculate claimable amounts
def calculate_financials(progress_df):
    claimable_amounts = []
    total_claimable = 0
    for _, row in progress_df.iterrows():
        claimable = (row["Completion (%)"] / 100) * 100000  # Assuming total project value = RM100k
        claimable_amounts.append(claimable)
        total_claimable += claimable
    return claimable_amounts, total_claimable


# Streamlit App Structure
st.title("Welcome to the Civitas Dashboard!")

# Login/Registration Section
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False

if not st.session_state.user_logged_in:
    st.subheader("Login or Register")
    user_option = st.radio("Choose an option:", ["Login", "Register"])
    
    if user_option == "Register":
        username = st.text_input("Create Username")
        password = st.text_input("Create Password", type="password")
        if st.button("Register"):
            st.session_state.user_logged_in = True
            st.success(f"Welcome, {username}! Your account has been created.")
    
    if user_option == "Login":
        username = st.text_input("Enter Username")
        password = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            st.session_state.user_logged_in = True
            st.success(f"Welcome back, {username}!")

else:
    # Main Dashboard Navigation
    options = ["Home", "New Project Registration", "Existing Projects"]
    choice = st.sidebar.radio("Navigate to:", options)

    # Home Section
    if choice == "Home":
        st.header("Civitas Dashboard Overview")
        st.write("""
        Manage your construction projects effectively with progress tracking, financials, 
        task management, and more. Use the navigation menu to explore different sections.
        """)

    # New Project Registration Section
    elif choice == "New Project Registration":
        st.header("Register a New Project")
        project_name = st.text_input("Project Name")
        project_description = st.text_area("Project Description")
        project_budget = st.number_input("Project Budget (RM)", min_value=0)
        
        if st.button("Register Project"):
            new_project = {
                "name": project_name,
                "description": project_description,
                "budget": project_budget,
                "progress_data": df_progress.copy(),
                "financial_data": df_financial.copy()
            }
            st.session_state.projects.append(new_project)
            st.success(f"Project '{project_name}' has been successfully registered!")

    # Existing Projects Section
    elif choice == "Existing Projects":
        st.header("Manage Existing Projects")
        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a project to manage:", project_names)
            project = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            tabs = ["Project Information & Details", "Progress Tracking", "Financials"]
            selected_tab = st.radio("Choose a section:", tabs)

            # Project Information & Details Tab
            if selected_tab == "Project Information & Details":
                st.subheader("Project Information")
                st.write(f"**Name:** {project['name']}")
                st.write(f"**Description:** {project['description']}")
                st.write(f"**Budget:** RM {project['budget']:.2f}")

            # Progress Tracking Tab
            elif selected_tab == "Progress Tracking":
                st.subheader("Progress Tracking")
                st.write("Update progress for each building element:")

                # Display editable progress table
                edited_df = st.experimental_data_editor(project["progress_data"], use_container_width=True)

                if st.button("Save Progress"):
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    edited_df["Last Updated"] = now
                    project["progress_data"] = edited_df
                    st.success("Progress updated successfully!")

                # Overall progress bar
                overall_progress = edited_df["Completion (%)"].mean()
                st.progress(overall_progress / 100)
                st.metric("Overall Project Progress", f"{overall_progress:.2f}%")

            # Financials Tab
            elif selected_tab == "Financials":
                st.subheader("Financial Overview")
                st.write("Financial calculations based on project progress:")

                # Calculate financials
                progress_df = pd.DataFrame(project["progress_data"])
                claimable_details, total_claimable = calculate_financials(progress_df)
                financial_data = project["financial_data"]
                financial_data["Claimable Amount (RM)"] = claimable_details
                financial_data["Total Claimable (RM)"] = total_claimable
                project["financial_data"] = financial_data

                # Display financial data
                st.write("Financial Summary:")
                st.write(pd.DataFrame(financial_data))

                # Display total claimable amount
                st.metric("Total Claimable Amount", f"RM {total_claimable:.2f}")
        else:
            st.warning("No projects registered yet! Please register a new project.")

# Footer
st.sidebar.info("Civitas Dashboard © 2024")
