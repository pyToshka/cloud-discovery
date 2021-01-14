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

import sys
import os

APP_NAME = "cloud_discovery_app"
APP_DESCRIPTION = "Cloud Discovery"
APP_PATH = os.path.join(os.path.expanduser("~"), "Cloud Discovery")

PLUGINS = [
    "cloud_discovery_plugin",
    "cloud_discovery_plugin_azure",
    "cloud_discovery_plugin_gce",
    "cloud_discovery_plugin_k8s",
    "cloud_discovery_plugin_os",
    "cloud_discovery_plugin_do",
    "cloud_discovery_plugin_linode",
]
LOG_LEVEL = os.getenv("CLOUD_DISCOVERY_LOG_LEVEL")
if LOG_LEVEL:
    LOG_LEVEL = os.getenv("CLOUD_DISCOVERY_LOG_LEVEL")
else:
    LOG_LEVEL = "ERROR"
GROUNDWORK_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(levelname)-5s - %(message)s"},
        "debug": {
            "format": "%(asctime)s - %(levelname)-5s - %(name)-40s - %(message)-80s - %(module)s:%("
            "funcName)s(%(lineno)s)"
        },
    },
    "handlers": {
        "console_stdout": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "level": f"{LOG_LEVEL}",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "debug",
            "filename": os.path.join(APP_PATH, "cloud_discovery.log"),
            "maxBytes": 1024000,
            "backupCount": 3,
            "level": "DEBUG",
        },
        # 'file_my_plugin': {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "formatter": "debug",
        #     "filename": "logs/my_plugin.log",
        #     "maxBytes": 1024000,
        #     "backupCount": 3,
        #     'level': 'DEBUG'
        # },
    },
    "loggers": {
        "": {"handlers": ["console_stdout"], "level": "DEBUG", "propagate": False},
        "groundwork": {
            "handlers": ["console_stdout", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        # 'MyPlugin': {
        #     'handlers': ['console_stdout', 'file_my_plugin'],
        #     'level': 'DEBUG',
        #     'propagate': False
        # },
    },
}
