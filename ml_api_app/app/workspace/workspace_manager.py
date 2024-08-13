import uuid
from typing import Dict, List, Any

class WorkspaceManager:
    def __init__(self):
        self.workspaces: Dict[str, Dict[str, Any]] = {}

    def create_workspace(self, workspace_name: str) -> str:
        workspace_id = str(uuid.uuid4())
        self.workspaces[workspace_id] = {
            "id": workspace_id,
            "name": workspace_name,
            "files": [],
            "configuration": {}
        }
        return workspace_id

    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        return self.workspaces[workspace_id]

    def update_workspace(self, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        self.workspaces[workspace_id].update(data)
        return self.workspaces[workspace_id]

    def delete_workspace(self, workspace_id: str) -> None:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        del self.workspaces[workspace_id]

    def list_workspaces(self) -> List[Dict[str, Any]]:
        return list(self.workspaces.values())

    def add_file_to_workspace(self, workspace_id: str, file_name: str, file_content: str) -> None:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        self.workspaces[workspace_id]["files"].append({
            "name": file_name,
            "content": file_content
        })

    def get_file_from_workspace(self, workspace_id: str, file_name: str) -> Dict[str, str]:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        for file in self.workspaces[workspace_id]["files"]:
            if file["name"] == file_name:
                return file
        raise ValueError(f"File {file_name} not found in workspace {workspace_id}")

    def update_file_in_workspace(self, workspace_id: str, file_name: str, new_content: str) -> None:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        for file in self.workspaces[workspace_id]["files"]:
            if file["name"] == file_name:
                file["content"] = new_content
                return
        raise ValueError(f"File {file_name} not found in workspace {workspace_id}")

    def delete_file_from_workspace(self, workspace_id: str, file_name: str) -> None:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        self.workspaces[workspace_id]["files"] = [
            file for file in self.workspaces[workspace_id]["files"] if file["name"] != file_name
        ]

    def list_files_in_workspace(self, workspace_id: str) -> List[str]:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        return [file["name"] for file in self.workspaces[workspace_id]["files"]]

    def update_workspace_configuration(self, workspace_id: str, configuration: Dict[str, Any]) -> None:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        self.workspaces[workspace_id]["configuration"].update(configuration)

    def get_workspace_configuration(self, workspace_id: str) -> Dict[str, Any]:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace with id {workspace_id} not found")
        return self.workspaces[workspace_id]["configuration"]
