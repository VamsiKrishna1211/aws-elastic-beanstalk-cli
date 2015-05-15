# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from botocore.compat import six

from ..controllers.create import get_and_validate_envars
from ..core import fileoperations
from ..lib import utils


ENV_DELIM = ','
ENV_KV_DELIM = '='


class EnvvarCollector(object):
    """
    Immutable class for grouping environment variables to add and remove.
    """

    def __init__(self, envvars_map=None, envvars_to_remove=None):
        """
        Constructor for EnvvarCollector
        :param envvars_map: dict: contains envvars to add
        :param envvars_to_remove: set: keys of environment variables to remove
        """

        self.map = envvars_map or {}
        self.to_remove = envvars_to_remove or set()

    @classmethod
    def from_str(cls, envvars_str, variable_delim=ENV_DELIM,
                 kv_delim=ENV_KV_DELIM):
        get_and_validate_envars(envvars_str)
        if not envvars_str:
            return cls()

        all_envvars = dict(e.split(kv_delim) for e in
                           envvars_str.split(variable_delim))

        # All envvars with empty strs are ones to remove
        envvars_map = {k: v for k, v in six.iteritems(all_envvars) if v}
        envvars_to_remove = {k for k, v in six.iteritems(all_envvars) if not v}

        return cls(envvars_map, envvars_to_remove)

    def merge(self, higher_priority_env):
        """
        Merge self with higher_priority_env.
        :param higher_priority_env: EnvvarCollector: environment to merge with
        :return EnvvarCollector
        """

        envvars_map = utils.merge_dicts(low_priority=self.map,
                                        high_priority=higher_priority_env.map)
        to_remove = self.to_remove | higher_priority_env.to_remove

        return EnvvarCollector(envvars_map, to_remove)

    def filtered(self):
        """
        Return new Envvarcollector with all environment variables in self.map that
        are not in to_remove
        :return EnvvarCollector
        """

        filtered_envvars = {k: v for k, v in six.iteritems(self.map) if k not in
                            self.to_remove}
        return EnvvarCollector(filtered_envvars)
