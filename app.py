import streamlit as st
import json
import os

def process_code_coverage(json_file):
    try:
        with open(json_file, encoding='utf-8') as json_data:
            raw_code_coverage_list = json.load(json_data)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON format") from e
    except FileNotFoundError as e:
        raise ValueError("File not found") from e
    except Exception as e:
        raise ValueError("Error loading JSON file") from e

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

            # Save critical code to file
            critical_file_path = f"critical_{file_name.replace('?', '_')}"
            try:
                with open(critical_file_path, "w", encoding='utf-8') as f:
                    f.write(critical_code)
            except Exception as e:
                raise ValueError(f"Error saving critical file: {str(e)}") from e
            critical_files.append((critical_file_path, url))

            # Save non-critical code to file
            non_critical_file_path = f"non_critical_{file_name.replace('?', '_')}"
            try:
                with open(non_critical_file_path, "w", encoding='utf-8') as f:
                    f.write(non_critical_code)
            except Exception as e:
                raise ValueError(f"Error saving non-critical file: {str(e)}") from e
            non_critical_files.append((non_critical_file_path, url))

    return critical_files, non_critical_files

# Streamlit app
st.title("Code Coverage Processor")

# File upload
uploaded_file = st.file_uploader("Upload JSON File", type="json")

# Process file and display processed files
if uploaded_file is not None:
    try:
        critical_files, non_critical_files = process_code_coverage(uploaded_file.name)
        st.success("Code coverage processed successfully.")

        # Display critical files with download buttons
        st.subheader("Critical Files")
        for file_path, url in critical_files:
            file_name = os.path.basename(file_path)
            st.write(file_name)
            st.write(f"({url})")
            try:
                st.download_button(
                    label="Download",
                    data=open(file_path, 'rb').read(),
                    file_name=file_name
                )
            except Exception as e:
                st.error(f"Error downloading critical file: {str(e)}")

        # Display non-critical files with download buttons
        st.subheader("Non-Critical Files")
        for file_path, url in non_critical_files:
            file_name = os.path.basename(file_path)
            st.write(file_name)
            st.write(f"({url})")
            try:
                st.download_button(
                    label="Download",
                    data=open(file_path, 'rb').read(),
                    file_name=file_name
                )
            except Exception as e:
                st.error(f"Error downloading non-critical file: {str(e)}")

    except ValueError as e:
        st.error(f"Error processing code coverage: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
