# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os

from tempest.common import accounts
from tempest.common import cred_provider
from tempest.common import isolated_creds
from tempest import config
from tempest import exceptions
import random

CONF = config.CONF


# Return the right implementation of CredentialProvider based on config
# Dropping interface and password, as they are never used anyways
# TODO(andreaf) Drop them from the CredentialsProvider interface completely
def get_isolated_credentials(name, network_resources=None,
                             force_tenant_isolation=False,
                             identity_version=None):
    # If a test requires a new account to work, it can have it via forcing
    # tenant isolation. A new account will be produced only for that test.
    # In case admin credentials are not available for the account creation,
    # the test should be skipped else it would fail.
    if CONF.auth.allow_tenant_isolation or force_tenant_isolation:
        return isolated_creds.IsolatedCreds(
            name=name,
            network_resources=network_resources,
            identity_version=identity_version)
    else:
        if (CONF.auth.test_accounts_file and
                os.path.isfile(CONF.auth.test_accounts_file)):
            # Most params are not relevant for pre-created accounts
            return accounts.Accounts(name=name,
                                     identity_version=identity_version)
        else:
            return accounts.NotLockingAccounts(
                name=name, identity_version=identity_version)


# We want a helper function here to check and see if admin credentials
# are available so we can do a single call from skip_checks if admin
# creds area vailable.
def is_admin_available():
    is_admin = True
    # If tenant isolation is enabled admin will be available
    if CONF.auth.allow_tenant_isolation:
        return is_admin
    # Check whether test accounts file has the admin specified or not
    elif (CONF.auth.test_accounts_file and
            os.path.isfile(CONF.auth.test_accounts_file)):
        check_accounts = accounts.Accounts(name='check_admin')
        if not check_accounts.admin_available():
            is_admin = False
    else:
        try:
            cred_provider.get_configured_credentials('identity_admin',
                                                     fill_in=False)
        except exceptions.InvalidConfiguration:
            is_admin = False
    return is_admin


# We want a helper function here to check and see if alt credentials
# are available so we can do a single call from skip_checks if alt
# creds area vailable.
def is_alt_available():
    # If tenant isolation is enabled admin will be available
    if CONF.auth.allow_tenant_isolation:
        return True
    # Check whether test accounts file has the admin specified or not
    if (CONF.auth.test_accounts_file and
            os.path.isfile(CONF.auth.test_accounts_file)):
        check_accounts = accounts.Accounts(name='check_alt')
    else:
        check_accounts = accounts.NotLockingAccounts(name='check_alt')
    try:
        if not check_accounts.is_multi_user():
            return False
        else:
            return True
    except exceptions.InvalidConfiguration:
        return False

def get_policy_password():
    pw_min_len = CONF.identity.policy_min_length
    mypw = ""

    u_case = CONF.identity.policy_num_uppercase
    if u_case > 0:
        for i in range(u_case):
            set = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            next_index = random.randrange(len(set))
            mypw += set[next_index]

    l_case = CONF.identity.policy_num_lowercase
    if l_case > 0:
        for i in range(l_case):
            set = "abcdefghijklmnopqrstuvwxyz"
            next_index = random.randrange(len(set))
            mypw += set[next_index]

    numeric = CONF.identity.policy_num_numeric
    if numeric > 0:
        for i in range(numeric):
            nums = "0123456789"
            next_index = random.randrange(len(nums))
            mypw += nums[next_index]

    specialchar = CONF.identity.policy_num_specialchars
    if specialchar > 0:
        for i in range(specialchar):
            s_chars = "~!@#$%^&*()_+-=:';,./<>""?{}[]\|"
            next_index = random.randrange(len(s_chars))
            mypw += s_chars[next_index]

    if len(mypw) < pw_min_len:
        for x in range(len(mypw), pw_min_len):
            alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            next_index = random.randrange(len(alphabet))
            mypw += alphabet[next_index]
    return mypw