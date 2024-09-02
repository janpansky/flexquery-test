import streamlit as st
import pandas as pd
from actions import reload_cache_action, execute_query_action, capture_dashboard_load_time
from config import workspace_id, data_source_id

# Initialize session state
st.session_state.setdefault('execution_times', pd.DataFrame(columns=["Query Type", "POST Execution Time (ms)", "GET Execution Time (ms)", "Total Execution Time (ms)"]))
st.session_state.setdefault('dashboard_load_times', pd.DataFrame(columns=["Load Time (ms)"]))
st.session_state.setdefault('cache_status', 'warm')  # Track cache status

# Streamlit App Layout
st.title("GoodData in-memory caching demo")
st.markdown("""**This demo showcases the performance of querying data through GoodData's in-memory caching layer (FlexQuery), currently 
using Snowflake as the underlying database. Both systems are hosted in the US data center.**

**Example use:** Click 3 times on 'Execute Custom Query', then click on 'Reload Cache' and then again 3 times on 'Execute Custom Query'.
""")

# Buttons and Tabs
if st.button("Reload Cache"):
    reload_cache_action()

st.write("The 'Reload Cache' button clears the cache, ensuring the next API execution queries the underlying database instead of GoodData's FlexCache. Use it with caution, as it runs against Snowflake.")

tab1, tab2 = st.tabs(["Execute Custom Query", "Embedded Dashboard"])

with tab1:
    st.header("Execute Custom Query")
    if st.button("Execute Query"):
        post_time, get_time, data = execute_query_action()

        if not st.session_state.execution_times.empty:
            st.subheader("Execution Times Summary")

            # Separate data for cached and uncached queries
            cached_queries = st.session_state.execution_times[st.session_state.execution_times["Query Type"] == "cached"]
            uncached_queries = st.session_state.execution_times[st.session_state.execution_times["Query Type"] == "uncached"]

            # Display cached queries (blue bars)
            if not cached_queries.empty:
                st.bar_chart(cached_queries[["POST Execution Time (ms)", "GET Execution Time (ms)"]])

            # Overlay uncached queries (red bars)
            if not uncached_queries.empty:
                st.bar_chart(uncached_queries[["POST Execution Time (ms)", "GET Execution Time (ms)"]], use_container_width=True)

        # Display the DataFrame at the very bottom
        if data is not None:
            st.subheader("Query Result Data")
            st.write(data)

with tab2:
    st.header("Embedded Dashboard")
    if st.button("Refresh and Capture Load Time"):
        capture_dashboard_load_time()
