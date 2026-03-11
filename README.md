# MCH Backend Framework

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