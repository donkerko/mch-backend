from app.domain.models.project import Project


class ProjectService:
    def __init__(self, crm_repository, folder_service):
        self.crm_repository = crm_repository
        self.folder_service = folder_service

    def create_project_from_lead(self, lead, projekt_id: str) -> Project:
        kunde = lead.full_name or lead.firma
        project_root = self.folder_service.create_project_folder_structure(kunde)

        project = Project(
            projekt_id=projekt_id,
            kunde=kunde,
            adresse=lead.adresse,
            mail=lead.email,
            telefon=lead.telefon,
            status="Lead",
            status_datum=lead.lead_datum,
            projektordner_pfad=str(project_root),
            notiz=lead.notiz,
        )

        self.crm_repository.append_project(project)
        return project