# -*- coding: utf-8 -*-

import getpass
import re


def parse(uri, user=None, port=22):
    """
    parses ssh connection uri-like sentences.
    ex:
        - root@google.com -> (root, google.com, 22)
        - noreply@facebook.com:22 -> (noreply, facebook.com, 22)
        - facebook.com:3306 -> ($USER, facebook.com, 3306)
        - twitter.com -> ($USER, twitter.com, 22)

    default port: 22
    default user: $USER (getpass.getuser())
    """

    uri = uri.strip()

    if not user:
        user = getpass.getuser()

    # get user
    if '@' in uri:
        user = uri.split("@")[0]

    # get port
    if ':' in uri:
        port = uri.split(":")[-1]

    try:
        port = int(port)
    except ValueError:
        raise ValueError("port must be numeric.")

    # get host
    uri = re.sub(":.*", "", uri)
    uri = re.sub(".*@", "", uri)
    host = uri

    return (
        user,
        host,
        port,
    )
