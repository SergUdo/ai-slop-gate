class GitLabMergeRequestReporter:
    def __init__(self, project_id, mr_iid, token):
        self.project_id = project_id
        self.mr_iid = mr_iid
        self.token = token

    def report(self, report):
        # intentionally simple stub
        print("GitLab MR advisory:")
        print(report.to_markdown())
