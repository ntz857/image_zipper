import os
import openai
import streamlit as st
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    st.json(openai.Model.list())



if __name__ == "__main__":
    main()
    