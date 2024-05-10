import streamlit as st
import boto3
from io import StringIO

# Function to list existing .csv files in the S3 bucket
def list_csv_files(bucket_name):
    s3_client = boto3.client('s3', aws_access_key_id=st.secrets["aws"]["access_key_id"],
                             aws_secret_access_key=st.secrets["aws"]["secret_access_key"],
                             region_name=st.secrets["aws"]["region"])
    csv_files = []
    try:
        contents = s3_client.list_objects_v2(Bucket=bucket_name)['Contents']
        for obj in contents:
            if obj['Key'].endswith('.csv'):
                csv_files.append(obj['Key'])
    except KeyError:
        st.error('No files found in the bucket.')
    except Exception as e:
        st.error(f"Error accessing bucket: {e}")
    return csv_files

# Function to add a new .csv file to the S3 bucket
def add_csv_to_s3(bucket_name, file_path, csv_content=""):
    s3_client = boto3.client('s3', aws_access_key_id=st.secrets["aws"]["access_key_id"],
                             aws_secret_access_key=st.secrets["aws"]["secret_access_key"],
                             region_name=st.secrets["aws"]["region"])
    # Create a CSV file in S3
    s3_client.put_object(Body=csv_content, Bucket=bucket_name, Key=file_path)
    st.success(f"File {file_path} created in bucket {bucket_name}.")

# Display title
st.title('Existing in and adding to S3 bucket')

# S3 bucket name
bucket_name = 'streamlitbucketkamra34'

# Display existing .csv files
st.subheader('Existing files in the bucket:')
csv_files = list_csv_files(bucket_name)
if csv_files:
    for file in csv_files:
        st.write(file)
else:
    st.write("No .csv files found.")

st.subheader('Add new to the bucket:')
# Input for new file name
file_name = st.text_input("Name of new file (must end with .csv)", key="new_file")

# Input for CSV content
csv_content = st.text_area("Enter CSV content", key="csv_cont", help="Format: '<col1>,<col2>,<col3>\nvalue1,value2,value3'")

# Button to add new .csv file
if st.button("Add CSV File"):
    if file_name.strip().endswith('.csv'):
        add_csv_to_s3(bucket_name, file_name, csv_content)
    else:
        st.error("File name must end with .csv")
