import streamlit as st

st.title("TrafForesight AI 🚦")
st.write("Traffic Prediction System Running")

# simple input
val = st.number_input("Enter value")

if st.button("Predict"):
    st.success(f"Prediction done for input: {val}")
