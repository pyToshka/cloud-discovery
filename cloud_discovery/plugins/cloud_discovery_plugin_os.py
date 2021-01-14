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

from .utils import pprint_json, pprint_table, get_os_connection


class cloud_discovery_plugin_os(GwCommandsPattern):
    def __init__(self, *args, **kwargs):
        self.name = self.__class__.__name__
        super().__init__(*args, **kwargs)

    def activate(self):
        tag_argument = Option(
            ("--tag", "-t"), required=True, type=str, help="Tag or property name"
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
            type=click.Choice(["name", "type", "state", "private_ip", "public_ip"]),
            help="Get single attribute",
        )
        self.commands.register(
            "os",
            "Find OpenStack instance info by tag key",
            self._os_info,
            params=[
                tag_argument,
                output_format_option,
                return_instance_attribute_option,
            ],
        )

    def deactivate(self):
        pass

    def _os_info(self, tag=None, output="plain", attribute=None):
        instances = {}
        instances_list = []
        instances_ips = []
        conn = get_os_connection()
        for instance in conn.compute.servers():
            if tag in instance.tags or tag in instance.metadata:
                for addresses in instance.addresses:
                    for ips in instance.addresses[addresses]:
                        instances_ips.append(ips["addr"])
                        instances_ips.reverse()
                if len(instances_ips) < 2:
                    private_ip = "None"
                else:
                    private_ip = instances_ips[0]
                flavor = conn.compute.find_flavor(instance.flavor["id"])
                instances[instance.id] = {
                    "name": instance.name,
                    "type": f"ram={flavor.ram}mb,cpu={flavor.vcpus}",
                    "state": instance.vm_state,
                    "private_ip": private_ip,
                    "public_ip": instances_ips[1],
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
                attributes = ["name", "type", "state", "private_ip", "public_ip"]
                for instance_id, instance in instances.items():
                    for key in attributes:
                        print("{0}: {1}".format(key, instance[key]))
                    print("------")
