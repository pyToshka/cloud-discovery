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
import ast
import pprint

import click
from click import Option
from groundwork.patterns import GwCommandsPattern
from kubernetes import client, config

from .utils import pprint_json, pprint_table


class cloud_discovery_plugin_k8s(GwCommandsPattern):
    def __init__(self, *args, **kwargs):
        self.name = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def activate(self):
        tag_argument = Option(
            ("--label", "-l"), required=True, type=str, help="Pods label"
        )
        output_format_option = Option(
            ("--output", "-o"),
            required=False,
            type=click.Choice(["json", "plain", "table"]),
            help="Output format for received " "information",
        )
        return_instance_attribute_option = Option(
            ("--attribute", "-a"),
            required=False,
            type=click.Choice(
                ["name", "namespace", "state", "private_ip", "public_ip"]
            ),
            help="Get single attribute",
        )
        self.commands.register(
            "k8s",
            "Find Kubernetes pods by tag key",
            self._k8s_info,
            params=[
                tag_argument,
                output_format_option,
                return_instance_attribute_option,
            ],
        )

    def deactivate(self):
        pass

    def _k8s_info(self, label=None, output="plain", attribute=None):
        instances = {}
        instances_list = []
        hostname = "None"
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False, label_selector=label)
        api_extensions = client.ExtensionsV1beta1Api()
        ingresses = api_extensions.list_ingress_for_all_namespaces(
            watch=False, label_selector=label
        )
        for pod in pods.items:
            if pod.status.phase == "Running":
                for ingress in ingresses.items:
                    for hostname in ingress.status.load_balancer.ingress:
                        if not hostname.hostname:
                            hostname = "None"
                        else:
                            hostname = hostname.hostname
                instances[pod.metadata.uid] = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "state": pod.status.phase,
                    "private_ip": pod.status.pod_ip,
                    "public_ip": hostname,
                }

        if attribute:
            for instance_id, instance in instances.items():
                print(ast.literal_eval(pprint.pformat(instance[attribute])))

        if output == "json" and not attribute:

            for instance_id, instance in instances.items():
                instances_list.append(instance)
            pprint_json(instances_list)

        elif output == "table" and not attribute:
            for instance_id, instance in instances.items():
                instances_list.append(instance)
            pprint_table(instances_list)
        else:
            if attribute:
                pass
            else:
                attributes = ["name", "namespace", "state", "private_ip", "public_ip"]
                for instance_id, instance in instances.items():
                    for key in attributes:
                        print("{0}: {1}".format(key, instance[key]))
                    print("------")
