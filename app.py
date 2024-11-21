import streamlit as st
import pandas as pd
import numpy as np

# Function to load the uploaded Excel file and return a DataFrame
def load_excel(file):
    try:
        # Read the Excel file using pandas
        df = pd.read_excel(file)

        # Normalize column names: strip spaces, lowercase, and remove special characters
        df.columns = df.columns.str.strip().str.lower().str.replace(r'[^a-z0-9\s]', '', regex=True).str.replace(' ', '_')

        # Display the column names for debugging purposes
        st.write("Column names in the uploaded file:", df.columns.tolist())

        # Display the first few rows to inspect the data
        st.write("First few rows of the data:")
        st.dataframe(df.head())

        return df
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
        return None

# Function to calculate the torque using linear interpolation for any "torque" column
def find_torque(df, time):
    # Find all columns with the word "torque" in their name (case-insensitive)
    torque_columns = [col for col in df.columns if 'torque' in col]
    
    if len(torque_columns) == 0:
        st.error("No columns with 'torque' in their name found in the uploaded file.")
        return None
    
    # Ensure that the data is sorted by time_s
    df = df.sort_values(by='time_s')

    # Check if the time is exactly in the dataset
    if time in df['time_s'].values:
        # If exact match found, return the torque values for each "torque" column
        results = {}
        for torque_column in torque_columns:
            torque = df.loc[df['time_s'] == time, torque_column].values[0]
            results[torque_column] = torque
        return results
    
    # Check if the entered time is within the available range
    min_time = df['time_s'].min()
    max_time = df['time_s'].max()

    if time < min_time or time > max_time:
        st.warning(f"Entered time {time} is outside the valid range ({min_time} to {max_time}). Interpolation may not be accurate.")
        return None

    # If the exact time is not found, interpolate for each "torque" column
    try:
        results = {}
        for torque_column in torque_columns:
            # Get the indices of the lower and upper time values for this column
            lower_time_idx = df[df['time_s'] <= time].index.max()
            upper_time_idx = df[df['time_s'] > time].index.min()

            # Get the corresponding lower and upper times and torques
            lower_time = df.loc[lower_time_idx, 'time_s']
            upper_time = df.loc[upper_time_idx, 'time_s']
            
            lower_torque = df.loc[lower_time_idx, torque_column]
            upper_torque = df.loc[upper_time_idx, torque_column]

            # Interpolate using the formula for linear interpolation
            torque = lower_torque + (time - lower_time) * (upper_torque - lower_torque) / (upper_time - lower_time)
            
            results[torque_column] = torque
        
        return results
    except Exception as e:
        st.error(f"Error during interpolation: {e}")
        return None

# Streamlit app
def app():
    # Set page title
    st.title("Torque Calculation from Time Input")

    # File upload widget
    uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        # Load the uploaded file
        df = load_excel(uploaded_file)

        if df is not None:
            # Ensure the required columns exist
            if 'time_s' not in df.columns:
                st.error("Excel file must contain 'time_s' column.")
                return

            # Take user input for time (text input)
            user_time_text = st.text_input("Enter time in seconds (e.g., 5.812):", value="0")
            
            try:
                # Convert the input to a float
                user_time = float(user_time_text)
            except ValueError:
                st.error("Please enter a valid numerical value for time.")
                return

            # Button to trigger calculation
            if st.button("Calculate Torque"):
                # Find the torque corresponding to the entered time
                results = find_torque(df, user_time)

                if results is not None:
                    # Display the results for each "torque" column
                    for torque_column, torque in results.items():
                        st.success(f"Calculated {torque_column} at {user_time} seconds is {torque:.2f} Nm")
                else:
                    st.warning("Could not calculate the torque. Please check your input and data.")

if __name__ == "__main__":
    app()
