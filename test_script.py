import urllib.request
import json

def post(url, data, token=None):
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode(), 
        headers={'Content-Type': 'application/json'}
    )
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        print(f"HTTPError on {url}: {e.code}")
        import re
        match = re.search(r'<pre class="exception_value">(.*?)</pre>', content, re.DOTALL)
        if match:
            print("Exception:", match.group(1).strip())
        else:
            print("Response:", content[:500])
        raise

print("Getting tokens...")
t = post('http://127.0.0.1:8000/api/auth/login/', {'username':'agent_ravi', 'password':'pass123'})['access']
tl = post('http://127.0.0.1:8000/api/auth/login/', {'username':'tl_alpha', 'password':'pass123'})['access']

print("\nCreating Task as Lead...")
task = post('http://127.0.0.1:8000/api/tasks/', {'title': 'PyTest', 'description': 'desc', 'priority': 'high', 'due_date': '2026-06-01', 'assigned_to': 5}, tl)

import urllib.request as urllib2
req = urllib2.Request('http://127.0.0.1:8000/api/tasks/')
req.add_header('Authorization', f'Bearer {t}')
tasks = json.loads(urllib2.urlopen(req).read())
task_id = tasks[0]['id'] if isinstance(tasks, list) else tasks['results'][0]['id']
print(f"Task created with ID: {task_id}")

print("\nStarting Visit as Agent...")
visit = post('http://127.0.0.1:8000/api/visits/start/', {'task_id': task_id}, t)
visit_id = visit['id']
print(f"Visit started with ID: {visit_id}")

try:
    print("\nCompleting Visit with High Risk notes...")
    comp = post(f'http://127.0.0.1:8000/api/visits/{visit_id}/complete/', {'visit_notes': 'angry customer refused service'}, t)
    print(f"Visit completed! AI Risk Flag: {comp.get('ai_risk_flag')}")
    print(f"AI Summary: {comp.get('ai_summary')}")

    print("\nGetting auditor token...")
    auditor = post('http://127.0.0.1:8000/api/auth/login/', {'username':'auditor_meera', 'password':'pass123'})['access']

    print("\nFetching logs as Auditor...")
    req = urllib2.Request('http://127.0.0.1:8000/api/logs/?entity_type=visit&action=completed')
    req.add_header('Authorization', f'Bearer {auditor}')
    logs = json.loads(urllib2.urlopen(req).read())
    results = logs.get('results', logs) if isinstance(logs, dict) else logs
    print(f"Auditor sees {len(results)} completed visit logs.")
    if len(results) > 0:
        print(f"Latest log: {results[0]['description']}")

    print("\nFetching logs as Agent (should fail)...")
    try:
        req = urllib2.Request('http://127.0.0.1:8000/api/logs/')
        req.add_header('Authorization', f'Bearer {t}')
        urllib2.urlopen(req)
        print("FAILED: Agent was able to fetch logs!")
    except urllib.error.HTTPError as e:
        print(f"SUCCESS: Agent got HTTP {e.code} (Forbidden)")

except Exception as e:
    print(f"Error occurred: {e}")
