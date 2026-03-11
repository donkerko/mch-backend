import win32com.client


class OutlookClient:
    def __init__(self):
        self.namespace = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    def get_mailbox(self, mailbox_name: str):
        return self.namespace.Folders[mailbox_name]

    def get_folder(self, mailbox_name: str, folder_path: list[str]):
        folder = self.get_mailbox(mailbox_name)
        for part in folder_path:
            folder = folder.Folders[part]
        return folder