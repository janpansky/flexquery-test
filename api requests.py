import requests


def reload_cache(hostname, token, data_source_id):
    url = f"{hostname}/api/v1/dataSources/{data_source_id}/cache/reload"
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(url, headers=headers)


def execute_api_call(hostname, token, workspace_id, data):
    url = f"{hostname}/api/v1/workspaces/{workspace_id}/execution"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=data)


def get_results(hostname, token, workspace_id, execution_result_id):
    url = f"{hostname}/api/v1/workspaces/{workspace_id}/executionResults/{execution_result_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers)
