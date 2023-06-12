import streamlit as st
import seaborn as sns
import pandas as pd
import datetime
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px
from vega_datasets import data
import calendar
import requests
import smtplib
import preprocessor, helper

st.set_page_config(
    page_title="Whatsapp Chat Analyzer",
    page_icon="4017334_circle_logo_media_network_social_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

para = True;

def handle_feedback(feedback):
    if feedback == 'Yes':
        st.write("Thank you for your feedback! We're glad to hear that our tool was useful.")
    elif feedback == 'No':
        st.write("We're sorry to hear that our tool was not useful. Please let us know how we can improve it.")


title = st.title('Analysis will be shown here⬇️')
st.text('\n')
st.text('\n')
st.sidebar.title('WhatsApp Chat Analyzer')
st.sidebar.text('Developed by Farneet Singh')
st.sidebar.text('\n')
st.sidebar.text('\n')

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    
    # Now lets get the data of the file
    data = bytes_data.decode('utf-8')
    # st.text(data)
    df = preprocessor.preprocess(data) # preprocess is the function we made in preprocessor.py
    # st.dataframe(df)

    # Lets find the unique users to make the dropdown
    user_list = df['user'].unique().tolist();

    # We dont want the group notification
    user_list.remove('Group_Notification')
    user_list.sort()
    user_list.insert(0, 'Overall') # To find the overall analysis

    selected_user = st.sidebar.selectbox('Show Analysis with respect to:', user_list)
    
    # Lets make the button
    if st.sidebar.button("Show Analysis"):
        para = False;
        title.title("Detailed Analysis of the Chat")
        col1, col2, col3, col4 = st.columns(4)

        num_messages, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)

        with col1:
            st.header("Total Messages")
            st.title(num_messages) # Gives the number of messages

        with col2:
            st.header("Total Words")
            st.title(num_words)

        with col3:
            st.header('Total Media')
            st.title(num_media)

        with col4:
            st.header('Total Links')
            st.title(num_links)

        if selected_user == 'Overall':
            st.write("\n")
            st.title('Most Busy Users')
            st.write("\n")
            data, percent = helper.most_busy_users(df)
            col1, col2 = st.columns(2)
