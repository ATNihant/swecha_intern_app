import streamlit as st
import pandas as pd
import os

# Define file paths for clarity
USERS_CSV = "data/users.csv"
ISSUES_CSV = "data/issues.csv"

def show_admin_dashboard():
    """
    Displays the main admin dashboard with three tabs:
    1. Intern Dashboard: View and filter registered interns.
    2. Issues: Track and manage active and completed issues.
    3. Raise Issue: Create new issues.
    """
    st.title("👑 Admin Dashboard")

    # Create data directory if it doesn't exist to prevent errors
    if not os.path.exists("data"):
        os.makedirs("data")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 Intern Dashboard", "🛠️ Issues", "🐞 Raise Issue"])

    # ----------------------
    # 📋 Intern Dashboard Tab
    # ----------------------
    with tab1:
        st.subheader("Interns Overview")
        if os.path.exists(USERS_CSV):
            users_df = pd.read_csv(USERS_CSV)
            
            # Create a list of unique colleges for the filter
            colleges = users_df['college'].unique()
            selected_college = st.selectbox("Select College", ["All"] + list(colleges))

            # Filter dataframe based on selection
            if selected_college != "All":
                filtered_df = users_df[users_df["college"] == selected_college]
            else:
                filtered_df = users_df

            st.dataframe(filtered_df[["name", "email", "role", "college"]], use_container_width=True)
        else:
            st.info("No interns have registered yet.")

    # ----------------------
    # 🛠️ Issues Dashboard Tab
    # ----------------------
    with tab2:
        st.subheader("Issue Tracking")

        if os.path.exists(ISSUES_CSV):
            issues_df = pd.read_csv(ISSUES_CSV)

            # Create sub-tabs for views
            view1, view2, view3 = st.tabs(["🔍 Filtered View", "📊 Table View", "📈 Graph View"])

            # --------------------
            # 🔍 Filtered View
            # --------------------
            with view1:
                st.markdown("### Filter and Search Issues")
                show_completed = st.checkbox("Show completed issues", value=False)

                # Filter by status
                filtered_df = issues_df if show_completed else issues_df[issues_df["status"] != "Completed"]

                # Filter by difficulty
                difficulty_filter = st.multiselect(
                    "Filter by Difficulty", ["Easy", "Medium", "Hard"], default=["Easy", "Medium", "Hard"]
                )
                filtered_df = filtered_df[filtered_df["difficulty"].isin(difficulty_filter)]

                # Search by title
                search_query = st.text_input("Search by Issue Title").lower()
                if search_query:
                    filtered_df = filtered_df[filtered_df["title"].str.lower().str.contains(search_query)]

                st.write(f"🔎 {len(filtered_df)} issues matched.")
                if not filtered_df.empty:
                    for index, row in filtered_df.iloc[::-1].iterrows():
                        st.markdown(f"**#{row['id']}** — {row['title']} ({row['difficulty']})")
                        st.write(row["description"])
                        st.write(f"Status: `{row['status']}` | Assigned To: {row.get('assigned_to', 'N/A')} | Submitter: {row.get('submitter', 'N/A')}")

                        if row["status"] == "Merge Request Submitted":
                            if st.button(f"✅ Mark as Completed", key=f"complete_filtered_{row['id']}"):
                                issues_df.loc[issues_df['id'] == row['id'], "status"] = "Completed"
                                issues_df.to_csv(ISSUES_CSV, index=False)
                                st.success(f"Issue #{row['id']} marked as Completed.")
                                st.rerun()
                        st.markdown("---")
                else:
                    st.info("No issues matched the filters.")

            # --------------------
            # 📊 Table View
            # --------------------
            with view2:
                st.markdown("### Full Issues Table")
                st.dataframe(issues_df, use_container_width=True, hide_index=True)

            # --------------------
            # 📈 Graph View
            # --------------------
            with view3:
                st.markdown("### 📊 Issues Insights Dashboard")

                import altair as alt

                if not issues_df.empty:
                    # Use consistent color schemes for clarity
                    difficulty_color_scale = alt.Scale(domain=["Easy", "Medium", "Hard"],
                                                    range=["#A1D99B", "#FC9272", "#9ECAE1"])
                    status_color_scale = alt.Scale(domain=["Open", "Merge Request Submitted", "Completed"],
                                                range=["#FEC44F", "#74C476", "#6BAED6"])

                    # --- Donut Chart for Difficulty ---
                    difficulty_data = issues_df.groupby("difficulty").size().reset_index(name="count")

                    difficulty_chart = alt.Chart(difficulty_data).mark_arc(innerRadius=60, outerRadius=100).encode(
                        theta=alt.Theta("count:Q", title=""),
                        color=alt.Color("difficulty:N", scale=difficulty_color_scale, legend=alt.Legend(title="Difficulty")),
                        tooltip=[alt.Tooltip("difficulty:N", title="Difficulty"),
                                alt.Tooltip("count:Q", title="Number of Issues")]
                    ).properties(
                        title={"text": "Issue Distribution by Difficulty", "fontSize": 16, "subtitleFontSize": 12},
                        width=300,
                        height=300
                    )

                    # --- Donut Chart for Status ---
                    status_data = issues_df.groupby("status").size().reset_index(name="count")

                    status_chart = alt.Chart(status_data).mark_arc(innerRadius=60, outerRadius=100).encode(
                        theta=alt.Theta("count:Q", title=""),
                        color=alt.Color("status:N", scale=status_color_scale, legend=alt.Legend(title="Status")),
                        tooltip=[alt.Tooltip("status:N", title="Status"),
                                alt.Tooltip("count:Q", title="Number of Issues")]
                    ).properties(
                        title={"text": "Issue Distribution by Status", "fontSize": 16, "subtitleFontSize": 12},
                        width=300,
                        height=300
                    )

                    # Display both charts side-by-side
                    st.altair_chart(difficulty_chart | status_chart, use_container_width=True)

                else:
                    st.info("No issues to visualize.")



    # ----------------------
    # 🐞 Raise New Issue Tab
    # ----------------------
    with tab3:
        st.subheader("Raise a New Issue")

        # --- Improvement: Load data only once per run ---
        if os.path.exists(ISSUES_CSV):
            issues_df = pd.read_csv(ISSUES_CSV)
        else:
            issues_df = pd.DataFrame(columns=["id", "title", "description", "difficulty", "status", "assigned_to", "submitter"])

        # --- Improvement: Use clear_on_submit for better UX ---
        with st.form("raise_issue_form", clear_on_submit=True):
            title = st.text_input("Issue Title")
            description = st.text_area("Issue Description")
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            submit_button = st.form_submit_button("Raise Issue")

            if submit_button:
                # --- Improvement: Basic validation ---
                if not title:
                    st.warning("Please enter a title for the issue.")
                else:
                    # Determine the next available ID
                    new_id = issues_df["id"].max() + 1 if not issues_df.empty else 1

                    # Create a new DataFrame for the new issue
                    new_issue = pd.DataFrame([{
                        "id": new_id,
                        "title": title,
                        "description": description,
                        "difficulty": difficulty,
                        "status": "Open",
                        "assigned_to": "",
                        "submitter": "Admin"
                    }])

                    # Append new issue and save to CSV
                    issues_df = pd.concat([issues_df, new_issue], ignore_index=True)
                    issues_df.to_csv(ISSUES_CSV, index=False)

                    # Signal to other tabs that an issue was added (optional but good practice)
                    st.session_state.new_issue_added = True
                    st.success("✅ Issue raised successfully!")


# Example of how to run the dashboard (optional, for standalone execution)
if __name__ == "__main__":
    show_admin_dashboard()