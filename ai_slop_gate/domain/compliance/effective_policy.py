class EffectiveCompliancePolicy:
    def __init__(self, profiles):
        self.forbid_licenses = set()
        self.data_regions = set()

        for profile in profiles:
            if profile.forbid_licenses:
                self.forbid_licenses.update(profile.forbid_licenses)
            if profile.data_regions:
                self.data_regions.update(profile.data_regions)
