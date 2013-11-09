usage
=================================


adding hosts
++++++++++++++++++++

.. code-block:: bash

    $ storm add [-h]  [--id_file ID_FILE] name connection_uri

where `-h`, `id_file` are optional arguments.

example:

.. code-block:: bash

    $ storm add my_vps root@emreyilmaz.me:22
    my_vps added to your ssh config. you can connect it by typing "ssh my_vps".

editing hosts
++++++++++++++++++++

.. code-block:: bash

    storm edit [-h] [--id_file ID_FILE] name connection_uri

Where `-h`, `id_file` are optional arguments.

example:

.. code-block:: bash

    $ storm edit my_vps emre@emreyilmaz.me:2400
    "my_vps" updated successfully.

deleting hosts
++++++++++++++++++++

.. code-block:: bash

    $ storm delete name

example:

.. code-block:: bash

    $ storm delete my_vps
    success hostname "my_vps" deleted successfully.

searching hosts
++++++++++++++++++++

.. code-block:: bash

    $ storm search git
    Listing results for git:
      github -> emre@github.com:22

listing hosts
++++++++++++++++++++

.. code-block:: bash

    $ storm list
    Listing hosts:
      vps -> 22@emreyilmaz.me:22
      netscaler -> root@127.0.0.1:8081

deleting all hosts
+++++++++++++++++++++++

.. code-block:: bash

    $ storm delete_all
    all entries deleted.

custom ssh config directives
+++++++++++++++++++++++++++++

storm does not wrap/cover all of the SSHConfig directives since there is a billion of them. But,
other than adding it manually to your ssh config file, you can use **--o** parameter to accomplish this.

It works both add and edit sub commands.

.. code-block:: bash
    $ storm add web-prod web@webprod.com --o "StrictHostKeyChecking=no" --o "UserKnownHostsFile=/dev/null"

command aliases
+++++++++++++++++++++++++++++

create a config file in: **/home/$user/.stormssh/config**

.. code-block:: javascript

    {
        "aliases": {
            "add": ["create", "touch"],
            "delete": ["rm"]
        }

    }


connection uri format
+++++++++++++++++++++++++++++

    - user@server:port (root@server.com:22)
    - server:port (server.com:22)
    - server (server.com)

defaults for user -> $USER, port -> 22 if they are not specified.

see `ssh_uri_parser <https://github.com/emre/storm/blob/master/storm/ssh_uri_parser.py>`_ for further look.
