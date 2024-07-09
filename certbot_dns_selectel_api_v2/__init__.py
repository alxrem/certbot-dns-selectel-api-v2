"""
The `~certbot_dns_selectel_api_v2.dns_selectel_api_v2` plugin automates
the process of completing a ``dns-01`` challenge (`~acme.challenges.DNS01`)
by creating, and subsequently removing, TXT records using domains/v2 calls
of the Selectel REST API.

Named Arguments
---------------

=============================================  =================================
``--dns-selectel-api-v2-credentials``          Selectel API credentials
                                               INI file. (Required)
``--dns-selectel-api-v2-propagation-seconds``  The number of seconds to wait for
                                               DNS to propagate before asking
                                               the ACME server to verify the DNS
                                               record. (Default: 120)
=============================================  =================================

Credentials
-----------

Use of this plugin requires a configuration file containing numeric account ID
(usually displayed at top right corner of control panel),
`textual project name <https://docs.selectel.ru/control-panel-actions/projects/about-projects/>`
and username and password of the `service account <https://docs.selectel.ru/control-panel-actions/users-and-roles/add-user/#add-service-user>`
having administrative rights for account.

.. code-block:: ini
   :name: selectel.ini
   :caption: Example credentials file

   dns_selectel_api_v2_account_id   = 167930
   dns_selectel_api_v2_project_name = my_project
   dns_selectel_api_v2_username     = certbot_at_stage
   dns_selectel_api_v2_password     = ijK021niOuvHE7EuatA94ho6LFnAsfVU

The path to this file can be provided interactively or using the
``--dns-selectel-api-v2-credentials`` command-line argument.

Examples
--------

.. code-block:: bash
   :caption: To acquire a certificate for ``example.com``

   certbot certonly \\
      -a dns-selectel-api-v2 \\
      --dns-selectel-api-v2-credentials ~/.local/share/certbot/selectel.ini \\
      -d example.com

.. code-block:: bash
   :caption: To acquire a single certificate for both ``example.com`` and
             ``*.example.com``

   certbot certonly \\
      -a dns-selectel-api-v2 \\
      --dns-selectel-api-v2-credentials ~/.local/share/certbot/selectel.ini \\
      -d example.com \\
      -d *.example.com

.. code-block:: bash
   :caption: To acquire a certificate for ``example.com``, waiting 60 seconds
             for DNS propagation
   certbot certonly \\
      -a dns-selectel-api-v2 \\
      --dns-selectel-api-v2-credentials ~/.local/share/certbot/selectel.ini \\
      --dns-selectel-api-v2-propagation-seconds 60 \\
      -d example.com
"""
