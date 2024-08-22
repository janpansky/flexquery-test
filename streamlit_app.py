import streamlit as st
import requests
import time

# Load credentials from Streamlit's secrets management
hostname = st.secrets["api"]["hostname"]
token = st.secrets["api"]["token"]
workskpace_id = "gdc_demo_a3da0f24-9c32-4f19-9848-43dfe4096416"
data_source_id = "gdc_demo_20557729-8b95-4121-b942-6abb88b735ad"

# Streamlit app title
st.title("Test FlexQuery")

# Button to reload cache
if st.button("Reload Cache"):
    # Define the API endpoint for cache reload
    reload_url = f"{hostname}/api/v1/actions/dataSources/{data_source_id}/uploadNotification"

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Make the POST request to reload cache
    reload_response = requests.post(reload_url, headers=headers)

    # Check if the request was successful
    if reload_response.status_code < 205:
        st.success("Cache reloaded successfully!")
    else:
        st.error(f"Cache reload failed with status code: {reload_response.status_code}")
        st.write(reload_response.text)

# Button to execute the API call
if st.button("Execute API"):
    # Start timing the POST request execution
    post_start_time = time.time()

    # Define the API endpoint for POST
    url = f"{hostname}/api/v1/actions/workspaces/{workskpace_id}/execution/afm/execute"

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Define the JSON body
    data = {
        "resultSpec": {
            "dimensions": [
                {
                    "localIdentifier": "dim_0",
                    "itemIdentifiers": ["a_product_category", "a_date.quarter"],
                    "sorting": [
                        {
                            "attribute": {
                                "attributeIdentifier": "a_product_category",
                                "sortType": "DEFAULT"
                            }
                        }
                    ]
                },
                {
                    "localIdentifier": "dim_1",
                    "itemIdentifiers": ["measureGroup"]
                }
            ],
            "totals": []
        },
        "execution": {
            "measures": [
                {
                    "localIdentifier": "m_order_unit_cost",
                    "definition": {
                        "measure": {
                            "item": {
                                "identifier": {"id": "order_unit_cost", "type": "fact"}
                            },
                            "aggregation": "SUM"
                        }
                    }
                },
                {
                    "localIdentifier": "m_of_net_sales",
                    "definition": {
                        "measure": {
                            "item": {
                                "identifier": {"id": "of_net_sales", "type": "metric"}
                            }
                        }
                    }
                },
                {
                    "localIdentifier": "m_of_orders",
                    "definition": {
                        "measure": {
                            "item": {
                                "identifier": {"id": "of_orders", "type": "metric"}
                            }
                        }
                    }
                },
                {
                    "localIdentifier": "m_of_orders_by_customer",
                    "definition": {
                        "measure": {
                            "item": {
                                "identifier": {"id": "of_orders_by_customer", "type": "metric"}
                            }
                        }
                    }
                }
            ],
            "attributes": [
                {
                    "label": {
                        "identifier": {"id": "product_category", "type": "label"}
                    },
                    "localIdentifier": "a_product_category"
                },
                {
                    "label": {
                        "identifier": {"id": "date.quarter", "type": "label"}
                    },
                    "localIdentifier": "a_date.quarter"
                }
            ],
            "filters": [],
            "auxMeasures": []
        },
        "settings": {}
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=data)

    # Stop timing the POST request execution
    post_end_time = time.time()
    post_execution_time = post_end_time - post_start_time

    # Check if the POST request was successful
    if response.status_code == 200:
        st.success("API call (POST) was successful!")
        result = response.json()

        # Extract the result ID from the POST response
        execution_result_id = result["executionResponse"]["links"]["executionResult"]

        # Start timing the GET request execution
        get_start_time = time.time()

        # Define the API endpoint for GET using the execution result ID
        result_url = f"{hostname}/api/v1/actions/workspaces/{workskpace_id}/execution/afm/execute/result/{execution_result_id}"

        # Make the GET request to fetch the results
        get_response = requests.get(result_url, headers=headers)

        # Stop timing the GET request execution
        get_end_time = time.time()
        get_execution_time = get_end_time - get_start_time

        # Check if the GET request was successful
        if get_response.status_code == 200:
            st.success("Data retrieval (GET) was successful!")
            st.json(get_response.json())  # Display the JSON result in the app
        else:
            st.error(f"Data retrieval (GET) failed with status code: {get_response.status_code}")
            st.write(get_response.text)

    else:
        st.error(f"API request (POST) failed with status code: {response.status_code}")
        st.write(response.text)

    # Convert execution times to milliseconds
    post_execution_time_ms = post_execution_time * 1000
    get_execution_time_ms = get_execution_time * 1000

    # Print execution times
    st.write(f"Time for POST Execution: {post_execution_time_ms:.2f} ms")
    st.write(f"Time for GET Execution: {get_execution_time_ms:.2f} ms")