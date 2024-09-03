import streamlit as st
import time
import pandas as pd
from api_requests import reload_cache, execute_api_call, get_results
from utils import load_json_body
from config import hostname, token, workspace_id, data_source_id


# Function to reload the cache
def reload_cache_action():
    response = reload_cache(hostname, token, data_source_id)
    if response.status_code < 205:
        st.success("Cache reloaded successfully!")
        st.session_state.cache_status = 'reloaded'  # Mark cache as reloaded
    else:
        st.error(f"Cache reload failed with status code: {response.status_code}")
        st.write(response.text)


# Function to execute the query
def execute_query_action():
    post_time, get_time, data = measure_query_execution()  # Capture the data from the execution
    update_execution_times(post_time, get_time)
    return post_time, get_time, data  # Return the times and data


# Function to measure the execution times
def measure_query_execution():
    query_type = "uncached" if st.session_state.get('cache_status') == 'reloaded' else "cached"

    post_start = time.time()
    response = execute_api_call(hostname, token, workspace_id, load_json_body("request_body.json"))
    post_time = (time.time() - post_start) * 1000

    if response.status_code != 200:
        st.error(f"API request (POST) failed with status code: {response.status_code}")
        st.write(response.text)
        return None, None, None

    st.success("API call (POST) was successful!")
    exec_result_id = response.json()["executionResponse"]["links"]["executionResult"]

    get_start = time.time()
    get_response = get_results(hostname, token, workspace_id, exec_result_id)
    get_time = (time.time() - get_start) * 1000

    if get_response.status_code == 200:
        st.success("Data retrieval (GET) was successful!")
        data = convert_response_to_dataframe(get_response.json())  # Convert the retrieved data to a DataFrame
        st.write(f"Aggregated data retrieved: {data.shape[0]} rows and {data.shape[1]} columns")
    else:
        st.error(f"Data retrieval (GET) failed with status code: {get_response.status_code}")
        st.write(get_response.text)
        return post_time, get_time, None

    if query_type == "uncached":
        st.session_state.cache_status = 'warm'  # Reset cache status after the uncached query

    return post_time, get_time, data


# Function to update the execution times
def update_execution_times(post_time, get_time):
    if post_time is not None and get_time is not None:
        query_type = "uncached" if st.session_state.get('cache_status') == 'reloaded' else "cached"
        st.session_state.execution_times = pd.concat([st.session_state.execution_times,
                                                      pd.DataFrame({"Query Type": [query_type],
                                                                    "POST Execution Time (ms)": [post_time],
                                                                    "GET Execution Time (ms)": [get_time],
                                                                    "Total Execution Time (ms)": [
                                                                        post_time + get_time]})],
                                                     ignore_index=True)
        st.write(f"Time for POST Execution: {post_time:.2f} ms")
        st.write(f"Time for GET Execution: {get_time:.2f} ms")


# Function to convert JSON response to DataFrame
def convert_response_to_dataframe(response_json):
    # Extract the attribute values (Product Category, Date, etc.)
    attribute_headers = [
        header["attributeHeader"]["labelValue"]
        for header in response_json["dimensionHeaders"][0]["headerGroups"][0]["headers"]
    ]

    time_headers = [
        header["attributeHeader"]["labelValue"]
        for header in response_json["dimensionHeaders"][0]["headerGroups"][1]["headers"]
    ]

    # Calculate the expected length of the data
    num_data_rows = len(response_json["data"])
    num_attributes = len(attribute_headers)
    num_time_periods = len(time_headers)

    # Assume that attributes are repeated for each time period
    attributes_repeated = attribute_headers * (num_data_rows // num_attributes)
    time_periods_repeated = time_headers * (num_data_rows // num_time_periods)

    # Ensure all arrays are the same length
    if len(attributes_repeated) != num_data_rows or len(time_periods_repeated) != num_data_rows:
        st.error("Mismatch in lengths of data arrays. Please check the response structure.")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

    # Extract the data (measures)
    data = response_json["data"]

    # Combine attributes and measures into a DataFrame
    df = pd.DataFrame(
        {
            "Product Category": attributes_repeated,
            "Time Period": time_periods_repeated,
            "Measure 1": [row[0] for row in data],
            "Measure 2": [row[1] for row in data],
            "Measure 3": [row[2] for row in data],
            "Measure 4": [row[3] for row in data],
        }
    )

    return df


# Function to display the data once after execution
def display_data(data):
    st.subheader("Query Result Data")
    st.write(data)


# Function to capture dashboard load time
def capture_dashboard_load_time():
    st.session_state.dashboard_load_times = pd.DataFrame(
        columns=["Initialization Load Time (ms)", "Render Complete Load Time (ms)"])
    st.session_state.dashboard_load_time_initialization = None
    st.session_state.dashboard_load_time_render_complete = None
    st.components.v1.html(generate_dashboard_html(), height=600)
    display_dashboard_load_time()


# Function to generate dashboard HTML
def generate_dashboard_html():
    return f"""
        <div class="responsive-web-component-container">
            <script type="module" src="{hostname}/components/gdc_demo_a3da0f24-9c32-4f19-9848-43dfe4096416.js?auth=sso"></script>
            <gd-dashboard 
                id="myDashboard"
                dashboard="c1d67cd4-94ad-40aa-91a5-cdf4143f778a"
            ></gd-dashboard>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var start = performance.now();
                var dashboard = document.getElementById('myDashboard');

                function sendLoadTime(type, loadTime) {{
                    window.parent.postMessage({{type: type, loadTime: loadTime}}, '*');
                }}

                function measureLoadTime(type) {{
                    var end = performance.now();
                    var loadTime = end - start;
                    console.log(type + ' Load Time:', loadTime, 'ms');  // Log load time to console
                    sendLoadTime(type, loadTime);
                }}

                dashboard.addEventListener('GDC.DASH/EVT.INITIALIZED', function() {{
                    measureLoadTime('Initialization');
                }});

                dashboard.addEventListener('GDC.DASH/EVT.RENDER.RESOLVED', function() {{
                    measureLoadTime('RenderComplete');
                }});
            }});
        </script>
    """


# Function to display dashboard load time
def display_dashboard_load_time():
    load_time_placeholder = st.empty()
    if st.session_state.dashboard_load_time_initialization is not None:
        load_time_placeholder.write(
            f"Dashboard Initialization Load Time: {st.session_state.dashboard_load_time_initialization:.2f} ms")
        st.session_state.dashboard_load_times = pd.concat([st.session_state.dashboard_load_times,
                                                           pd.DataFrame({"Initialization Load Time (ms)": [
                                                               st.session_state.dashboard_load_time_initialization]})],
                                                          ignore_index=True)
    else:
        load_time_placeholder.write("Dashboard Initialization Load Time: Not yet captured")

    if st.session_state.dashboard_load_time_render_complete is not None:
        load_time_placeholder.write(
            f"Dashboard Render Complete Load Time: {st.session_state.dashboard_load_time_render_complete:.2f} ms")
        st.session_state.dashboard_load_times = pd.concat([st.session_state.dashboard_load_times,
                                                           pd.DataFrame({"Render Complete Load Time (ms)": [
                                                               st.session_state.dashboard_load_time_render_complete]})],
                                                          ignore_index=True)
    else:
        load_time_placeholder.write("Dashboard Render Complete Load Time: Not yet captured")

    if not st.session_state.dashboard_load_times.empty:
        st.line_chart(st.session_state.dashboard_load_times)
