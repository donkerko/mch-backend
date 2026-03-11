# MCH Backend Framework

Automation platform for MCH Vertrieb.

Repository structure:
- app/core → shared utilities
- app/domain → domain models and services
- app/excel → Excel repositories
- app/intake → mail intake logic
- app/runners → execution scripts

## Ziel
Gemeinsames Python-Framework für Lead-Verarbeitung, CRM, Projektordner und Kalkulation.

## Prinzipien
- gemeinsame Logik in `app/core`
- Excel-Zugriffe nur in `app/excel`
- Fachlogik in `app/domain/services`
- Runner-Skripte in `app/runners`

## Start
Beispiel:
python -m app.runners.run_create_project_folders
