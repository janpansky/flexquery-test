import requests


def reload_cache(hostname, token, data_source_id):
    url = f"{hostname}/api/v1/actions/dataSources/{data_source_id}/uploadNotification"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    return requests.post(url, headers=headers)


def execute_api_call(hostname, token, workspace_id, data):
    url = f"{hostname}/api/v1/actions/workspaces/{workspace_id}/execution/afm/execute"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    return requests.post(url, headers=headers, json=data)


def get_results(hostname, token, workspace_id, execution_result_id):
    url = f"{hostname}/api/v1/actions/workspaces/{workspace_id}/execution/afm/execute/result/{execution_result_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return requests.get(url, headers=headers)
