import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Function to load and clean the data


def load_and_clean_data(file_path):
    email_data = pd.read_csv(file_path)

    # Remove unnecessary columns
    if 'Unnamed: 2' in email_data.columns:
        email_data = email_data.drop(columns=['Unnamed: 2'])

    # Convert the Timestamp column to datetime format
    email_data['Timestamp'] = pd.to_datetime(
        email_data['Timestamp'], errors='coerce')

    # Drop rows with invalid timestamps
    email_data = email_data.dropna(subset=['Timestamp'])

    # Extract hour, day of the week, and month from the Timestamp
    email_data['Hour'] = (email_data['Timestamp'].dt.hour + 1) % 24
    email_data['DayOfWeek'] = email_data['Timestamp'].dt.dayofweek
    email_data['Month'] = email_data['Timestamp'].dt.month

    return email_data

# Function to plot the daily email activity for a specific user with times


def plot_user_daily_activity(data, user_id):
    user_data = data[data['Unique ID'] == user_id]

    # Extract day of the week and time from the Timestamp
    user_data['DayOfWeek'] = user_data['Timestamp'].dt.dayofweek
    user_data['Time'] = user_data['Timestamp'].dt.time

    plt.figure(figsize=(14, 7))

    # Scatter plot of email timestamps
    plt.scatter(user_data['DayOfWeek'], user_data['Timestamp'].dt.hour +
                user_data['Timestamp'].dt.minute/60, alpha=0.7, marker='x')

    plt.title(f'Monthly Email Activity for User {user_id}')
    plt.xlabel('Day of the Week')
    plt.ylabel('Time of Day')
    plt.grid(True)

    # Set x-axis labels
    plt.xticks(ticks=range(7), labels=[
               'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    # Set y-axis to show hours
    plt.yticks(range(0, 24), [f'{hour}:00' for hour in range(24)])

    st.pyplot(plt)

# Streamlit interface


def main():
    st.title("Email Activity Analysis")

    # File uploader
    file_path = st.file_uploader("Upload CSV file", type=["csv"])

    if file_path is not None:
        # Load data
        email_data = load_and_clean_data(file_path)

        # Determine the timeframe present in the CSV
        start_date = email_data['Timestamp'].min()
        end_date = email_data['Timestamp'].max()

        st.write(
            f"Data Timeframe: {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}")

        # Get unique user IDs
        unique_ids = len(email_data['Unique ID'].unique())

        # User ID selection
        user_id = st.number_input(
            "Select User ID", min_value=1, max_value=unique_ids)

        user_id_formatted = f"UID{user_id:03}"

        # Plot user activity
        if user_id_formatted:
            user_data = email_data[email_data['Unique ID']
                                   == user_id_formatted]
            user_department = user_data['Department'].iloc[0]
            total_emails = user_data.shape[0]
            col1, col2 = st.columns(2)
            col1.metric("Department", user_department)
            col2.metric("Total Emails Sent (1 month)", total_emails)

            # st.write(f"Department: {user_department}")
            # st.write(f"Total Emails Sent (1 month): {total_emails}")

            plot_user_daily_activity(email_data, user_id_formatted)


if __name__ == "__main__":
    main()
