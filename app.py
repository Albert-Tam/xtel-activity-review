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
    email_data['Date'] = email_data['Timestamp'].dt.date
    email_data['Hour'] = (email_data['Timestamp'].dt.hour + 1) % 24
    email_data['Minute'] = email_data['Timestamp'].dt.minute
    time_in_hours = email_data['Hour'] + email_data['Minute']/60
    adjusted_for_cet = (time_in_hours + 1) % 24
    email_data['TimeInHours'] = adjusted_for_cet
    email_data['DayOfWeek'] = email_data['Timestamp'].dt.dayofweek
    email_data['Month'] = email_data['Timestamp'].dt.month
    email_data['Week'] = email_data['Timestamp'].dt.isocalendar().week

    return email_data

# Function to plot the daily email activity for a specific user with times


def plot_user_daily_activity(data, user_id):
    user_data = data[data['Unique ID'] == user_id]
    # Extract day of the week and time from the Timestamp
    # user_data['DayOfWeek'] = user_data['Timestamp'].dt.dayofweek
    # user_data['Time'] = user_data['Timestamp'].dt.time

    plt.figure(figsize=(14, 7))

    # Scatter plot of email timestamps
    plt.scatter(user_data['DayOfWeek'],
                user_data["TimeInHours"], alpha=0.7, marker='x')

    plt.title(f'Email Activity for User {user_id}')
    plt.xlabel('Day of the Week')
    plt.ylabel('Time of Day')
    plt.grid(True)

    # Set x-axis labels
    plt.xticks(ticks=range(7), labels=[
               'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    # Set y-axis to show hours
    plt.yticks(range(0, 24), [f'{hour}:00' for hour in range(24)])

    st.pyplot(plt)


def median_daily_working_hours(email_data, user_id):
    # Filter data for the specific user
    user_data = email_data[email_data['Unique ID'] == user_id]

    # Exclude weekends
    user_data = user_data[user_data['DayOfWeek'] < 5]

    # Calculate the first and last email times per day for the specific user
    grouped = user_data.groupby(['Unique ID', 'Date'])[
        'Timestamp'].agg(['min', 'max']).reset_index()

    # Extract only the time part from 'min' and 'max'
    grouped['min_time'] = grouped['min'].dt.time
    grouped['max_time'] = grouped['max'].dt.time

    grouped['total_time'] = (
        grouped['max'] - grouped['min']).dt.total_seconds().round().astype(int)

    # Calculate the median of these times in seconds
    median_working_hour = grouped['total_time'].median() / 3600

    return median_working_hour

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

        st.write("Timezone: CET (Central European Time)")

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
            median_working_hours = median_daily_working_hours(
                email_data, user_id_formatted)

            hours = int(median_working_hours)
            minutes = int((median_working_hours - hours) * 60)
            median_working_hours_minutes = f"{hours:02}:{minutes:02}"

            col1, col2, col3 = st.columns(3)
            col1.metric("Department", user_department)
            col2.metric("Total Emails Sent (1 month)", total_emails)
            col3.metric("Median Working Hours", median_working_hours_minutes,
                        help="Calculated by taking the median of the time between the first and last email sent each day (excluding weekends). A value of 0 indicates only one email was sent each day.")
            # st.write(f"Department: {user_department}")
            # st.write(f"Total Emails Sent (1 month): {total_emails}")

            st.subheader(f"Aggregated Activity for User {user_id_formatted}")
            plot_user_daily_activity(email_data, user_id_formatted)
            st.divider()

            # Get unique weeks
            unique_weeks = sorted(user_data['Week'].unique())

            # Plot user daily activity for each unique week
            for week in unique_weeks:
                st.subheader(f"Week {week}")
                week_data = email_data[email_data['Week'] == week]
                plot_user_daily_activity(week_data, user_id_formatted)


if __name__ == "__main__":
    main()
