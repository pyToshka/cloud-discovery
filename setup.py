"""
Cloud Discovery
===============
"""
from setuptools import setup, find_packages
import re
import ast

_version_re = re.compile(r"__version__\s+=\s+(.*)")
with open("cloud_discovery/version.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

setup(
    name="cloud_discovery",
    version=version,
    url="https://github.com/pyToshka/cloud-discovery",
    license="BSD license",
    author="cloud_discovery",
    author_email="medvedev.yp@gmail.com",
    description="Tool for discover ip addresses of nodes in cloud environments based on meta information like tags "
    "provided by the environment.",
    long_description=__doc__,
    packages=find_packages(exclude=["ez_setup", "tests"]),
    include_package_data=True,
    platforms="any",
    setup_requires=[],
    tests_require=[],
    install_requires=[
        "groundwork>=0.1.17",
        "boto3>=1.16.48",
        "click",
        "azure-mgmt-resource>=2.2.0",
        "azure-mgmt-network>=2.7.0",
        "azure-mgmt-compute>=4.6.2",
        "google-api-python-client>=1.12.8",
        "kubernetes>=12.0.1",
        "openstacksdk>=0.52.0",
        "python-digitalocean>=1.16.0",
        "linode_api4>=3.0.2",
        "linode-api>=4.1.9b1",
        "rich==10.15.1",
        "bitmath==1.3.3.1",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    entry_points={
        "console_scripts": [
            "cloud_discovery = "
            "cloud_discovery.applications.cloud_discovery_app:start_app"
        ],
        "groundwork.plugin": [
            "cloud_discovery_plugin = "
            "cloud_discovery.plugins.cloud_discovery_plugin:"
            "cloud_discovery_plugin",
            "cloud_discovery_plugin_azure = "
            "cloud_discovery.plugins.cloud_discovery_plugin_azure:"
            "cloud_discovery_plugin_azure",
            "cloud_discovery_plugin_gce = "
            "cloud_discovery.plugins.cloud_discovery_plugin_gce:"
            "cloud_discovery_plugin_gce",
            "cloud_discovery_plugin_k8s = "
            "cloud_discovery.plugins.cloud_discovery_plugin_k8s:"
            "cloud_discovery_plugin_k8s",
            "cloud_discovery_plugin_os = "
            "cloud_discovery.plugins.cloud_discovery_plugin_os:"
            "cloud_discovery_plugin_os",
            "cloud_discovery_plugin_do = "
            "cloud_discovery.plugins.cloud_discovery_plugin_do:"
            "cloud_discovery_plugin_do",
            "cloud_discovery_plugin_linode = "
            "cloud_discovery.plugins.cloud_discovery_plugin_linode:"
            "cloud_discovery_plugin_linode",
        ],
    },
)
