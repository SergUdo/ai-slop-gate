class ProviderRegistry:
    def __init__(self):
        self._providers = {}

    def register(self, provider):
        self._providers[provider.name] = provider

    def get(self, name):
        return self._providers[name]

    def all(self):
        return list(self._providers.values())