#             name = data.index
#             count = data.values
            data = data.rename(columns={'count': 'Number of messages'})
            percent = percent.rename(columns={'count': '% of messages'})

            with col1:
                # fig, ax = plt.subplots()
                # ax.bar(name, count)
                # plt.xticks(rotation=40)
                # st.pyplot(fig)
                
                chart = alt.Chart(data).mark_bar().encode(
                    x = 'User:N',
                    y = 'Number of messages:Q',
                    color = alt.Color('User:N', scale=alt.Scale(scheme='inferno'))
                ).properties(
                    height = 500,
                    width = 500
                )

                chart = chart.configure_axis(
                    labelFontSize=0,
                    domain=False,  # hide axis line
                    labelAngle=0,  # set label angle to 0 degrees
                )

                chart = chart.configure_axisY(
                    labelFontSize=12  # set label font size for y-axis
                )

                st.altair_chart(chart)
            
            with col2:
                # st.dataframe(percent, use_container_width=st.session_state.use_container_width)
                table = st.dataframe(percent, width=800)

                # Set the CSS style for the table
                table_style = f"height: 500px;overflow: scroll;"
                table_html = f"<style>div.row-widget.stDataFrame {{ {table_style} }}</style>"
                st.markdown(table_html, unsafe_allow_html=True)
                table_style = f"height: 500px; width: 800px;"

        common = helper.most_commom_words(selected_user, df)
        
        st.write("\n")
        
        if common.empty:
            if selected_user == 'Overall':
                st.title(f"No Common Words")
            else:
                st.title(f"{selected_user} has no common words")

        else:
            if selected_user == 'Overall':
                st.title(f"{selected_user} Most Common Words")
            else:
                st.title(f"{selected_user}'s Most Common Words")
            st.write("\n")
            container = st.container()
            container.markdown(
                f"""
                <style>
                .st-bc {{
                    margin: 0 auto;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )

            # We will use the bar

            scale = alt.Scale(
            domain=list(common['Common Words']),
            range=["#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600"],

            )
            color = alt.Color("Common Words:N", scale=scale)

            # We create two selections:
            # - a brush that is active on the top panel
            # - a multi-click that is active on the bottom panel
            select = alt.selection_multi(name="select", encodings=["color"])

            # Bottom panel is a bar chart of weather type
            bars = (
                alt.Chart(common)
                .mark_bar()
                .encode(
                    x="Frequency:Q",
                    y="Common Words:N",
                    color=alt.condition(select, color, alt.value("lightgray")),
                )
                .properties(
                    width=600,
                    height=400,
                )
                .add_selection(select)
            )

            chart = alt.vconcat(bars, data=common)

            tab1, tab2 = st.tabs(["Streamlit theme (default)", "Altair theme"])

            with container:
                with tab1:
                    st.altair_chart(chart, theme="streamlit", use_container_width=True)
                with tab2:
                    st.altair_chart(chart, theme=None, use_container_width=True)


        st.write("\n")
        emoji_df = helper.emoji_helper(selected_user, df)

        if emoji_df.empty:
            if selected_user == 'Overall':
                st.title(f"{selected_user}, No emoji used")
            else:
                st.title(f"{selected_user} didn't use any emoji")

        else:
            if selected_user == 'Overall':
                st.title(f"{selected_user} Most Used Emojis")
            else:
                st.title(f"{selected_user}'s Most Used Emojis")

            st.write("\n")
            col1, col2 = st.columns(2)

            with col1:
                table = st.dataframe(emoji_df, width=800)
                # Set the CSS style for the table
                table_style = f"height: 500px;overflow: scroll;"
                table_html = f"<style>div.row-widget.stDataFrame {{ {table_style} }}</style>"
                st.markdown(table_html, unsafe_allow_html=True)
                table_style = f"height: 500px; width: 800px;"

            
            with col2:
                # fig, ax = plt.subplots()

                emoji_df['Percentage (in %)'] = ((emoji_df['Frequency']/emoji_df['Frequency'].sum())*100).round(1)

                chart = alt.Chart(emoji_df).mark_arc().encode(
                        theta=alt.Theta(field="Percentage (in %)", type="quantitative", stack=True), 
                        color=alt.Color(field="Emoji", type="nominal"),
                    ).properties(
                            width=500,
                            height=500,
                    )
                
                pie = chart.mark_arc(outerRadius=180)
                text = chart.mark_text(radius=200, size=25).encode(text="Emoji:N")
                
                st.altair_chart(pie+text, use_container_width=True)
        
        st.write("\n")
        if selected_user == 'Overall':
            st.title(f"{selected_user} Daily Timeline")
        else:
            st.title(f"{selected_user}'s Daily Timeline")

        daily = helper.daily_timeline(selected_user, df)
        fig = px.line(daily, x="Dates", y="Number of Messages", markers=True)
        fig.update_traces(hovertemplate='Date: %{x}<br>Number of Messages: %{y}')
        fig.update_layout(hoverlabel=dict(bgcolor='white', font=dict(color='red'),bordercolor='red'))
        fig.update_layout(
            height=500,  # set the height in pixels
            width=1000,  # set the width in pixels
        )
        st.plotly_chart(fig)

        st.write("\n")
        if selected_user == 'Overall':
            st.title(f"{selected_user} Monthly Timeline")
        else:
            st.title(f"{selected_user}'s Monthly Timeline")
        # Line Plot of NUMBER OF MESSAGES
        monthly = helper.monthly_timeline(selected_user, df)
        li = list(monthly['Month'])
        datetimes = [datetime.datetime.strptime(d, '%B %Y') for d in li]

        # Sort the datetime objects
        sorted_datetimes = sorted(datetimes)

        # Convert the sorted datetime objects back to month-year strings
        sorted_data = [d.strftime('%B %Y') for d in sorted_datetimes]

        monthly['Month'] = sorted_data
        fig = px.line(monthly, x="Month", y="Number of Messages", markers=True)
        fig.update_traces(hovertemplate='Time: %{x}<br>Number of Messages: %{y}')
        fig.update_layout(hoverlabel=dict(bgcolor='white', font=dict(color='red'), bordercolor='red'))
        fig.update_layout(
            height=500,  # set the height in pixels
            width=1000   # set the width in pixels
        )
        fig.update_traces(line=dict(color='green'))
        st.plotly_chart(fig)

        st.write("\n")
        if selected_user == 'Overall':
            st.title(f"{selected_user} Activity Map")
        else:
            st.title(f"{selected_user}'s Activity Map")

        
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            st.write("\n")
#             r = helper.week_Activity_map(selected_user, df)

#             sorter = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
#             sorterIndex = dict(zip(sorter,range(len(sorter))))
#             r['Day_id'] = r['Day']
#             r['Day_id'] = r['Day_id'].map(sorterIndex)
#             r.sort_values('Day_id', inplace=True)

#             chart = alt.Chart(r).mark_bar().encode(
#                                 x=alt.X('Day:N', sort=None),
#                                 y='Number of Messages',
#                                 color=alt.Color('Day', scale=alt.Scale(scheme='inferno'), sort=None),
#                         ).properties(
#                                 height = 500,
#                                 width = 500
#             )

#             chart = chart.configure_axis(
#                                 labelFontSize=0,
#                                 domain=False,  # hide axis line
#                                 labelAngle=0,  # set label angle to 0 degrees
#                         )

#             chart = chart.configure_axisY(
#                                 labelFontSize=12  # set label font size for y-axis
#                         )

#             st.altair_chart(chart)
            
        with col2:
            st.header("Most Busy Month")
            st.write("\n")
            dk = helper.month_Activity_map(selected_user, df)
            st.write(dk)
            dk = dk.rename(columns={'count': 'Number of Messages', 'Number of Messages' : 'Month'})
            st.write(dk)
            dk['Month'] = pd.DatetimeIndex(pd.to_datetime(dk['Month'], format='%B')).month
            dk = dk.set_index('Month').sort_index().reset_index()

            dk['Month'] = dk['Month'].apply(lambda x: calendar.month_abbr[x])

            chart = alt.Chart(dk).mark_bar().encode(
                                x=alt.X('Month:N', sort=None),
                                y='Number of Messages:Q',
                                color=alt.Color('Month', scale=alt.Scale(scheme='sinebow'), sort=None),
                        ).properties(
                                height = 500,
                                width = 500
            )

            chart = chart.configure_axis(
                                labelFontSize=0,
                                domain=False,  # hide axis line
                                labelAngle=0,  # set label angle to 0 degrees
                        )

            chart = chart.configure_axisY(
                                labelFontSize=12  # set label font size for y-axis
                        )

            st.altair_chart(chart)



        # WORD CLOUD CODE HERE
        # st.write("\n")
        # if selected_user == 'Overall':
        #     st.title(f"{selected_user} WordCloud")
        # else:
        #     st.title(f"{selected_user}'s WordCloud")
        
        # st.write("\n")
        # df_wc = helper.create_Word_Cloud(selected_user, df)
        # fig, ax = plt.subplots()
        # ax.imshow(df_wc, interpolation="bilinear")
        # st.pyplot(fig)

        st.write('\n')
        st.write('\n')
        st.markdown("""
        <style>
        .big-font {
            font-size:18px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.header('Spam Analyzer')
        st.markdown('<p class="big-font">Wanna know SMS or Email you received is Spam or not? Check out my <a href="https://farneet24-sms-spam-app-j9qp5s.streamlit.app/">SMS Spam Analyzer</a></p>', unsafe_allow_html=True)
        # st.markdown('''Wanna know SMS or Email you received is Spam or not? Check out my <a href="https://sms-spam-6zao.onrender.com/">SMS Spam Analyzer</a>''', unsafe_allow_html=True)

        st.write('\n')
        st.write('\n')
        st.header('📝 Have questions?')
        st.markdown("""Tell us what you want to know!! <a href="https://farneet24-contact-contact-y0vege.streamlit.app/">Contact Us</a>""", unsafe_allow_html=True)

if para:
    with st.expander("How to upload the chat?"):
            # st.write("This is the content of the card")
                html = """
                <h2><u>Export chat history</u></h2>
                    <p>You can use the export chat feature to export a copy of the chat history from an individual or group chat.</p>
                    <ol>
                        <li>Open the individual or group chat.</li>
                        <li>Tap More options <img src="https://scontent.whatsapp.net/v/t39.8562-34/109105444_276026637003261_6902470040701723547_n.png?ccb=1-7&_nc_sid=2fbf2a&_nc_ohc=AmefhqxK-gUAX_AdSAu&_nc_ht=scontent.whatsapp.net&oh=01_AdR2xzISoH9PxZCgLPqGuCBSJz7_I5d7D8YBkDWNA4bFWw&oe=642F2462" alt=":", height = "20px"> > More > Export chat.</li>
                        <li> Choose to export without media.</li>
                    </ol> 
                    <p></p>
                """

                html2 = '''
                    <ul style="list-style-type:square;">
                    <li>Upload the .txt file and Click on 'Show Analysis'</li>
                    </ul>
                    <p></p>'''

                st.markdown(html, unsafe_allow_html=True)
                st.warning("⚠️ Remember: Do not export 'with media'")        
                st.markdown(html2, unsafe_allow_html=True)

