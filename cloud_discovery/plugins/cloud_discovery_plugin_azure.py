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
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from click import Option
from groundwork.patterns import GwCommandsPattern

from .utils import pprint_json, pprint_table, get_azure_credentials


class cloud_discovery_plugin_azure(GwCommandsPattern):
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
            ("--resource_group", "-r"),
            required=False,
            type=str,
            help="Azure resource group name",
        )
        self.commands.register(
            "azure",
            "Find Azure vms by tag key",
            self._azure_info,
            params=[
                tag_argument,
                output_format_option,
                return_instance_attribute_option,
                region_option,
            ],
        )

    def deactivate(self):
        pass

    def _azure_info(
        self, tag, resource_group=None, output="plain", attribute="public_ip"
    ):

        credentials, subscription_id = get_azure_credentials()
        compute_client = ComputeManagementClient(credentials, subscription_id)
        network_client = NetworkManagementClient(credentials, subscription_id)
        instances = {}
        instances_list = []
        for vm in compute_client.virtual_machines.list(resource_group):
            try:
                if vm.tags[tag]:
                    vm_state = compute_client.virtual_machines.instance_view(
                        resource_group_name=resource_group, vm_name=vm.name
                    )
                    for interface in vm.network_profile.network_interfaces:
                        name = " ".join(interface.id.split("/")[-1:])
                        sub = "".join(interface.id.split("/")[4])
                        try:
                            vms_networks = network_client.network_interfaces.get(
                                sub, name
                            ).ip_configurations
                            for ips in vms_networks:
                                if ips.public_ip_address:
                                    public_ip = ips.public_ip_address
                                else:
                                    public_ip = "None"
                                instances[vm.vm_id] = {
                                    "name": vm.name,
                                    "type": vm.hardware_profile.vm_size,
                                    "state": vm_state.statuses[1].code,
                                    "private_ip": ips.private_ip_address,
                                    "public_ip": public_ip,
                                }

                        except TypeError:
                            print("Not found")
            except TypeError:
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
