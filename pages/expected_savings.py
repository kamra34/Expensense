import streamlit as st
import pandas as pd
import boto3
from io import StringIO

def save_df_to_s3(df, bucket_name, file_path):
    """Convert DataFrame to CSV and upload to S3."""
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket_name, file_path).put(Body=csv_buffer.getvalue())
    st.success(f'DataFrame saved to S3 successfully: {file_path}')

def load_df_from_s3(bucket_name, file_path):
    """Load a DataFrame from a CSV file on S3."""
    s3_client = boto3.client('s3', aws_access_key_id=st.secrets["aws"]["access_key_id"],
                             aws_secret_access_key=st.secrets["aws"]["secret_access_key"],
                             region_name=st.secrets["aws"]["region"])
    try:
        csv_obj = s3_client.get_object(Bucket=bucket_name, Key=file_path)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        if csv_string.strip() == "":
            return pd.DataFrame()  # Return an empty DataFrame if the file is empty
        else:
            df = pd.read_csv(StringIO(csv_string))
            return df
    except s3_client.exceptions.NoSuchKey:
        return pd.DataFrame()  # Return an empty DataFrame if the file does not exist
    except Exception as e:
        st.error(f"Error loading data from S3: {e}")
        return pd.DataFrame()

st.title('Expected Monthly Savings')


df_income = load_df_from_s3('streamlitbucketkamra34', 'expected_income.csv')
df_expenses = load_df_from_s3('streamlitbucketkamra34', 'expected_expenses.csv')
print(df_income)
print(df_expenses)

st.subheader(":orange[Current income]")
st.dataframe(df_income)
st.subheader(":orange[Predicted Expenses]")
st.dataframe(df_expenses)

# Expander for editing the selected DataFrame
with st.container(border=True):
    with st.expander("Edit Columns"):
        # User selects which data to edit
        data_choice = st.radio("Select data to edit:", ("Income", "Expenses"))

        # Load the corresponding DataFrame
        if data_choice == "Income":
            file_path = 'expected_income.csv'
        else:
            file_path = 'expected_expenses.csv'

        df = load_df_from_s3('streamlitbucketkamra34', file_path)
        col1, col2, col3 = st.columns(3, gap='large')
        with col1:
            # Display the selected DataFrame or indicate it's empty
            if df.empty:
                st.write("The DataFrame is currently empty. Please add columns and data.")

            #st.subheader(f"Editing: {data_choice}")

            # Manage columns in an empty DataFrame
            if df.empty:
                new_cols = st.text_input("Enter column names, separated by commas", key="new_cols")
                if st.button("Create Columns"):
                    col_names = [x.strip() for x in new_cols.split(',')]
                    df = pd.DataFrame(columns=col_names)
                    save_df_to_s3(df, 'streamlitbucketkamra34', file_path)
                    st.rerun()  # Rerun the app to refresh the state with the new DataFrame
            else:
                # For non-empty DataFrame, provide editing options
                #st.write("Rename, add, or delete columns as needed.")

            # Display current columns with an option to rename
                new_columns = []
                for i, col in enumerate(df.columns):
                    new_col = st.text_input(f"Rename column '{col}'", value=col, key=f"new_name_{i}")
                    new_columns.append(new_col)
            # Save button to apply changes
            if st.button("Rename Columns"):
                # Apply any column renamings
                df.columns = new_columns            
                # Save the updated DataFrame back to S3
                save_df_to_s3(df, 'streamlitbucketkamra34', file_path)
                st.rerun()
        with col2:
            # Option to add a new column
            new_col_name = st.text_input("Add (leave blank if not):", key="add_new_col") 
            # Save button to apply changes
            if st.button("Add column"):
                # Apply any column renamings
                df.columns = new_columns
            
                # Add new column if specified
                if new_col_name:
                    df[new_col_name] = pd.NA  # or appropriate default value
            
                # Save the updated DataFrame back to S3
                save_df_to_s3(df, 'streamlitbucketkamra34', file_path)
                st.rerun()
        with col3:
            # Option to delete a column
            col_to_delete = st.selectbox("Delete a column (optional):", [''] + list(df.columns), key="delete_col")

            # Save button to apply changes
            if st.button("Delete Columns"):            
                # Delete selected column if specified
                if col_to_delete:
                    df = df.drop(columns=[col_to_delete])
            
                # Save the updated DataFrame back to S3
                save_df_to_s3(df, 'streamlitbucketkamra34', file_path)
                st.rerun()

# Initialize session state for new row data if it doesn't already exist
if 'new_row_data' not in st.session_state:
    st.session_state['new_row_data'] = {}

# Additional functionality for row editing
with st.container(border=True):
    with st.expander("Edit Rows"):
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.subheader("Edit Existing Row")
            # User selects which data to edit
            row_data_choice = st.radio("Select data to edit rows in:", ("Income", "Expenses"), key="row_data_choice")

            if row_data_choice == "Income":
                file_path = 'expected_income.csv'
            else:
                file_path = 'expected_expenses.csv'

            df_to_edit = load_df_from_s3('streamlitbucketkamra34', file_path)

            # Select a row to edit
            row_to_edit = st.selectbox("Select a row to edit (by index):", options=range(len(df_to_edit)), key="row_to_edit_index")

            # Initialize or update session state for row editing
            if 'edit_row_data' not in st.session_state or st.session_state['edit_row_index'] != row_to_edit:
                st.session_state['edit_row_data'] = df_to_edit.iloc[row_to_edit].to_dict()
                st.session_state['edit_row_index'] = row_to_edit

            # Generate inputs for each column in the row
            for col in df_to_edit.columns:
                st.session_state['edit_row_data'][col] = st.text_input(f"New value for {col}", value=str(st.session_state['edit_row_data'][col]), key=f"edit_{col}")

            if st.button("Save Edited Row"):
                # Update the DataFrame with edited values
                for col, value in st.session_state['edit_row_data'].items():
                    df_to_edit.at[row_to_edit, col] = value

                # Save changes and reset session state for the next edit
                save_df_to_s3(df_to_edit, 'streamlitbucketkamra34', file_path)
                del st.session_state['edit_row_data']
                st.rerun()
        with col2:
            st.subheader("Add new Row")
            # Form for adding a new row
            with st.form(key='add_row_form'):
                new_row_data = {col: st.text_input(f"Value for {col}", key=f"new_row_{col}") for col in df_to_edit.columns}
                submit_button = st.form_submit_button(label='Save New Row')

            if submit_button:
                new_row_series = pd.Series(new_row_data)
                df_to_edit = pd.concat([df_to_edit, pd.DataFrame([new_row_series])], ignore_index=True)
                save_df_to_s3(df_to_edit, 'streamlitbucketkamra34', file_path)
                st.rerun()

    
# Sum up total income and expenses
total_income = int(df_income.sum().sum())  # Summing twice to get the total of all values
total_expenses = int(df_expenses.sum().sum())

# Calculate the difference
difference = total_income - total_expenses

# Create a summary DataFrame
df_summary = pd.DataFrame({
    'Total Income': [total_income],
    'Total Expenses': [total_expenses],
    'Difference': [difference]
})

# Display the summary DataFrame
st.title("Summary")
st.table(df_summary)
