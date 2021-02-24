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
import logging
import os
import pprint

import click
import googleapiclient.discovery

from click import Option
from groundwork.patterns import GwCommandsPattern

from .utils import pprint_json, pprint_table, get_gcp_connection


def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result["items"] if "items" in result else None


class cloud_discovery_plugin_gce(GwCommandsPattern):
    def __init__(self, *args, **kwargs):
        self.name = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def activate(self):
        tag_argument = Option(("--tag", "-t"), required=True, type=str, help="Tag name")
        output_format_option = Option(
            ("--output", "-o"),
            required=False,
            type=click.Choice(["json", "plain", "table"]),
            help="Output format for received " "information",
        )
        return_instance_attribute_option = Option(
            ("--attribute", "-a"),
            required=False,
            type=click.Choice(["name", "type", "state", "private_ip", "public_ip"]),
            help="Get single attribute",
        )
        region_option = Option(
            ("--region", "-r"),
            required=True,
            type=str,
            help="Zone name for example us-central1-a",
        )
        project_option = Option(
            ("--project", "-p"), required=True, type=str, help="Project name"
        )
        self.commands.register(
            "gce",
            "Find GCE vms by tag key",
            self._gce_info,
            params=[
                tag_argument,
                output_format_option,
                return_instance_attribute_option,
                region_option,
                project_option,
            ],
        )

    def deactivate(self):
        pass

    def _gce_info(
        self, tag, region=None, project=None, output="plain", attribute="public_ip"
    ):
        instances = {}
        instances_list = []
        public_ip = ""
        private_ip = ""
        get_gcp_connection()
        compute = googleapiclient.discovery.build("compute", "v1")
        vm = list_instances(compute, project, region)
        for instance in vm:
            try:
                if instance["status"] == "RUNNING" and tag in instance["labels"]:
                    instance_type = " ".join(instance["machineType"].split("/")[-1:])
                    for network in instance["networkInterfaces"]:
                        private_ip = network["networkIP"]
                        for public_ips in network["accessConfigs"]:
                            public_ip = public_ips["natIP"]
                    instances[instance["id"]] = {
                        "name": instance["name"],
                        "type": instance_type,
                        "state": instance["status"],
                        "private_ip": private_ip,
                        "public_ip": public_ip,
                    }
            except KeyError:
                pass
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
                attributes = ["name", "type", "state", "private_ip", "public_ip"]
                for instance_id, instance in instances.items():
                    for key in attributes:
                        print("{0}: {1}".format(key, instance[key]))
                    print("------")
