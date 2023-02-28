# The following function will get the data as the string and will return the DataFrame
import re
import pandas as pd

def preprocess(data):
    pattern =  '\d{1,2}\/\d{2,4}\/\d{2,4},\s\d{1,2}:\d{1,2}\s\w{1,2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message' : messages, 'message_date' : dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %I:%M %p - ') #its in 24hr format
    df.rename(columns={'message_date' : 'date'}, inplace=True)

    users = []
    message = []

    for i in df['user_message']:
        entry = re.split('([\w\W]+?):\s', i)
    #     print(entry)
        if entry[1:]:
            users.append(entry[1]);
            message.append(entry[2])
        else:
            users.append('Group_Notification')
            message.append(entry[0])


    df['user'] = users
    df['message'] = message
    df.drop(columns=["user_message"], inplace=True)
    df['Dates'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour # In 24hr format
    df['minute'] = df['date'].dt.minute

    return df