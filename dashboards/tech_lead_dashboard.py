import streamlit as st
import pandas as pd
import altair as alt
import os

USERS_CSV = "data/users.csv"
ISSUES_CSV = "data/issues.csv"
HELP_REQUESTS_CSV = "data/help_requests.csv"

def show_tech_lead_dashboard(college_name):
    if "name" not in st.session_state or not st.session_state.name:
        st.session_state.name = st.text_input("Enter your name")
        st.stop()

    if "role" not in st.session_state:
        st.session_state.role = "Tech Lead"

    tech_lead_label = f"Tech Lead - {st.session_state.name}"
    st.title("🧑‍🏫 Tech Lead Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Interns", "🛠 Issues & Help", "📄 My Issues", "🐞 Raise Issue"])

    # ------------------- 👥 Interns Tab -------------------
    with tab1:
        st.subheader(f"AI Developers from {college_name}")
        if os.path.exists(USERS_CSV):
            users_df = pd.read_csv(USERS_CSV)
            filtered = users_df[(users_df["college"] == college_name) & (users_df["role"] == "AI Developer")]
            if not filtered.empty:
                st.dataframe(filtered[["name", "email", "college"]], use_container_width=True)
            else:
                st.info("No AI developers registered for your college.")
        else:
            st.warning("No data available.")

    # ------------------- 🛠 Issues & Help Tab -------------------
    with tab2:
        st.subheader("🛠 Issues")
        tab_prog, tab_help, tab_table, tab_charts = st.tabs(["📂 Program Issues", "🙋 Help Requests", "📋 All Issues", "📊 Charts"])

        # 📂 Program Issues
        with tab_prog:
            st.markdown("### 🔍 Pending Program Issues")
            if os.path.exists(ISSUES_CSV):
                issues_df = pd.read_csv(ISSUES_CSV)
            else:
                issues_df = pd.DataFrame(columns=["id", "title", "description", "difficulty", "status", "assigned_to", "submitter"])

            pending_df = issues_df[issues_df["status"].isin(["Open", "In Progress"])]
            difficulty_filter = st.multiselect("Filter by Difficulty", options=issues_df["difficulty"].unique(), default=issues_df["difficulty"].unique())
            keyword = st.text_input("Search by keyword in title/description")

            filtered_df = pending_df[
                pending_df["difficulty"].isin(difficulty_filter) &
                (
                    pending_df["title"].str.contains(keyword, case=False, na=False) |
                    pending_df["description"].str.contains(keyword, case=False, na=False)
                )
            ]

            if not filtered_df.empty:
                for index, row in filtered_df.iterrows():
                    st.markdown(f"**#{row['id']}** — {row['title']} ({row['difficulty']})")
                    st.write(row["description"])
                    st.write(f"Status: `{row['status']}` | Assigned To: {row['assigned_to'] or 'Unassigned'} | Submitter: {row['submitter']}")

                    if row["status"] == "Open":
                        if st.button(f"🟡 Mark In Progress - Issue #{row['id']}", key=f"inprogress-{row['id']}"):
                            issues_df.at[index, "status"] = "In Progress"
                            issues_df.at[index, "assigned_to"] = tech_lead_label
                            issues_df.to_csv(ISSUES_CSV, index=False)
                            st.success(f"Issue #{row['id']} marked In Progress.")
                            st.rerun()
                    elif row["status"] == "In Progress" and row["assigned_to"] == tech_lead_label:
                        if st.button(f"🔁 Submit Merge Request - Issue #{row['id']}", key=f"mr-{row['id']}"):
                            issues_df.at[index, "status"] = "Merge Request Submitted"
                            issues_df.to_csv(ISSUES_CSV, index=False)
                            st.success(f"Issue #{row['id']} marked as Merge Request Submitted.")
                            st.rerun()
                    st.divider()
            else:
                st.info("No matching pending issues.")

        # 🙋 Help Requests
        with tab_help:
            st.markdown("### 🙋 General Developer Help Requests")
            if os.path.exists(HELP_REQUESTS_CSV):
                help_df = pd.read_csv(HELP_REQUESTS_CSV)
                if not help_df.empty:
                    st.dataframe(help_df[["developer", "email", "query"]], use_container_width=True, hide_index=True)
                else:
                    st.info("No help requests found.")
            else:
                st.info("No help requests submitted yet.")

        # 📋 All Issues Table
        with tab_table:
            st.markdown("### 📋 All Issues")
            if os.path.exists(ISSUES_CSV):
                issues_df = pd.read_csv(ISSUES_CSV)
                st.dataframe(issues_df, use_container_width=True, hide_index=True)
            else:
                st.info("No issues available.")

        # 📊 Donut Charts
        with tab_charts:
            st.markdown("### 📊 Issue Insights")
            if os.path.exists(ISSUES_CSV):
                issues_df = pd.read_csv(ISSUES_CSV)
                if not issues_df.empty:
                    difficulty_data = issues_df.groupby("difficulty").size().reset_index(name="count")
                    status_data = issues_df.groupby("status").size().reset_index(name="count")

                    difficulty_chart = alt.Chart(difficulty_data).mark_arc(innerRadius=60).encode(
                        theta="count:Q",
                        color=alt.Color("difficulty:N"),
                        tooltip=["difficulty:N", "count:Q"]
                    ).properties(title="By Difficulty", width=300, height=300)

                    status_chart = alt.Chart(status_data).mark_arc(innerRadius=60).encode(
                        theta="count:Q",
                        color=alt.Color("status:N"),
                        tooltip=["status:N", "count:Q"]
                    ).properties(title="By Status", width=300, height=300)

                    st.altair_chart(difficulty_chart | status_chart, use_container_width=True)
                else:
                    st.info("No data to visualize.")
            else:
                st.info("Issue file not found.")

    # ------------------- 📄 My Issues Tab -------------------
    with tab3:
        st.subheader("📄 Issues Assigned to You")

        if os.path.exists(ISSUES_CSV):
            issues_df = pd.read_csv(ISSUES_CSV)
            my_issues = issues_df[issues_df["assigned_to"] == tech_lead_label]

            if my_issues.empty:
                st.info("You haven’t claimed or been assigned any issues yet.")
            else:
                for index, row in my_issues.iterrows():
                    st.markdown(f"**#{row['id']}** — {row['title']} ({row['difficulty']})")
                    st.write(row["description"])
                    st.write(f"Status: `{row['status']}`")

                    if row["status"] == "In Progress":
                        if st.button(f"🔁 Submit Merge Request - Issue #{row['id']}", key=f"techlead-mr-{row['id']}"):
                            issues_df.at[index, "status"] = "Merge Request Submitted"
                            issues_df.to_csv(ISSUES_CSV, index=False)
                            st.success(f"Issue #{row['id']} marked as Merge Request Submitted.")
                            st.rerun()

                    elif row["status"] == "Merge Request Submitted":
                        if st.button(f"✅ Mark Completed - Issue #{row['id']}", key=f"techlead-complete-{row['id']}"):
                            issues_df.at[index, "status"] = "Completed"
                            issues_df.to_csv(ISSUES_CSV, index=False)
                            st.success(f"Issue #{row['id']} marked as Completed.")
                            st.rerun()

                    st.divider()

                # Insights
                total = len(my_issues)
                completed = len(my_issues[my_issues["status"] == "Completed"])
                merge_ready = len(my_issues[my_issues["status"] == "Merge Request Submitted"])
                in_progress = len(my_issues[my_issues["status"] == "In Progress"])
                completion_rate = round((completed / total) * 100, 2) if total > 0 else 0.0

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Assigned", total)
                col2.metric("Completed", completed)
                col3.metric("Completion Rate", f"{completion_rate}%")

                chart_data = my_issues.groupby(["difficulty", "status"]).size().unstack(fill_value=0)
                st.bar_chart(chart_data)
        else:
            st.info("No issues available.")

    # ------------------- 🐞 Raise Issue Tab -------------------
    with tab4:
        st.subheader("Raise a New Issue")
        if os.path.exists(ISSUES_CSV):
            issues_df = pd.read_csv(ISSUES_CSV)
        else:
            issues_df = pd.DataFrame(columns=["id", "title", "description", "difficulty", "status", "assigned_to", "submitter"])

        with st.form("raise_issue_techlead_form", clear_on_submit=True):
            title = st.text_input("Issue Title")
            description = st.text_area("Issue Description")
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            submit_button = st.form_submit_button("Raise Issue")

            if submit_button:
                if not title:
                    st.warning("Please enter a title for the issue.")
                else:
                    new_id = issues_df["id"].max() + 1 if not issues_df.empty else 1
                    new_issue = pd.DataFrame([{
                        "id": new_id,
                        "title": title,
                        "description": description,
                        "difficulty": difficulty,
                        "status": "Open",
                        "assigned_to": "",
                        "submitter": st.session_state.name
                    }])
                    issues_df = pd.concat([issues_df, new_issue], ignore_index=True)
                    issues_df.to_csv(ISSUES_CSV, index=False)
                    st.success("✅ Issue raised successfully!")

        st.divider()
        st.subheader("All Raised Issues")
        if not issues_df.empty:
            st.dataframe(issues_df.iloc[::-1], use_container_width=True, hide_index=True)
        else:
            st.info("No issues raised yet.")
