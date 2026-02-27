import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from calculator import calculate_meeting_cost, format_currency
import json

st.set_page_config(page_title="Meeting Cost Calculator", layout="wide")

st.title("💰 Meeting Cost Calculator")
st.subheader("See how much your meetings actually cost")

# Country selection
col1, col2 = st.columns(2)
with col1:
    country = st.selectbox("Country", ["UK", "USA"])
with col2:
    currency = "£" if country == "UK" else "$"

# Load roles
with open(f'data/salaries_{country.lower()}.json') as f:
    salary_data = json.load(f)

roles = list(salary_data['roles'].keys())

st.divider()

# Attendees section
st.header("👥 Attendees")

attendees = []
for i in range(5):
    cols = st.columns([3, 1, 2])
    with cols[0]:
        role = st.selectbox(f"Role {i+1}", ["None"] + roles, key=f"role_{i}")
    with cols[1]:
        count = st.number_input(f"Count", min_value=1, max_value=10, value=1, key=f"count_{i}")
    with cols[2]:
        if role != "None":
            rate = salary_data['roles'][role]['hourly_rate']
            st.write(f"{currency}{rate}/hr")
            attendees.append((role, count))

st.divider()

# Meeting duration
st.header("⏱️ Meeting Details")
col1, col2 = st.columns(2)
with col1:
    duration = st.slider("Duration (hours)", 0.5, 8.0, 1.0, 0.5)
with col2:
    st.write(f"**{duration} hours**")
    st.write(f"**{int(duration * 60)} minutes**")

# Overheads
st.header("💸 Overheads")
col1, col2, col3 = st.columns(3)
with col1:
    room_cost = st.number_input("Room/venue", min_value=0, value=50)
with col2:
    catering_cost = st.number_input("Catering", min_value=0, value=30)
with col3:
    tech_cost = st.number_input("Tech/tools", min_value=0, value=20)

overheads = {
    'room': room_cost,
    'catering': catering_cost,
    'tech': tech_cost
}

st.divider()

# Calculate
if st.button("🚀 Calculate Cost", type="primary"):
    result = calculate_meeting_cost(attendees, duration, country, overheads)
    
    # Big numbers
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cost", format_currency(result['total_cost'], salary_data['currency']))
    with col2:
        st.metric("Per Minute", format_currency(result['total_cost'] / (duration * 60), salary_data['currency']))
    with col3:
        st.metric("Attendees", result['attendee_count'])
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cost by Role")
        if result['breakdown']:
            df_roles = {
                'Role': [item['role'] for item in result['breakdown']],
                'Cost': [item['cost'] for item in result['breakdown']]
            }
            fig = px.pie(df_roles, values='Cost', names='Role', 
                        title=f"Salary Costs ({currency}{result['salary_cost']:,.2f})")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Cost Breakdown")
        categories = ['Salaries', 'Room', 'Catering', 'Tech']
        values = [result['salary_cost'], overheads['room'], overheads['catering'], overheads['tech']]
        fig = go.Figure(data=[go.Bar(x=categories, y=values)])
        fig.update_layout(title="Total Cost Breakdown", yaxis_title=f"Cost ({currency})")
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown
    st.subheader("📊 Detailed Breakdown")
    for item in result['breakdown']:
        st.write(f"**{item['role']}** x{item['count']}: "
                f"{format_currency(item['cost'], salary_data['currency'])} "
                f"({format_currency(item['hourly_rate'], salary_data['currency'])}/hr × {duration}hrs)")
    
    st.write(f"\n**Overheads:** {format_currency(result['overhead_cost'], salary_data['currency'])}")
    st.write(f"**Total:** {format_currency(result['total_cost'], salary_data['currency'])}")
    
    # The reality check
    st.divider()
    st.header("😬 The Reality Check")
    
    annual_meetings = st.number_input("How many meetings like this per year?", min_value=1, value=50)
    annual_cost = result['total_cost'] * annual_meetings
    
    st.write(f"### If you have {annual_meetings} of these meetings per year:")
    st.write(f"# {format_currency(annual_cost, salary_data['currency'])}")
    st.write("*That's your annual meeting cost for this type of meeting alone.*")
    
    if annual_cost > 50000:
        st.error("🚨 That's more than a full-time salary! Time to audit your meetings.")
    elif annual_cost > 20000:
        st.warning("⚠️ That's a significant chunk of budget. Worth optimizing.")
    else:
        st.success("✅ Relatively manageable, but still worth tracking.")

st.divider()
st.caption("Built to expose the true cost of organisational theatre.")
