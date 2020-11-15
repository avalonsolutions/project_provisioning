
from flask import request
from flask import Flask
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import time
import urllib.parse
import os

app = Flask(__name__)


@app.route('/create', methods=['GET'])
def create():
    project_name = urllib.parse.unquote(request.args.get('project_name'))
    folder_name = request.args.get('folder_name')
    respondent_email = request.args.get('respondent_email')

    project_name = project_name.replace("'", "").replace(' ', '').lower()
    print('Creating {:s}'.format(project_name))

    if folder_name == 'Marketing':
        folder = os.environ['MARKETING_FOLDER_ID']
    elif folder_name == 'Demo':
        folder = os.environ['DEMO_FOLDER_ID']
    elif folder_name == 'Playground / Learning':
        folder = os.environ['PLAYGROUND_FOLDER_ID']
    elif folder_name == 'Managed Service':
        folder = os.environ['MS_FOLDER_ID']
    elif folder_name == 'Internal Service':
        folder = os.environ['IS_FOLDER_ID']
    else:
        folder = os.environ['PLAYGROUND_FOLDER_ID']

    credentials = GoogleCredentials.get_application_default()
    service = discovery.build(
        'cloudresourcemanager', 'v1', credentials=credentials)
    project_body = {
                'name': project_name,
                'projectId': project_name,
                'parent': {'type': 'folder',
                           'id': folder}
            }
    create_request = service.projects().create(body=project_body)
    create_request.execute()

    time.sleep(2)

    policy = get_policy(project_name)

    print('Adding {:s} as project Iam Admin'.format(respondent_email))

    policy, added = modify_policy_add_member(
        policy, 'roles/resourcemanager.projectIamAdmin',
        'user: {0}'.format(respondent_email))

    if not added:
        modify_policy_add_role(policy, 'roles/resourcemanager.projectIamAdmin',
                               'user:{0}'.format(respondent_email))

    set_policy(project_name, policy)

    service = discovery.build('cloudbilling', 'v1', credentials=credentials)
    billing_info = {
        "name": 'projects/{0}/billingInfo'.format(project_name),
        "projectId": project_name,
        "billingAccountName": 'billingAccounts/{0}'.format(
            os.environ['BILLING_ACCOUNT_ID']),
        "billingEnabled": True
        }
    update_request = service.projects().updateBillingInfo(
        name='projects/' + project_name, body=billing_info)
    update_request = update_request.execute()

    return 'OK'


def get_policy(project_id):
    """Gets IAM policy for a project."""

    # pylint: disable=no-member
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build(
        'cloudresourcemanager', 'v1', credentials=credentials)
    policy = service.projects().getIamPolicy(
        resource=project_id, body={}).execute()

    return policy


def modify_policy_add_member(policy, role, member):
    """Adds a new member to a role binding."""
    added = False
    for b in policy['bindings']:
        if b['role'] == role:
            b['members'].append(member)
            added = True

    return policy, added


def modify_policy_add_role(policy, role, member):
    """Adds a new role binding to a policy."""

    binding = {
        'role': role,
        'members': [member]
    }
    policy['bindings'].append(binding)
    return policy


def set_policy(project_id, policy):
    """Sets IAM policy for a project."""

    credentials = GoogleCredentials.get_application_default()
    service = discovery.build(
        'cloudresourcemanager', 'v1', credentials=credentials)

    policy = service.projects().setIamPolicy(
        resource=project_id, body={
            'policy': policy
        }).execute()

    return policy


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
