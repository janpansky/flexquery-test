import streamlit as st
import time
import pandas as pd
from api_requests import reload_cache, execute_api_call, get_results
from utils import load_json_body

# Load credentials from Streamlit's secrets management
hostname = st.secrets["api"]["hostname"]
token = st.secrets["api"]["token"]
workspace_id = "gdc_demo_a3da0f24-9c32-4f19-9848-43dfe4096416"
data_source_id = "gdc_demo_20557729-8b95-4121-b942-6abb88b735ad"

# Initialize or load execution times from the session state
if 'execution_times' not in st.session_state:
    st.session_state.execution_times = pd.DataFrame(columns=["POST Execution Time (ms)", "GET Execution Time (ms)"])

# Streamlit app title
st.title("GoodData FlexQuery Performance and Cache Management Demo")

# Display informative text
st.markdown("""**This demo showcases the performance of querying data through GoodData's FlexQuery system, currently 
using Snowflake as the underlying database. Both systems are hosted in the US data center.**
""")

# Layout for Reload Cache button and text
col1, col2 = st.columns([2, 3])

with col1:
    if st.button("Reload Cache"):
        response = reload_cache(hostname, token, data_source_id)
        if response.status_code < 205:
            st.success("Cache reloaded successfully!")
        else:
            st.error(f"Cache reload failed with status code: {response.status_code}")
            st.write(response.text)

with col2:
    st.write("The 'Reload Cache' button clears the cache, ensuring the next API execution queries the underlying "
             "database instead of GoodData's FlexCache. Use it with caution, as it can be costly as it run against "
             "Snowflake.")

# Layout for Execute API button and text
col1, col2 = st.columns([2, 3])

with col1:
    if st.button("Execute API"):
        # Start timing the POST request execution
        post_start_time = time.time()

        # Load the JSON body from a file
        data = load_json_body("request_body.json")

        response = execute_api_call(hostname, token, workspace_id, data)
        post_end_time = time.time()
        post_execution_time = post_end_time - post_start_time

        if response.status_code == 200:
            st.success("API call (POST) was successful!")
            result = response.json()

            # Extract the result ID from the POST response
            execution_result_id = result["executionResponse"]["links"]["executionResult"]

            # Start timing the GET request execution
            get_start_time = time.time()
            get_response = get_results(hostname, token, workspace_id, execution_result_id)
            get_end_time = time.time()
            get_execution_time = get_end_time - get_start_time

            if get_response.status_code == 200:
                st.success("Data retrieval (GET) was successful!")
                # Do not display the JSON result in the app
            else:
                st.error(f"Data retrieval (GET) failed with status code: {get_response.status_code}")
                st.write(get_response.text)
        else:
            st.error(f"API request (POST) failed with status code: {response.status_code}")
            st.write(response.text)

        # Convert execution times to milliseconds
        post_execution_time_ms = post_execution_time * 1000
        get_execution_time_ms = get_execution_time * 1000

        # Store the execution times in the session state DataFrame
        st.session_state.execution_times = st.session_state.execution_times.append(
            {"POST Execution Time (ms)": post_execution_time_ms, "GET Execution Time (ms)": get_execution_time_ms},
            ignore_index=True
        )

        # Display execution times
        st.write(f"Time for POST Execution: {post_execution_time_ms:.2f} ms")
        st.write(f"Time for GET Execution: {get_execution_time_ms:.2f} ms")

with col2:
    st.write(
        "Click the button to execute the API call. This triggers a POST request to run a query and a GET request to "
        "retrieve the results. After a cache reload, the execution may take longer as it queries the underlying "
        "database. If clicked multiple times without cache invalidation, subsequent executions will use GoodData's "
        "FlexCache, which is faster.")

# Plot the execution times on a line chart
if not st.session_state.execution_times.empty:
    st.line_chart(st.session_state.execution_times)