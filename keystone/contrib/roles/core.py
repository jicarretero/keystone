# Copyright (C) 2014 Universidad Politecnica de Madrid
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

import abc
import six

from keystone.common import dependency
from keystone import exception
from keystone.common import extension
from keystone.common import manager

from keystone.openstack.common import log


LOG = log.getLogger(__name__)

EXTENSION_DATA = {
    'name': 'UPM-FIWARE Roles API',
    'namespace': 'https://github.com/ging/keystone/'
                 'OS-ROLES/v1.0',
    'alias': 'OS-ROLES',
    'updated': '2014-11-3T12:00:0-00:00',
    'description': 'UPM\'s Roles provider for applications in the FIWARE GE \
                    Identity Manager implementation',
    'links': [
        {
            'rel': 'describedby',
            # TODO(garcianavalon): needs a description
            'type': 'text/html',
            'href': 'https://github.com/ging/keystone/wiki',
        }
    ]}
extension.register_admin_extension(EXTENSION_DATA['alias'], EXTENSION_DATA)
extension.register_public_extension(EXTENSION_DATA['alias'], EXTENSION_DATA)

ASSIGN_ALL_ROLES_PERMISSION = 'Get and assign all application roles'
ASSIGN_OWNED_ROLES_PERMISSION = 'Get and assign only owned roles'

@dependency.provider('roles_api')
class RolesManager(manager.Manager):
    """Roles and Permissions Manager.

    See :mod:`keystone.common.manager.Manager` for more details on
    how this dynamically calls the backend.

    """

    def __init__(self):
        super(RolesManager, self).__init__(
            'keystone.contrib.roles.backends.sql.Roles')


    def list_roles_allowed_to_assign(self, user_id, organization_id):
        """List the roles that a given user can assign. To be able to assign roles
        a user needs a certain permission. It can be the 'get and assign all
        application's roles' or the 'get and assign owned roles'

        :param user_id: user with roles
        :type user_id: string
        :param organization_id: organization-scope
        :type organization_id: string
        ;returns: list.
        """
        allowed_roles = {}
        user_roles = self.driver.list_roles_for_user(user_id)
        applications = set([r['application'] for r in user_roles])
        for application in applications:
            permissions = [p['name'] for p in self.driver.list_permissions(
                                                            application=application,
                                                            is_internal=True)]
            # NOTE(garcianavalon) this is a very poor way to do it, if in the future
            # a more complex logic and system is required refactor this
            if ASSIGN_ALL_ROLES_PERMISSION in permissions:
                # add all roles in the application
                allowed_roles[application] = self.driver.list_roles(
                                                    application=application)
            elif ASSIGN_OWNED_ROLES_PERMISSION in permissions:
                # add only the roles the user has in the application
                allowed_roles[application] = [r for r in user_roles 
                                                if r['application'] == application]
        return allowed_roles


@dependency.requires('assignment_api', 'identity_api')
@six.add_metaclass(abc.ABCMeta)
class RolesDriver(object):
    """Interface description for Roles and Permissions driver."""

    # ROLES
    @abc.abstractmethod
    def list_roles(self, **kwargs):
        """List all created roles

        :returns: roles list as dict

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def create_role(self, role):
        """Create a new role

        :param role: role data
        :type role: dict
        :returns: role as dict

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def get_role(self, role_id):
        """Get role details
        
        :param role_id: role id
        :type role_id: string
        :returns: role

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def update_role(self, role_id, role):
        """Update role details
        
        :param role_id: id of role to update
        :type role_id: string
        :param role: new role data
        :type role: dict
        :returns: role

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def delete_role(self, role_id):
        """Delete role.

        :param role_id: id of role to delete
        :type role_id: string
        :returns: None.

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def list_roles_for_user(self, user_id, organization_id=None):
        """List roles for a user_id. Optional organization filtering

        :param user_id: user with roles
        :type user_id: string
        :param organization_id: organization-scope in which we want to list the
            roles of the user. If we want user-scoped roles it should be the id of
            the user default organization (the project created with same name as user
            when user registration). Optional parameter
        :type organization_id: string
        ;returns: list.
        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def add_role_to_user(self, role_id, user_id, organization_id):
        """Delete role.

        :param role_id: id of role to add user to
        :type role_id: string
        :param user_id: user to add to role
        :type user_id: string
        :param organization_id: organization-scope in which we are giving the
            role to the user. If is a user-scoped role it should be the id of
            the user default organization (the project created with same name as user
            when user registration)
        :type organization_id: string
        :returns: None.

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def remove_role_from_user(self, role_id, user_id, organization_id):
        """Remove user from role.

        :param role_id: id of role to remove user from
        :type role_id: string
        :param user_id: user to remove from role
        :type user_id: string
        :param organization_id: organization-scope in which the role was given to the user. 
            If is a user-scoped role it should be the id of the user default organization 
            (the project created with same name as user when user registration)
        :type organization_id: string
        :returns: None.

        """
        raise exception.NotImplemented()   
    
    # PERMISSIONS
    @abc.abstractmethod
    def list_permissions(self, **kwargs):
        """List all created permissions

        :returns: permissions list as dict

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def create_permission(self, permission):
        """Create a new permission

        :param permission: permission data
        :type permission: dict
        :returns: permission as dict

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def get_permission(self, permission_id):
        """Get permission details
        
        :param permission_id: permission id
        :type permission_id: string
        :returns: permission

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def update_permission(self, permission_id, permission):
        """Update permission details
        
        :param permission_id: id of permission to update
        :type permission_id: string
        :param permission: new permission data
        :type permission: dict
        :returns: permission

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def delete_permission(self, permission_id):
        """Delete permission.

        :param permission_id: id of permission to delete
        :type permission_id: string
        :returns: None.

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def list_permissions_for_role(self, role_id):
        """List permissions for role.

        :param role_id: id of role to remove permission from
        :type role_id: string
        :param permission_id: permission to remove from role
        :type permission_id: string
        :returns: None.

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def add_permission_to_role(self, role_id, permission_id):
        """Delete role.

        :param role_id: id of role to add permission to
        :type role_id: string
        :param permission_id: permission to add to role
        :type permission_id: string
        :returns: None.

        """
        raise exception.NotImplemented()

    @abc.abstractmethod
    def remove_permission_from_role(self, role_id, permission_id):
        """Remove Permission from role.

        :param role_id: id of role to remove permission from
        :type role_id: string
        :param permission_id: permission to remove from role
        :type permission_id: string
        :returns: None.

        """
        raise exception.NotImplemented()
