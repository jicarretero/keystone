# Copyright (C) 2015 Universidad Politecnica de Madrid
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

import six

from keystone.auth.plugins.password import UserAuthInfo, Password
from keystone.common import dependency
from keystone import exception
from keystone.i18n import _
from keystone.openstack.common import log


LOG = log.getLogger(__name__)

METHOD_NAME = 'password'
      
@dependency.requires('assignment_api', 'identity_api')
class UserTwoFactorAuthInfo(UserAuthInfo):
    @staticmethod
    def create(auth_payload):
        user_auth_info = UserTwoFactorAuthInfo()
        user_auth_info._validate_and_normalize_auth_data(auth_payload)
        return user_auth_info

    def __init__(self):
        super(UserTwoFactorAuthInfo, self).__init__()
        self.verification_code = None

    def _validate_and_normalize_auth_data(self, auth_payload):
        super(UserTwoFactorAuthInfo, self)._validate_and_normalize_auth_data(auth_payload)
        verification_code = auth_payload['user'].get('verification_code', None)
        if not verification_code:
            raise exception.ValidationError(attribute='verification_code', target=METHOD_NAME)
        self.verification_code = verification_code


@dependency.requires('two_factor_auth_api')
class TwoFactor(Password):

    method = METHOD_NAME

    def authenticate(self, context, auth_payload, auth_context):
        """Two factor authentication"""

        if not self.two_factor_auth_api:
            raise exception.Unauthorized(_('%s not supported') % self.method)

        user_info = UserAuthInfo.create(auth_payload)
        user_id = user_info.user_id

        try:
            self.two_factor_auth_api.is_two_factor_enabled(user_id)
        except exception.NotFound:
            return super(TwoFactor, self).authenticate(context, auth_payload, auth_context)

        user_info = UserTwoFactorAuthInfo.create(auth_payload)

        if not self.two_factor_auth_api.verify_code(user_id, user_info.verification_code):
            raise exception.Unauthorized(_('Invalid time based code'))
        
        return super(TwoFactor, self).authenticate(context, auth_payload, auth_context)
            