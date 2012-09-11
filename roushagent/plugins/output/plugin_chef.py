#!/usr/bin/env python

import sys
import os
from bashscriptrunner import BashScriptRunner

name = "chef"

def setup(config={}):
    LOG.debug('Doing setup in test.py')
    if not config.has_key("script_path"):
        raise ValueError("Expecting script_path in configuration")
    script_path = [config["script_path"]]
    script = BashScriptRunner(script_path=script_path)
    chef = ChefThing(script, config)
    register_action('install_chef', chef.install_chef)
    register_action('run_chef', chef.run_chef)

def get_environment(required, optional, payload):
    env = dict([(k, v) for k, v in payload.iteritems()
                if k in required + optional])
    for r in required:
        if not r in env:
            return False, {'result_code': 22,
                           'result_str': 'Bad Request (missing %s)' % r,
                           'result_data': None}
    return True, env

def retval(result_code, result_str, result_data):
    return {'result_code': result_code,
            'result_str': result_str,
            'result_data': result_data}

def success(result_str="success", result_data=None):
    return retval(0, result_str, result_data)

class ChefThing(object):
    def __init__(self, script, config):
        self.script = script
        self.config = config
        
    def install_chef(self, input_data):
        payload = input_data['payload']
        action = input_data['action']
        required = ["CHEF_SERVER", "CHEF_VALIDATOR"]
        optional = ["CHEF_RUNLIST", "CHEF_ENVIRONMENT", "CHEF_VALIDATION_NAME"]
        success, env = get_environment(required, optional, payload)
        return env if not success
        return self.script.run_env("install-chef.sh", env, "")

    def run_chef(self, input_data):
        payload = input_data['payload']
        action = input_data['action']
        return self.script.run("run-chef.sh")

    def install_chef_server(self, input_data):
        payload = input_data['payload']
        action = input_data['action']
        success, env = get_environment([], 
                                       ["CHEF_URL", "CHEF_WEBUI_PASSWORD" ],
                                       payload)
        return env if not success
        return self.script.run_env("install-chef-server.sh", env, "")

    def get_validation_pem(self, input_data):
        try:
            with f as open("/etc/chef/validation.pem", "r"):
                return success("Success", f.read())
        except IOError as e:
            return retval(e.errno, str(e), None)
