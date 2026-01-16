from ai_slop_gate.domain.compliance.profiles import PROFILE_REGISTRY, ComplianceProfile

class ComplianceProfileResolver:
    def resolve(self, profile_names):
        resolved = []
        visited = set()

        for name in profile_names:
            self._resolve_recursive(name, resolved, visited)

        return resolved

    def _resolve_recursive(self, name, resolved, visited):
        if name in visited:
            return

        if name not in PROFILE_REGISTRY:
            raise ValueError(f"Unknown compliance profile: {name}")

        profile = PROFILE_REGISTRY[name]

        if profile.extends:
            self._resolve_recursive(profile.extends, resolved, visited)

        resolved.append(profile)
        visited.add(name)
