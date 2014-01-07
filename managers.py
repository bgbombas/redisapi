# Copyright 2014 redis-api authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os
import redis
import docker
import io


class DockerManager(object):
    def __init__(self):
        self.client = docker.Client(
            base_url='unix://var/run/docker.sock'
        )

    def add_instance(self):
        script = io.BytesIO('\n'.join([
            'FROM base',
            'RUN mkdir -p /tmp/test',
            'EXPOSE 8080',
        ]))
        self.client.build(fileobj=script)


class FakeManager(object):
    instance_added = False
    binded = False
    unbinded = False
    removed = False
    ok = False
    msg = "error"

    def add_instance(self):
        self.instance_added = True

    def bind(self):
        self.binded = True

    def unbind(self):
        self.unbinded = True

    def remove_instance(self):
        self.removed = True

    def is_ok(self):
        return self.ok, self.msg


class RedisManager(object):
    def __init__(self):
        try:
            self.server = os.environ["REDIS_SERVER_HOST"]
        except KeyError:
            msg = u"You must define the REDIS_SERVER_HOST " \
                  "environment variable."
            raise Exception(msg)

    def add_instance(self):
        pass

    def bind(self):
        host = os.environ.get("REDIS_PUBLIC_HOST", self.server)
        port = os.environ.get("REDIS_SERVER_PORT", "6379")
        result = {
            "REDIS_HOST": host,
            "REDIS_PORT": port,
        }
        pswd = os.environ.get("REDIS_SERVER_PASSWORD")
        if pswd:
            result["REDIS_PASSWORD"] = pswd
        return result

    def unbind(self):
        pass

    def remove_instance(self):
        pass

    def is_ok(self):
        passwd = os.environ.get("REDIS_SERVER_PASSWORD")
        kw = {"host": self.server}
        if passwd:
            kw["password"] = passwd
        try:
            conn = redis.Connection(**kw)
            conn.connect()
        except Exception as e:
            return False, str(e)
        return True, ""


managers = {
    'shared': RedisManager,
    'fake': FakeManager,
}