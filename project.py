class Project:
    def __init__(self, project_name, repository_names):
        self.project_name = project_name
        self.repository_names = repository_names

    def __str__(self):
        return f"Project Name: {self.project_name}, Repository Names: {', '.join(self.repository_names)}"
