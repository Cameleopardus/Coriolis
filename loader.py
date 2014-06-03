import imp
import os

PluginFolder = "./plugins"
MainModule = "__init__"


class Loader():
    def get(self, plugin):
        return imp.load_module(MainModule, *plugin["info"])

    def load(self):
        plugins = []
        possibleplugins = os.listdir(PluginFolder)
        for i in possibleplugins:
            location = os.path.join(PluginFolder, i)
            if not os.path.isdir(location) or not MainModule + ".py" in os.listdir(location):
                continue
            info = imp.find_module(MainModule, [location])
            plugins.append({"name": i, "info": info})
        return plugins