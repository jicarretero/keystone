#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# This is a placeholder for Juno backports. Do not use this number for new
# Kilo work. New Kilo work starts after all the placeholders.

import sqlalchemy as sql

from oslo.serialization import jsonutils

def upgrade(migrate_engine):
    meta = sql.MetaData()
    meta.bind = migrate_engine
    user_table = sql.Table('user', meta, autoload=True)

    gravatar = sql.Column('gravatar', sql.Boolean, nullable=True, default=False)
    gravatar.create(user_table, populate_default=True)


def downgrade(migrate_engine):
    meta = sql.MetaData()
    meta.bind = migrate_engine
    user_table = sql.Table('user', meta, autoload=True)

    user_table.c.gravatar.drop()
