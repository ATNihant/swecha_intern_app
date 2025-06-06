import streamlit as st
import pandas as pd
import os

HELP_REQUESTS_CSV = "data/help_requests.csv"
ISSUES_CSV = "data/issues.csv"

def show_ai_developer_dashboard(current_user_email):
    st.title("🤖 AI Developer Dashboard")

    developer_name = st.session_state.get("name", current_user_email)
    assigned_label = f"AI Developer - {developer_name}"

    if os.path.exists(ISSUES_CSV):
        issues_df = pd.read_csv(ISSUES_CSV)
    else:
        issues_df = pd.DataFrame(columns=["id", "title", "description", "difficulty", "status", "assigned_to", "submitter"])

    tab1, tab2, tab3, tab4 = st.tabs(["🛠 Issues", "📈 My Issues", "📊 My Insights", "🙋 Request Tech Lead Help"])

    # ───────────── Tab 1: All Issues with Claim Button ───────────── #
    with tab1:
        st.subheader("Browse & Claim Issues")

        st.markdown("### 🔍 Filter Issues")
        status_filter = st.selectbox("Filter by Status", options=["All", "Open", "In Progress", "Completed"])
        difficulty_filter = st.multiselect("Filter by Difficulty", options=issues_df["difficulty"].dropna().unique().tolist())

        filtered_issues = issues_df.copy()
        if status_filter != "All":
            filtered_issues = filtered_issues[filtered_issues["status"] == status_filter]
        if difficulty_filter:
            filtered_issues = filtered_issues[filtered_issues["difficulty"].isin(difficulty_filter)]

        if filtered_issues.empty:
            st.info("No issues match your filters.")
        else:
            for index, row in filtered_issues.iterrows():
                st.markdown(f"**#{row['id']}** — {row['title']} ({row['difficulty']})")
                st.write(row["description"])
                st.write(f"Status: `{row['status']}` | Assigned To: {row['assigned_to'] or 'Unassigned'}")

                # ✅ FIX: Properly check if unassigned
                if row["status"] == "Open" and (pd.isna(row["assigned_to"]) or row["assigned_to"] == ""):
                    if st.button(f"🟡 Start Working on Issue #{row['id']}", key=f"start-{row['id']}"):
                        issues_df.at[index, "status"] = "In Progress"
                        issues_df.at[index, "assigned_to"] = assigned_label
                        issues_df.to_csv(ISSUES_CSV, index=False)
                        st.success(f"Issue #{row['id']} assigned to you.")
                        st.rerun()

                st.divider()

    # ───────────── Tab 2: My Assigned Issues ───────────── #
    with tab2:
        st.subheader("📄 Your Assigned Issues")

        my_issues = issues_df[issues_df["assigned_to"] == assigned_label]

        if my_issues.empty:
            st.info("You haven’t claimed or been assigned any issues yet.")
        else:
            for index, row in my_issues.iterrows():
                st.markdown(f"**#{row['id']}** — {row['title']} ({row['difficulty']})")
                st.write(row["description"])
                st.write(f"Status: `{row['status']}`")

                if row["status"] == "In Progress":
                    if st.button(f"✅ Mark Completed - Issue #{row['id']}", key=f"complete-{row['id']}"):
                        issues_df.at[index, "status"] = "Completed"
                        issues_df.to_csv(ISSUES_CSV, index=False)
                        st.success(f"Issue #{row['id']} marked as completed.")
                        st.rerun()
                st.divider()

    # ───────────── Tab 3: Insights ───────────── #
    with tab3:
        st.subheader("📊 Your Contribution Insights")

        my_issues = issues_df[issues_df["assigned_to"] == assigned_label]
        total = len(my_issues)
        completed = len(my_issues[my_issues["status"] == "Completed"])
        in_progress = len(my_issues[my_issues["status"] == "In Progress"])

        completion_rate = round((completed / total) * 100, 2) if total > 0 else 0.0

        col1, col2, col3 = st.columns(3)
        col1.metric("🧮 Total Assigned", total)
        col2.metric("✅ Completed", completed)
        col3.metric("📈 Completion Rate", f"{completion_rate}%")

        if not my_issues.empty:
            chart_data = my_issues.groupby(["difficulty", "status"]).size().unstack(fill_value=0)
            st.bar_chart(chart_data)
        else:
            st.info("No contribution data yet.")

    # ───────────── Tab 4: Request Help ───────────── #
    with tab4:
        st.subheader("🙋 Request Tech Lead Help")
        st.markdown("This is **not** for project issues. Use this for general doubts or development help.")

        with st.form("help_form"):
            help_query = st.text_area("Describe your issue or ask a question")
            submit = st.form_submit_button("Send Help Request")

            if submit and help_query.strip():
                if os.path.exists(HELP_REQUESTS_CSV):
                    help_df = pd.read_csv(HELP_REQUESTS_CSV)
                else:
                    help_df = pd.DataFrame(columns=["email", "developer", "query", "timestamp"])

                new_row = pd.DataFrame([{
                    "email": current_user_email,
                    "developer": developer_name,
                    "query": help_query.strip(),
                    "timestamp": pd.Timestamp.now()
                }])

                help_df = pd.concat([help_df, new_row], ignore_index=True)
                help_df.to_csv(HELP_REQUESTS_CSV, index=False)
                st.success("✅ Your request has been sent to your Tech Lead.")
