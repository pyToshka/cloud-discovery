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
import socket

import click
from click import Option
from groundwork.patterns import GwCommandsPattern

from .utils import pprint_json, pprint_table, get_li_connection


class cloud_discovery_plugin_linode(GwCommandsPattern):
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
            type=click.Choice(
                ["name", "type", "state", "private_ip", "public_ip", "ipv6_address"]
            ),
            help="Get single attribute",
        )
        self.commands.register(
            "li",
            "Find Linodes info by tag key",
            self._li_info,
            params=[
                tag_argument,
                output_format_option,
                return_instance_attribute_option,
            ],
        )

    def deactivate(self):
        pass

    def _li_info(self, tag=None, output="plain", attribute=None):
        instances = {}
        instances_list = []
        client = get_li_connection()
        check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        linodes = client.get("/linode/instances")
        public_ip = "None"
        private_ip = "None"
        for instance in linodes["data"]:
            if tag in instance["tags"]:
                for ip in instance["ipv4"]:
                    location = (ip, 22)
                    result_of_check = check_socket.connect_ex(location)
                    if result_of_check == 0:
                        public_ip = ip
                    else:
                        private_ip = ip
                instances[instance["id"]] = {
                    "name": instance["label"],
                    "type": instance["type"],
                    "state": instance["status"],
                    "private_ip": private_ip,
                    "public_ip": public_ip,
                    "ipv6_address": instance["ipv6"],
                }
        if attribute:
            for instance_id, instance in instances.items():
                try:
                    print(ast.literal_eval(pprint.pformat(instance[attribute])))
                except KeyError:
                    pass

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
                try:
                    for instance_id, instance in instances.items():
                        if "ipv6_address" in instance:
                            attributes.append("ipv6_address")
                        for key in attributes:
                            print("{0}: {1}".format(key, instance[key]))
                        print("------")
                except KeyError:
                    pass
