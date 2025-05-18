import streamlit as st
import json
from datetime import datetime

# Session-based group data
if 'groups' not in st.session_state:
    st.session_state.groups = {}

st.title("💸 PiSplit – Splitwise with Pi Coin")

# Sidebar – Group controls
st.sidebar.header("➕ Create / Select Group")
group_name = st.sidebar.text_input("Group Name")
members_input = st.sidebar.text_input("Members (comma-separated)")

if st.sidebar.button("Create Group"):
    members = [m.strip() for m in members_input.split(",") if m.strip()]
    st.session_state.groups[group_name] = {
        "members": members,
        "expenses": []
    }
    st.sidebar.success(f"Group '{group_name}' created!")

group_list = list(st.session_state.groups.keys())
selected_group = st.sidebar.selectbox("Select a group", group_list)

# Add Expense
if selected_group:
    st.subheader(f"Group: {selected_group}")
    st.markdown("### ➕ Add Expense")

    payer = st.selectbox("Who paid?", st.session_state.groups[selected_group]["members"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    description = st.text_input("Description")

    if st.button("Add Expense"):
        members = st.session_state.groups[selected_group]["members"]
        share = round(amount / len(members), 2)
        split = {}
        for m in members:
            if m == payer:
                split[m] = round(amount - share, 2) * -1
            else:
                split[m] = share

        expense = {
            "payer": payer,
            "amount": amount,
            "description": description,
            "split": split,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.session_state.groups[selected_group]["expenses"].append(expense)
        st.success("Expense added!")

    # Display Expenses
    st.markdown("### 📄 Expense History")
    for i, expense in enumerate(st.session_state.groups[selected_group]["expenses"], 1):
        st.markdown(f"**{i}. {expense['description']} (₹{expense['amount']})** by {expense['payer']} – {expense['timestamp']}")
        for user, val in expense["split"].items():
            st.markdown(f"- {user}: ₹{val}")

    # Calculate Balance
    st.markdown("### 💰 Net Balances")
    balances = {m: 0.0 for m in st.session_state.groups[selected_group]["members"]}
    for exp in st.session_state.groups[selected_group]["expenses"]:
        for m, v in exp["split"].items():
            balances[m] += v

    for m, b in balances.items():
        status = "gets back" if b > 0 else "owes"
        st.markdown(f"- **{m}** {status} ₹{abs(round(b, 2))}")

# Future: Add Pi SDK Simulation
st.markdown("---")
st.markdown("👨‍💻 _Phase 6_: Pi Coin payment integration coming soon...")
