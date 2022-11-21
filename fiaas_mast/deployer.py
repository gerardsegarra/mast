# Copyright 2017-2019 The FIAAS Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import yaml
from k8s.client import NotFound
from k8s.models.common import ObjectMeta
from requests.exceptions import MissingSchema, InvalidURL

from .common import generate_random_uuid_string, ClientError, check_models


class Deployer:
    def __init__(self, create_deployment_id=generate_random_uuid_string):
        self.create_deployment_id = create_deployment_id
        self.application_model, self.spec_model = check_models()

    def deploy(self, target_namespace, release):
        """Create or update TPR for application"""
        application_name = release.application_name
        config = release.config
        namespace = config["namespace"] if (config['version'] < 3) and ("namespace" in config) else target_namespace
        deployment_id = self.create_deployment_id()
        labels = {"fiaas/deployment_id": deployment_id, "app": application_name}
        metadata = ObjectMeta(name=application_name, namespace=namespace, labels=labels)
        spec = self.spec_model(application=application_name, image=release.image, config=config)
        try:
            application = self.application_model.get(application_name, namespace)
            application.metadata = metadata
            application.spec = spec
        except NotFound:
            application = self.application_model(metadata=metadata, spec=spec)
        application.save()

        return namespace, application_name, deployment_id


class DeployerError(Exception):
    pass
