!pip install streamlit pyngrok

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="PiSplit - Splitwise with Pi", layout="wide")

# Inject Pi Wallet JS SDK (runs only in Pi Browser)
components.html(
    """
    <script src='https://sdk.minepi.com/pi-sdk.js'></script>
    <script>
        Pi.init({ version: "2.0" });
        const scopes = ['payments'];
        function onIncompletePaymentFound(payment) {
            console.log("Incomplete payment", payment);
        }
        Pi.authenticate(scopes, onIncompletePaymentFound)
            .then(auth => {
                window.parent.postMessage({type: 'pi_auth', payload: auth}, "*");
            })
            .catch(error => console.error("Auth failed", error));
    </script>
    """,
    height=0
)

# Sample session data
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "friends" not in st.session_state:
    st.session_state.friends = ["Alice", "Bob", "Charlie"]
if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "Bharath Reddy Ambati",
        "email": "bharath@example.com",
        "photo": "https://via.placeholder.com/100",
        "auth_type": "Pi Network",
        "notifications": True
    }

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Dashboard", "Friends", "Activity", "Profile"])

# 1. Dashboard
if page == "Dashboard":
    st.title("📊 Dashboard")
    st.markdown("### Payables and Receivables Summary")

    net_balances = {f: 0 for f in st.session_state.friends}
    for exp in st.session_state.expenses:
        for user, val in exp["split"].items():
            net_balances[user] = net_balances.get(user, 0) + val

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Receivables")
        for user, val in net_balances.items():
            if val < 0:
                st.markdown(f"- {user} owes ₹{abs(val):.2f}")
    with col2:
        st.subheader("Payables")
        for user, val in net_balances.items():
            if val > 0:
                st.markdown(f"- You owe {user} ₹{val:.2f}")

    st.markdown("### 💹 Expense Graph")
    df = pd.DataFrame(st.session_state.expenses)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["amount"] = df["amount"].astype(float)
        df = df.sort_values("timestamp")
        df.set_index("timestamp")[["amount"]].plot(kind="bar", figsize=(10,4), title="Monthly Spending")
        st.pyplot()

# 2. Friends
elif page == "Friends":
    st.title("👥 Friends")
    st.markdown("### Total with Each Friend")

    net_balances = {f: 0 for f in st.session_state.friends}
    for exp in st.session_state.expenses:
        for user, val in exp["split"].items():
            net_balances[user] = net_balances.get(user, 0) + val

    for user in st.session_state.friends:
        status = "gets back" if net_balances[user] > 0 else "owes"
        st.markdown(f"- **{user}** {status} ₹{abs(net_balances[user]):.2f}")

# 3. Activity
elif page == "Activity":
    st.title("📜 Activity Log")
    st.markdown("### Filter transactions by friend or date")

    df = pd.DataFrame(st.session_state.expenses)
    if not df.empty:
        friend_filter = st.selectbox("Filter by friend", ["All"] + st.session_state.friends)
        date_filter = st.date_input("Date", value=datetime.today())
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        if friend_filter != "All":
            df = df[df["payer"] == friend_filter]
        df = df[df["timestamp"].dt.date == date_filter]
        st.write(df)

# 4. Profile
elif page == "Profile":
    st.title("🙋 Profile")
    profile = st.session_state.profile
    st.image(profile["photo"], width=100)
    st.write(f"**Name:** {profile['name']}")
    st.write(f"**Email:** {profile['email']}")
    st.write(f"**Authentication Type:** {profile['auth_type']}")
    st.checkbox("Enable Notifications", value=profile["notifications"])

with open("app.py", "w") as f:
    f.write("""<PASTE FULL CODE HERE>""")

from pyngrok import ngrok
!streamlit run app.py &>/content/log.txt &
print(ngrok.connect(8501))

