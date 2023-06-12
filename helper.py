from urlextract import URLExtract
import streamlit as st
import pandas as pd
import smtplib
import emoji
from collections import Counter
from wordcloud import WordCloud

extract = URLExtract()

def fetch_stats(selected_user, df):

    # This is whole concept of the function !!!!!!!!!!!!
    # if selected_user == 'Overall':
    #     num_messages = df.shape[0] # 1. finds number of messages
    #     words = [] # 2. finds number of words
    #     for i in df['message']:
    #         words.extend(i.split())
        
    #     num_words = len(words);
    #     return num_messages, num_words
    # else: # return the number of messages sent by the specific user
    #     words = []
    #     num_messages = df[df['user'] == selected_user].shape[0]
    #     for i in df[df['user'] == selected_user]['message']:
    #         words.extend(i.split());
    #     num_words = len(words);
    #     return num_messages, num_words


    # Lets minimize the code

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    
    # 1. return the number of messages sent by the specific user
    num_messages = df.shape[0]

    # 2. finds number of words
    words = []
    for i in df['message']:
        words.extend(i.split())
        num_words = len(words);
    

    # 3. Finding total number of media
    num_media = df[df['message'] == '<Media omitted>\n'].shape[0]

    # 4. Finding total number of links
    links = []
    for i in df['message']:
        links.extend(extract.find_urls(i));
    num_links = len(links)
    
    return num_messages, num_words, num_media, num_links


def most_busy_users(df):
    x = df['user'].value_counts().reset_index().rename(columns= {'index' : 'Number of messages', 'user':'User'}).head() # Top 5 users
    percent = ((df['user'].value_counts()/df.shape[0])*100).round(1).reset_index().rename(columns= {'index' : '% of messages', 'user':'User'})
    return x, percent;


def create_Word_Cloud(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'Group_Notification'] # Gave all data that are not Group_Notification
    temp = temp[temp['message'] != '<Media omitted>\n']

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    def remove_stop_words(message):
        words = []

        for i in temp['message']:
            for word in i.lower().split():
                if word not in stop_words:
                    words.append(word)
        return " ".join(words)

    # We will remove stop words and other stuff from word cloud


    wc = WordCloud(height = 500, width = 1100, min_font_size=5, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc  = wc.generate(temp['message'].str.cat(sep = " "))
    return df_wc

def most_commom_words(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    temp = df[df['user'] != 'Group_Notification'] # Gave all data that are not Group_Notification
    temp = temp[temp['message'] != '<Media omitted>\n']

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    words = []

    for i in temp['message']:
        for word in i.lower().split():
            if word not in stop_words:
                words.append(word)

    empty_df = pd.DataFrame()

    if len(words)==0:
        return empty_df;
    else:
        x = pd.DataFrame(Counter(words).most_common(20)).rename(columns={0:'Common Words', 1:'Frequency'}).head() # Gives us most common words with frequency
        return x;



def emoji_helper(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    empty_df = pd.DataFrame()
    emojis = []

    for i in df['message']:
        emojis.extend([c for c in i if c in emoji.EMOJI_DATA])
    
    if len(emojis)==0:
        return empty_df;
    else:
        emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis)))).rename(columns={0:'Emoji', 1:'Frequency'}).head(10)
        return emoji_df



def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    
    timeline = df.groupby(['year', 'month'])['message'].count().reset_index()

    time = []
    index = []
    for i in range(timeline.shape[0]):
        index.append(i)
        time.append(timeline['month'][i] + " " + str(timeline['year'][i]))

    
    timeline['order'] = index
    timeline['Month'] = time
    timeline = timeline.rename(columns={'message':"Number of Messages"})
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df['Dates'] = df['date'].dt.date
    daily_timeline = df.groupby('Dates').count()['message'].reset_index().rename(columns={'message':'Number of Messages'})

    return daily_timeline


def week_Activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    r = df['day_name'].value_counts().reset_index().rename(columns = {'index':"Day", 'day_name':"Number of Messages"})
    return r


def month_Activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    t = df['month'].value_counts().reset_index().rename(columns = {'index':"Month", 'month':"Number of Messages"})

    return t


# def activity_heatmap(selected_user,df):
    
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]

#     s = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

#     return s




