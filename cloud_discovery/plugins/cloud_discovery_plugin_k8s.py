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
import operator
import pprint
import time

import bitmath
import click
from click import Option
from groundwork.patterns import GwCommandsPattern
from kubernetes import client
from kubernetes.client import CustomObjectsApi
from rich import box
from rich.console import Console
from rich.live import Live
from rich.table import Table

from .utils import (
    pprint_json,
    pprint_table,
    get_k8s_connection,
    check_k8s_apis,
    convert_cpu,
)


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
        k8s_top = Option(
            ("--top", "-t"), required=False, is_flag=True, help="Show pods statistic"
        )
        k8s_top_sort = Option(
            ("--sort", "-s"),
            required=False,
            type=click.Choice(["cpu", "memory"]),
            help="Sort by value",
        )
        k8s_top_limit = Option(
            ("--limit", "-m"),
            required=False,
            type=int,
            help="Number of pods in top table",
        )
        self.commands.register(
            "k8s",
            "Find Kubernetes pods by tag key",
            self._k8s_info,
            params=[
                tag_argument,
                output_format_option,
                return_instance_attribute_option,
                k8s_top,
                k8s_top_sort,
                k8s_top_limit,
            ],
        )

    def deactivate(self):
        pass

    def _k8s_get_metrics(self):
        instances = {}
        coa = CustomObjectsApi()
        pods = coa.list_cluster_custom_object(
            "metrics.k8s.io", "v1beta1", "pods", label_selector=self
        )["items"]

        for pod in pods:
            for container in pod["containers"]:
                usage_cpu = convert_cpu(container["usage"]["cpu"])
                memory_usage = bitmath.parse_string_unsafe(container["usage"]["memory"])
                memory_converted = memory_usage.best_prefix().format(
                    "{value:.3f} {unit}"
                )
                instances[pod["metadata"]["name"]] = {
                    "cpu": f"{str(round(usage_cpu, 4))}",
                    "memory": f"{memory_converted}",
                }
        return instances

    def _k8s_info(
        self,
        label=None,
        output="plain",
        attribute=None,
        top=None,
        sort=None,
        limit=None,
    ):
        instances = {}
        instances_list = []
        hostname = "None"
        v1 = get_k8s_connection()
        pods = v1.list_pod_for_all_namespaces(watch=False, label_selector=label)
        api_extensions = client.ExtensionsV1beta1Api()
        ingresses = api_extensions.list_ingress_for_all_namespaces(
            watch=False, label_selector=label
        )
        if top:
            check_k8s_apis()
            k8s_metrics = cloud_discovery_plugin_k8s._k8s_get_metrics(label)
            console = Console()
            try:
                with Live(
                    console=console,
                    auto_refresh=False,
                    vertical_overflow="crop",
                    transient=True,
                    screen=True,
                ) as live:
                    while True:
                        live.update(
                            cloud_discovery_plugin_k8s._create_k8s_top_table(
                                k8s_metrics, sort, limit
                            ),
                            refresh=True,
                        )
                        time.sleep(1)
            except KeyboardInterrupt:
                pass

        else:
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
                    attributes = [
                        "name",
                        "namespace",
                        "state",
                        "private_ip",
                        "public_ip",
                    ]
                    for instance_id, instance in instances.items():
                        for key in attributes:
                            print("{0}: {1}".format(key, instance[key]))
                        print("------")

    def _create_k8s_top_table(self, sort=None, limit=None) -> Table:
        metrics = self.items()
        if sort:
            sorted_by_dict = sorted(metrics, key=lambda x: operator.getitem(x[1], sort))
        else:
            sorted_by_dict = sorted(
                metrics, key=lambda x: operator.getitem(x[1], "cpu")
            )
        if limit:
            metrics_sorted = sorted_by_dict[: int(limit)]
        else:
            metrics_sorted = sorted_by_dict

        table = Table(
            "Pod Name",
            "Cpu cores",
            "Memory",
            title=f"PODS memory and cpu usage. Sorted by {sort}",
            box=box.DOUBLE_EDGE,
            collapse_padding=False,
            highlight=True,
        )

        for name, metric in metrics_sorted:
            table.add_row(
                str(name),
                metric["cpu"],
                str(metric["memory"]),
            )

        return table
