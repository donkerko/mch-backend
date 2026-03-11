from app.domain.models.lead import Lead


class LeadService:
    def __init__(self, anfragen_repository, enko_repository=None):
        self.anfragen_repository = anfragen_repository
        self.enko_repository = enko_repository

    def save_lead_to_anfragen(self, lead: Lead) -> None:
        self.anfragen_repository.append_lead(lead)

    def sync_lead_to_enko(self, lead: Lead) -> None:
        if self.enko_repository:
            self.enko_repository.append_lead(lead)