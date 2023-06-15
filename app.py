import streamlit as st
import json
import io
import tempfile

def process_code_coverage(json_data):
    try:
        raw_code_coverage_list = json.loads(json_data)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON format") from e

    critical_files = []
    non_critical_files = []

    for raw_code_coverage in raw_code_coverage_list:
        if '.css' in raw_code_coverage['url']:
            url = raw_code_coverage['url']
            file_name = url[url.rfind('/') + 1:]
            ranges_list = raw_code_coverage['ranges']
            code = raw_code_coverage['text']

            critical_code = ''
            non_critical_code = ''

            # Add code within and outside the ranges
            if ranges_list:
                # Code before the first range
                if ranges_list[0]['start'] > 0:
                    non_critical_code += code[:ranges_list[0]['start']]

                # Code between ranges
                for i in range(len(ranges_list) - 1):
                    critical_code += code[ranges_list[i]['start']:ranges_list[i]['end']]
                    non_critical_code += code[ranges_list[i]['end']:ranges_list[i + 1]['start']]

                # Code after the last range
                critical_code += code[ranges_list[-1]['start']:ranges_list[-1]['end']]
                non_critical_code += code[ranges_list[-1]['end']:]

            else:
                non_critical_code = code

            # Save critical code to a temporary file
            critical_file = tempfile.NamedTemporaryFile(mode='wb', delete=False)
            critical_file.write(critical_code.encode('utf-8'))
            critical_file.close()
            critical_files.append((critical_file.name, file_name, url))

            # Save non-critical code to a temporary file
            non_critical_file = tempfile.NamedTemporaryFile(mode='wb', delete=False)
            non_critical_file.write(non_critical_code.encode('utf-8'))
            non_critical_file.close()
            non_critical_files.append((non_critical_file.name, file_name, url))

    return critical_files, non_critical_files

# Streamlit app
st.title("Code Coverage Processor")

# File upload
uploaded_file = st.file_uploader("Upload JSON File", type="json")

# Process file and display processed files
if uploaded_file is not None:
    st.write(uploaded_file.name)
    try:
        uploaded_json_data = uploaded_file.read().decode('utf-8')
        critical_files, non_critical_files = process_code_coverage(uploaded_json_data)
        st.success("Code coverage processed successfully.")

        # Display critical files with download buttons
        st.subheader("Critical Files")
        for file_path, file_name, url in critical_files:
            st.write(file_name)
            st.write(f"({url})")
            try:
                with open(file_path, 'rb') as file:
                    file_contents = file.read()
                st.download_button(
                    label="Download",
                    data=file_contents,
                    file_name=file_name
                )
            except Exception as e:
                st.error(f"Error downloading critical file: {str(e)}")

        # Display non-critical files with download buttons
        st.subheader("Non-Critical Files")
        for file_path, file_name, url in non_critical_files:
            st.write(file_name)
            st.write(f"({url})")
            try:
                with open(file_path, 'rb') as file:
                    file_contents = file.read()
                st.download_button(
                    label="Download",
                    data=file_contents,
                    file_name=file_name
                )
            except Exception as e:
                st.error(f"Error downloading non-critical file: {str(e)}")

    except ValueError as e:
        st.error(f"Error processing code coverage: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
