#!/usr/bin/python3
from ldap3 import *
import requests
import uuid

ad_servername = 'exapmle.com' #ldap server host
username = 'binduser' #ldap bind user
password = 'bindpasswd'
base = 'ou=Users,dc=example,dc=com' #path where search users
ldap_id = 'ldapmain' #ldap server id can ve found in /etc/gitlab/gitlab.rb. default is "main". "ldap" must be added as prefix.

gitlab_domain = 'git.example.com' #gitlab domain
private_token = 'privatetoken' #admin private token (can be find in profile settings tab)
ssl = False #is there ssl (not testet if true)

main = Server(ad_servername, get_info=ALL)
connection = Connection(main, user=username, password=password)

if not connection.bind():
	print('error in bind'. connection.result)

type = 'http://'
if ssl == True:
        type = 'https://'

user_passwd = uuid.uuid4().hex
header = {'PRIVATE-TOKEN': private_token}

users = []
user_generator = connection.extend.standard.paged_search(search_base = base,
	search_filter = '(objectClass=User)',
        search_scope = SUBTREE,
        attributes = ['sAMAccountName', 'cn', 'mail', 'distinguishedName'],
        paged_size = 5,
        generator = True)
for entry in user_generator:
        users.append(entry['attributes'])

for user in users:
	try:
		user['mail']
	except:
		user['mail'] = user['sAMAccountName'] + '@' + ad_servername
	print('Creating user:' + user['cn'])
	user_info = {'email': user['mail'], 'username': user['sAMAccountName'], 'password': user_passwd, 'name': user['cn'], 'provider': ldap_id, 'extern_uid': user['distinguishedName']}
	print(user_info)
	api_request = requests.post(type + gitlab_domain + "/api/v3/users/", data=user_info, headers=header)
	print(api_request)
