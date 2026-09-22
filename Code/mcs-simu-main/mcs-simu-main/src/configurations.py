# -----------------------------------------------------------------------------
# mcs-simu
# Steven X. Dai
# University of York
# 2023/24
# -----------------------------------------------------------------------------

import json


class ParameterServer:
    def __init__(self):
        self.configs = []

    def load_from_file(self, config_file_path):
        # load configures from file
        try:
            with open(config_file_path, "r") as config_file:
                self.configs = json.load(config_file)
        except:
            raise EnvironmentError("Unable to open the configuration file: %s" % config_file_path)

    # this has to be protected to ensure it is thread-safe
    def write_to_file(self, config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.configs, f, ensure_ascii=False, indent=4)

    def set(self, key, value):
        try:
            self.configs[key] = value
        except:
            raise Exception(f"The parameter {key} is not existed in the configuration.")

    # [todo] support cascaded configs
    def get(self, *arg):
        key = arg[0]
        if key in self.configs:
            return self.configs[key]
        else:
            raise Exception(f"The parameter {key} is not existed in the configuration.")

    def delete(self, key):
        try:
            del self.configs[key]
        except KeyError:
            pass
