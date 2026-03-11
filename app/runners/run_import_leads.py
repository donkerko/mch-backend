from app.config.paths import GLOBAL_LOG_DIR, ANFRAGEN_XLSX, ENKO_LEADS_XLSX
from app.core.logging_service import LoggerService
from app.core.constants import SCRIPT_IMPORT_LEADS
from app.domain.models.lead import Lead
from app.domain.services.lead_service import LeadService
from app.excel.anfragen_repository import AnfragenRepository
from app.excel.enko_leads_repository import ENKOLeadsRepository


def main():
    logger = LoggerService(GLOBAL_LOG_DIR, SCRIPT_IMPORT_LEADS)

    anfragen_repo = AnfragenRepository(ANFRAGEN_XLSX)
    enko_repo = ENKOLeadsRepository(ENKO_LEADS_XLSX)
    lead_service = LeadService(anfragen_repo, enko_repo)

    lead = Lead(
        quelle="Mundpropaganda",
        lead_datum="2026-03-06",
        vorname="Max",
        nachname="Mustermann",
        adresse="Musterstraße 1",
        plz="1010",
        ort="Wien",
        telefon="+436601234567",
        email="max@example.com",
        notiz="Testimport",
    )

    lead_service.save_lead_to_anfragen(lead)
    logger.log_global(lead.full_name, "Lead in Anfragen.xlsx gespeichert")

    # Nur ausführen, wenn die ENKO-Datei lokal als Excel-Datei erreichbar ist
    # lead_service.sync_lead_to_enko(lead)
    # logger.log_global(lead.full_name, "Lead in Leads-Marcel-Huetter.xlsx synchronisiert")


if __name__ == "__main__":
    main()