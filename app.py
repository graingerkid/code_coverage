import streamlit as st
import json
import io

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

            # Save critical code to BytesIO
            critical_file = io.BytesIO()
            critical_file.write(critical_code.encode('utf-8'))
            critical_file.seek(0)  # Move pointer to the start of file
            critical_files.append((critical_file, file_name, url))

            # Save non-critical code to BytesIO
            non_critical_file = io.BytesIO()
            non_critical_file.write(non_critical_code.encode('utf-8'))
            non_critical_file.seek(0)  # Move pointer to the start of file
            non_critical_files.append((non_critical_file, file_name, url))

    return critical_files, non_critical_files

# Streamlit app
st.title("Code Coverage Processor")

# Upload file
uploaded_file = st.file_uploader("Upload JSON File", type="json")

# Process file and display processed files
if uploaded_file is not None:
    st.write(uploaded_file.name)
    try:
        critical_files, non_critical_files = process_code_coverage(uploaded_file)
        st.success("Code coverage processed successfully.")

        # Display critical files with download buttons
        st.subheader("Critical Files")
        for file, file_name, url in critical_files:
            st.write(file_name)
            st.write(f"({url})")
            st.download_button(
                label="Download",
                data=file.getvalue(),
                file_name=file_name
            )

        # Display non-critical files with download buttons
        st.subheader("Non-Critical Files")
        for file, file_name, url in non_critical_files:
            st.write(file_name)
            st.write(f"({url})")
            st.download_button(
                label="Download",
                data=file.getvalue(),
                file_name=file_name
            )

    except ValueError as e:
        st.error(f"Error processing code coverage: {str(e)}")
