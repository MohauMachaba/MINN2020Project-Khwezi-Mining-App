import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("NewApp")

st.write("Please enter info to log in")
if st.button("Log in"):
    M = st.text_input("Enter Your Username")
    P = st.text_input("Enter Your Password"")
    st.write("Valid User",M,P)

     st.write("Please enter your data below:")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df)
        fig = px.line(df, x=df.columns[0], y=df.columns[1])
        st.plotly_chart(fig)

if st.button("Sign up"):
       K = st.text_input("Enter Your Email")
       L = st.text_input("Enter Your Password", "")
       st.write("New user signed up successfully", K, L)
