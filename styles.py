import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .metric-card {
            background-color: #262730;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .stock-header {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .data-table {
            font-size: 0.9rem;
        }
        .stDownloadButton {
            background-color: #FF4B4B;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.3rem;
            border: none;
            cursor: pointer;
        }
        .insight-card {
            background-color: #262730;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .insight-header {
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .insight-timestamp {
            color: #666;
            font-size: 0.8rem;
        }
        .insight-actions {
            margin-top: 0.5rem;
        }
        .sentiment-indicator {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 0.2rem;
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }
        .share-button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.3rem;
            border: none;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)