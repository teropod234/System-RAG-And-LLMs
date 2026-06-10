import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def eda():
    st.title("Exploratory Data Analysis (EDA)")

    # Upload dataset
    uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Dataset Preview:")
        st.dataframe(df.head())

        # Show basic statistics
        st.write("Basic Statistics:")
        st.write(df.describe())

        # Show missing values
        st.write("Missing Values:")
        st.write(df.isnull().sum())

        # Show correlation heatmap
        st.write("Correlation Heatmap:")
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
        st.pyplot(plt)