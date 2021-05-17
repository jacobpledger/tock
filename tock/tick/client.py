from builtins import object
import json
from typing import Dict, List, Optional

import httplib2

from tock.tick.entry import TickEntry


class ProjectNotFoundException(Exception):
    pass


class TaskNotFoundException(Exception):
    pass


class TickClient(object):
    def __init__(self, token: str, subscription_id: int, email: str):
        self.api_version: str = "v2"
        self.subscription_id = subscription_id
        self.token = token
        self.email = email

        self.headers = {
            "Authorization": f"Token token={self.token}",
            "User-Agent": f"Tock ({self.email})",
            "Content-Type": "application/json; charset=utf-8",
        }

        self._base_url: str = (
            f"https://www.tickspot.com/"
            f"{self.subscription_id}/"
            f"api/{self.api_version}/"
        )

    def _get_items(self, url: str):
        http = httplib2.Http(".cache")
        _, content = http.request(url, "GET", headers=self.headers)
        return json.loads(content.decode("utf-8"))

    def _post_items(self, url: str, data: str):
        http = httplib2.Http(".cache")
        _, content = http.request(url, "POST", body=data, headers=self.headers)
        return json.loads(content.decode("utf-8"))

    def get_projects(self) -> List[Dict]:
        return self._get_items(url=self._base_url + "/projects.json")

    def get_project_by_id(self, id_: int) -> List[Dict]:
        return self._get_items(
            url=f"{self._base_url}{id_}.json",
        )

    def get_project_by_name(self, name: str) -> Optional[Dict]:
        project = None
        projects = self.get_projects()
        project_names = [p["name"] for p in projects]
        for project in projects:
            if project.get("name") == name:
                break
        if project is not None:
            project = self._get_items(url=f"{project['url']}")
        else:
            raise ProjectNotFoundException(
                f'Project "{name}" not found! Options were:\n{project_names}.'
            )
        return project

    def get_tasks(self) -> List[Dict]:
        return self._get_items(url=f"{self._base_url}tasks.json")

    def get_project_tasks(self, project_id: int) -> List[Dict]:
        return self._get_items(url=f"{self._base_url}projects/{project_id}/tasks.json")

    def get_project_task_by_name(self, project_id: int, name: str) -> Optional[Dict]:
        task = None
        project_tasks = self.get_project_tasks(project_id=project_id)
        task_names = [task["name"] for task in project_tasks]
        for task in project_tasks:
            if task["name"] == name:
                break
        if task is not None:
            task = self._get_items(f"{task['url']}")
        else:
            raise TaskNotFoundException(
                f'Task "{name}" not found! Options were:\n{task_names}'
            )
        return task

    def create_entry(self, entry: TickEntry):
        return self._post_items(
            url=f"{self._base_url}entries.json", data=json.dumps(entry.serialize())
        )
