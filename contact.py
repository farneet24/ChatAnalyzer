import streamlit as st
import requests
import re

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Define the form
st.set_page_config(
    page_title="Contact Us Form",
    page_icon="notes.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title('WhatsApp Chat Analyzer')
        


st.success("Got a question? We'd love to hear from you. Send us a message and we'll respond as soon as possible.")

st.markdown("<h1 style='text-align: center;'>Contact Us</h1>", unsafe_allow_html=True)

with st.form(key='my_form'):

    occupation = st.selectbox(label='What can we help you with?', options=['Select', 'I want to report a bug', 'I have a suggestion', 'Other'])

    name = st.text_input(label='Name')
    email = st.text_input(label='Email')
    text = st.text_area("Message")
    submit_button = st.form_submit_button(label='Submit')

# Process the form data
if submit_button:

    if occupation == 'Select':
            st.error("Please select the reason")
    if not name:
            st.error('Please enter your name')
    if not email:
            st.error('Please enter your email')
    if not text:
            st.error('Please enter a message')

    if name and email and text and occupation != 'Select':
    # Send the form data to FormsPree
        data = {'Name': name, 'Email': email, 'Purpose': occupation, 'Message' : text}
        response = requests.post('https://formspree.io/f/xdovznoy', data=data)

        if email and not re.match(email_regex, email):
            st.error('Please enter a valid email address')
        # Display a success message
        if response.status_code == 200:
            st.success('Form submitted successfully.')
        else:
            st.error('Error submitting form.')

