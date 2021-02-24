#  Copyright (c) 2021, Yuriy Medvedev
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#  1. Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above
#  copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials
#  provided with the distribution.
#  3. All advertising materials mentioning features or use of this software must
#  display the following acknowledgement: This product includes software developed by the Yuriy Medvedev.
#  4.Neither the name of the Yuriy Medvedev nor the names of its contributors may be used to endorse or promote
#  products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
#  BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#  IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
#  OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
#  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import os

from azure.common.credentials import ServicePrincipalCredentials
from keystoneauth1.exceptions import Unauthorized
from openstack import connection
import openstack
import digitalocean
import logging
from linode import LinodeClient
from kubernetes import client, config


def pprint_json(json_array, sort=True, indents=4):
    if isinstance(json_array, str):
        print(json.dumps(json.loads(json_array), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_array, sort_keys=sort, indent=indents))
    return None


def pprint_table(my_dict, col_list=None):
    """
    :param my_dict:
    :param col_list:
    """
    if not col_list:
        col_list = list(my_dict[0].keys() if my_dict else [])
    my_list = [col_list]  # 1st row = header
    for item in my_dict:
        my_list.append(
            [str(item[col] if item[col] is not None else "") for col in col_list]
        )
    col_size = [max(map(len, col)) for col in zip(*my_list)]
    format_str = " | ".join(["{{:<{}}}".format(i) for i in col_size])
    my_list.insert(1, ["-" * i for i in col_size])  # Seperating line
    for item in my_list:
        print(format_str.format(*item))


def get_azure_credentials():
    azure_subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    azure_client_id = os.getenv("AZURE_CLIENT_ID")
    azure_client_secret = os.getenv("AZURE_CLIENT_SECRET")
    azure_tenant_id = os.getenv("AZURE_TENANT_ID")
    if not (
        azure_subscription_id
        or azure_client_id
        or azure_client_secret
        or azure_tenant_id
    ):
        logging.error(
            "Azure application credentials environment variable doesnt exist please check "
            "AZURE_SUBSCRIPTION_ID,AZURE_CLIENT_ID,AZURE_CLIENT_SECRET or AZURE_TENANT_ID"
        )
        exit(2)
    subscription_id = azure_subscription_id
    credentials = ServicePrincipalCredentials(
        client_id=azure_client_id, secret=azure_client_secret, tenant=azure_tenant_id
    )
    return credentials, subscription_id


def get_os_connection():
    os_auth_url = os.getenv("OS_AUTH_URL")
    os_user_name = os.getenv("OS_USERNAME")
    os_user_password = os.getenv("OS_PASSWORD")
    os_project_id = os.getenv("OS_PROJECT_ID")
    os_user_domain_id = os.getenv("OS_USER_DOMAIN_NAME")
    os_identity_interface = os.getenv("OS_INTERFACE")
    os_region = os.getenv("OS_REGION_NAME")
    if not (
        os_auth_url
        or os_user_name
        or os_user_password
        or os_project_id
        or os_user_domain_id,
        os_identity_interface,
        os_region,
    ):
        logging.error(
            "OpenStack application credentials environment variable doesnt exist please check "
            "OS_AUTH_URL, OS_USERNAME, OS_PASSWORD, OS_PROJECT_ID, OS_USER_DOMAIN_NAME, OS_INTERFACE"
        )
        exit(2)
    try:
        conn = connection.Connection(
            auth=dict(
                auth_url=f"{os_auth_url}",
                username=f"{os_user_name}",
                password=f"{os_user_password}",
                project_id=f"{os_project_id}",
                user_domain_id=f"{os_user_domain_id}",
            ),
            compute_api_version="2",
            identity_interface=f"{os_identity_interface}",
        )
        conn.compute.servers
    except Unauthorized:
        conn = openstack.connect(region_name=os_region)
    return conn


def get_do_connection():
    do_access_token = os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
    if not do_access_token:
        logging.error(
            "DIGITALOCEAN_ACCESS_TOKEN doesnt find in system envs please export DIGITALOCEAN_ACCESS_TOKEN "
            "with token"
        )
        exit(2)
    manager = digitalocean.Manager()
    return manager


def get_li_connection():
    li_access_token = os.getenv("LINODE_ACCESS_TOKEN")
    if not li_access_token:
        logging.error(
            "LINODE_ACCESS_TOKEN doesnt find in system envs please export LINODE_ACCESS_TOKEN "
            "with token"
        )
        exit(2)
    client = LinodeClient(li_access_token)
    return client


def get_gcp_connection():
    google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not google_application_credentials:
        logging.error(
            "Google application credentials environment variable doesnt exist please export "
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        exit(2)
    return google_application_credentials


def get_k8s_connection():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    return v1


def check_k8s_apis():
    for api in client.ApisApi().get_api_versions().groups:
        versions = []
        for v in api.versions:
            name = ""
            if v.version == api.preferred_version.version and len(api.versions) > 1:
                name += "*"
            name += v.version
            versions.append(name)
    if "metrics.k8s.io" in api.name:
        return True
    else:
        raise Exception(
            "Metrics are not available for kubernetes cluster. Please deploy "
            "https://github.com/kubernetes-sigs/metrics-server"
        )


def convert_cpu(cpu_usage):
    if "n" in cpu_usage[-1]:
        calc = float(cpu_usage.replace("n", "")) / 1000000000
    elif "u" in cpu_usage[-1]:
        calc = float(cpu_usage.replace("u", "")) / 100000
    elif "m" in cpu_usage[-1]:
        calc = float(cpu_usage.replace("m", "")) / 1000
    else:
        calc = cpu_usage
    return calc
