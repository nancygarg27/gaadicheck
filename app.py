import streamlit as st
from anomaly import get_vehicle_details, get_vehicle_id_by_plate_number
from trust_score import calculate_trust_score

st.set_page_config(
    page_title = "GaadiCheck",
    page_icon = "🚗",
    layout = "centered"
)

st.markdown("<h1 style = 'text-align : center; margin-bottom : 0;'>GaddiCheck</h1>", unsafe_allow_html=True)

st.markdown("<p style = 'text-align : center; color : grey; font-size : 18px; margin-top : 0;'>Second-hand car? Get the first-hand truth.</p>", unsafe_allow_html=True)

st.divider()

col1, col2, col3 = st.columns([1,3,1])

with col2:
    plate = st.text_input(
        "Registration Number",
        placeholder = "e.g. MH 12 AB 1234"
    )
    check = st.button("Check this car", use_container_width = True)

if check:
    if not plate.strip():
        st.warning("Enter the Plate Number please!")
    else:
        vehicle_id = get_vehicle_id_by_plate_number(plate)
        if vehicle_id is None:
            st.error("This car's data does not exist in our database")
        else:
            vehicle = get_vehicle_details(vehicle_id)
            score, status, reasons = calculate_trust_score(vehicle_id)

            colors = {"Green": "#2e9e4f", "Yellow": "#e0a800", "Red": "#d63031"}
            color = colors[status]

            st.markdown(
                f"<div style='text-align:center; padding:20px; border-radius:12px; "
                f"background:{color}22; border:2px solid {color};'>"
                f"<p style='margin:0; font-size:18px;'>Trust Score</p>"
                f"<h1 style='margin:0; font-size:64px; color:{color};'>{score}/100</h1>"
                f"<p style='margin:0; font-size:22px; font-weight:600; color:{color};'>{status}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

            st.subheader(f"{vehicle.company} {vehicle.model}")
            st.write(f"Year: {vehicle.year}  |  Fuel: {vehicle.fuel_type}  |  Plate: {vehicle.plate_number}")
            st.subheader("Why this score?")
            if not reasons:
                st.success("No red flags found. This car has zero problems.")
            else:
                for reason in reasons:
                    st.error(reason)

