import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date, timedelta
from database import (
    initialize_database,
    fetch_data,
    execute_query
)


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="CampusFlow",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================
# DATABASE
# =====================================

initialize_database()


# =====================================
# CUSTOM CSS
# =====================================

def load_css():
    with open("assets/style.css", encoding="utf-8") as file:
        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )


load_css()


# =====================================
# HELPER FUNCTIONS
# =====================================

def heading(title, subtitle):
    st.title(title)
    st.caption(subtitle)
    st.divider()


def show_empty(message):
    st.info(message)


# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("🎓 CampusFlow")

st.sidebar.caption("Your Academic Life. One Smart Dashboard.")

st.sidebar.divider()

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "Study Planner",
        "Study Tracker",
        "Expense Manager",
        "Goal Tracker",
        "Analytics",
        "Reports"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### ✨ Stay Productive")

st.sidebar.caption(
    "Small steps every day lead to big achievements."
)

st.sidebar.divider()

st.sidebar.caption("CampusFlow v1.0 | Python Project")


# =====================================
# 1. DASHBOARD
# =====================================

if page == "Dashboard":

    heading(
        "Welcome to CampusFlow 👋",
        "Your personal academic command center."
    )

    tasks = fetch_data("tasks")
    sessions = fetch_data("study_sessions")
    expenses = fetch_data("expenses")
    goals = fetch_data("goals")

    total_tasks = len(tasks)

    completed = sum(
        t["completed"] for t in tasks
    )

    pending = total_tasks - completed

    hours = sum(
        s["duration"] for s in sessions
    )

    spending = sum(
        e["amount"] for e in expenses
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📚 Total Tasks", total_tasks)
    c2.metric("✅ Completed", completed)
    c3.metric("⏱️ Study Hours", f"{hours:.1f}")
    c4.metric("💰 Expenses", f"₹{spending:,.0f}")

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("📊 Task Completion")

        if total_tasks:

            progress = completed / total_tasks

            st.progress(progress)

            st.write(
                f"{progress * 100:.1f}% completed"
            )

        else:
            show_empty("Start adding your tasks!")

    with right:

        st.subheader("🎯 Your Goals")

        if goals:

            for goal in goals:

                st.write(f"**{goal['title']}**")

                st.progress(
                    min(max(goal["progress"], 0), 100) / 100
                )

        else:
            show_empty("Add your first academic goal!")

    st.divider()

    st.subheader("📅 Upcoming Tasks")

    upcoming = [
        t for t in tasks
        if not t["completed"]
    ]

    upcoming.sort(
        key=lambda x: x["due_date"] or "9999-99-99"
    )

    if upcoming:

        for task in upcoming[:5]:

            st.write(
                f"⏳ **{task['title']}** — "
                f"{task['due_date']} "
                f"({task['priority']})"
            )

    else:
        show_empty("No pending tasks. Great work!")


# =====================================
# 2. STUDY PLANNER
# =====================================

elif page == "Study Planner":

    heading(
        "📚 Study Planner",
        "Organize assignments, subjects and deadlines."
    )

    with st.form("add_task"):

        title = st.text_input("Task Name")

        subject = st.text_input("Subject")

        due = st.date_input(
            "Deadline",
            value=date.today()
        )

        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High"]
        )

        submitted = st.form_submit_button(
            "➕ Add Task",
            use_container_width=True
        )

        if submitted:

            if title.strip():

                execute_query(
                    """
                    INSERT INTO tasks
                    (title, subject, due_date, priority)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        title.strip(),
                        subject.strip(),
                        str(due),
                        priority
                    )
                )

                st.success("Task added!")
                st.rerun()

            else:
                st.error("Task name is required.")

    st.divider()

    st.subheader("Your Assignments")

    tasks = fetch_data("tasks")

    if tasks:

        for task in tasks:

            c1, c2, c3 = st.columns([4, 1, 1])

            with c1:

                status = "✅" if task["completed"] else "⏳"

                st.write(
                    f"{status} **{task['title']}**"
                )

                st.caption(
                    f"{task['subject']} | "
                    f"Due: {task['due_date']} | "
                    f"Priority: {task['priority']}"
                )

            with c2:

                if not task["completed"]:

                    if st.button(
                        "Done",
                        key=f"done_{task['id']}"
                    ):

                        execute_query(
                            "UPDATE tasks SET completed=1 WHERE id=?",
                            (task["id"],)
                        )

                        st.rerun()

            with c3:

                if st.button(
                    "Delete",
                    key=f"delete_task_{task['id']}"
                ):

                    execute_query(
                        "DELETE FROM tasks WHERE id=?",
                        (task["id"],)
                    )

                    st.rerun()

            st.divider()

    else:
        show_empty("No tasks added yet.")


# =====================================
# 3. STUDY TRACKER
# =====================================

elif page == "Study Tracker":

    heading(
        "⏱️ Study Tracker",
        "Record and monitor your daily study sessions."
    )

    with st.form("study_form"):

        subject = st.text_input("Subject Name")

        duration = st.number_input(
            "Study Duration (Hours)",
            min_value=0.5,
            max_value=24.0,
            step=0.5
        )

        study_date = st.date_input(
            "Study Date",
            value=date.today()
        )

        submitted = st.form_submit_button(
            "Save Study Session",
            use_container_width=True
        )

        if submitted:

            if subject.strip():

                execute_query(
                    """
                    INSERT INTO study_sessions
                    (subject, duration, study_date)
                    VALUES (?, ?, ?)
                    """,
                    (
                        subject.strip(),
                        duration,
                        str(study_date)
                    )
                )

                st.success("Study session saved!")
                st.rerun()

            else:
                st.error("Enter a subject name.")

    st.divider()

    sessions = fetch_data("study_sessions")

    if sessions:

        df = pd.DataFrame(sessions)

        st.metric(
            "Total Study Time",
            f"{df['duration'].sum():.1f} hours"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        if st.button("Delete Latest Session"):

            execute_query(
                "DELETE FROM study_sessions WHERE id=?",
                (sessions[0]["id"],)
            )

            st.rerun()

    else:
        show_empty("No study sessions recorded.")


# =====================================
# 4. EXPENSE MANAGER
# =====================================

elif page == "Expense Manager":

    heading(
        "💰 Expense Manager",
        "Keep track of your student budget."
    )

    with st.form("expense_form"):

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Books",
                "Education",
                "Shopping",
                "Other"
            ]
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=1.0,
            step=10.0
        )

        expense_date = st.date_input(
            "Date",
            value=date.today()
        )

        note = st.text_input("Description")

        submitted = st.form_submit_button(
            "Add Expense",
            use_container_width=True
        )

        if submitted:

            execute_query(
                """
                INSERT INTO expenses
                (category, amount, expense_date, note)
                VALUES (?, ?, ?, ?)
                """,
                (
                    category,
                    amount,
                    str(expense_date),
                    note.strip()
                )
            )

            st.success("Expense recorded!")
            st.rerun()

    st.divider()

    expenses = fetch_data("expenses")

    if expenses:

        df = pd.DataFrame(expenses)

        st.metric(
            "Total Spending",
            f"₹{df['amount'].sum():,.2f}"
        )

        fig = px.pie(
            df,
            names="category",
            values="amount",
            hole=0.55,
            title="Expense Distribution",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        if st.button("Delete Latest Expense"):

            execute_query(
                "DELETE FROM expenses WHERE id=?",
                (expenses[0]["id"],)
            )

            st.rerun()

    else:
        show_empty("No expenses recorded yet.")


# =====================================
# 5. GOAL TRACKER
# =====================================

elif page == "Goal Tracker":

    heading(
        "🎯 Goal Tracker",
        "Set goals and track your achievements."
    )

    with st.form("goal_form"):

        title = st.text_input("Goal Name")

        target = st.text_input(
            "Target / Description"
        )

        progress = st.slider(
            "Initial Progress",
            0, 100, 0
        )

        submitted = st.form_submit_button(
            "Create Goal",
            use_container_width=True
        )

        if submitted:

            if title.strip():

                execute_query(
                    """
                    INSERT INTO goals
                    (title, target, progress)
                    VALUES (?, ?, ?)
                    """,
                    (
                        title.strip(),
                        target.strip(),
                        progress
                    )
                )

                st.success("Goal created!")
                st.rerun()

            else:
                st.error("Please enter a goal name.")

    st.divider()

    goals = fetch_data("goals")

    if goals:

        for goal in goals:

            st.subheader(goal["title"])

            st.caption(goal["target"])

            updated = st.slider(
                "Progress",
                0,
                100,
                goal["progress"],
                key=f"goal_{goal['id']}"
            )

            if updated != goal["progress"]:

                execute_query(
                    "UPDATE goals SET progress=? WHERE id=?",
                    (updated, goal["id"])
                )

                st.rerun()

            c1, c2 = st.columns([3, 1])

            with c1:
                st.progress(updated / 100)

            with c2:

                if st.button(
                    "Delete Goal",
                    key=f"del_goal_{goal['id']}"
                ):

                    execute_query(
                        "DELETE FROM goals WHERE id=?",
                        (goal["id"],)
                    )

                    st.rerun()

            st.divider()

    else:
        show_empty("Create your first goal!")


# =====================================
# 6. ANALYTICS
# =====================================

elif page == "Analytics":

    heading(
        "📊 Performance Analytics",
        "Understand your productivity with data."
    )

    sessions = fetch_data("study_sessions")
    tasks = fetch_data("tasks")
    expenses = fetch_data("expenses")

    if sessions:

        df = pd.DataFrame(sessions)

        df["study_date"] = pd.to_datetime(
            df["study_date"]
        )

        fig = px.bar(
            df,
            x="study_date",
            y="duration",
            color="subject",
            title="Study Hours by Date",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        subject_data = (
            df.groupby("subject")["duration"]
            .sum()
            .reset_index()
        )

        fig2 = px.pie(
            subject_data,
            names="subject",
            values="duration",
            hole=0.5,
            title="Time Spent by Subject",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:
        show_empty("Record study sessions to see analytics.")

    st.divider()

    if tasks:

        completed = sum(
            t["completed"] for t in tasks
        )

        pending = len(tasks) - completed

        task_df = pd.DataFrame({
            "Status": ["Completed", "Pending"],
            "Count": [completed, pending]
        })

        fig3 = px.pie(
            task_df,
            names="Status",
            values="Count",
            title="Task Performance",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    else:
        show_empty("Add tasks to see task analytics.")

    if expenses:

        expense_df = pd.DataFrame(expenses)

        fig4 = px.bar(
            expense_df,
            x="expense_date",
            y="amount",
            color="category",
            title="Expense History",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )


# =====================================
# 7. REPORTS
# =====================================

elif page == "Reports":

    heading(
        "📁 Reports & Downloads",
        "Download your CampusFlow data."
    )

    report_options = {
        "Tasks": "tasks",
        "Study Sessions": "study_sessions",
        "Expenses": "expenses",
        "Goals": "goals"
    }

    selected = st.selectbox(
        "Choose Report",
        list(report_options.keys())
    )

    data = fetch_data(report_options[selected])

    if data:

        df = pd.DataFrame(data)

        st.subheader(f"{selected} Report")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name=f"campusflow_{selected.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:
        show_empty("No data available for this report yet.")


# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "CampusFlow © 2026 | Built with Python, "
    "Streamlit, SQLite and Plotly"
)