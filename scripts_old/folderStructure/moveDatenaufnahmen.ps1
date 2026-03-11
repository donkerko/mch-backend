Set-Location -Path "C:\Users\PV\OneDrive\ENKO GmbH"


# Basis-Zielpfad
$targetBasePath = "C:\Users\PV\OneDrive\MCH Vertrieb\Vertrieb\ENKO\Datenaufnahmen"

# Alle passenden Word-Dateien im aktuellen Verzeichnis holen
Get-ChildItem -Path (Get-Location) -Filter "Datenaufnahme *.docx" | ForEach-Object {

    $file = $_
    
    # Dateiname ohne Erweiterung
    $nameWithoutExtension = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    
    # "Datenaufnahme " entfernen
    $personName = $nameWithoutExtension -replace "^Datenaufnahme\s+", ""
    
    # Zielordner zusammensetzen
    $targetFolder = Join-Path $targetBasePath $personName
    
    # Ordner erstellen, falls nicht vorhanden
    if (!(Test-Path $targetFolder)) {
        New-Item -Path $targetFolder -ItemType Directory | Out-Null
    }
    
    # Zieldateipfad
    $targetFilePath = Join-Path $targetFolder $file.Name
    
    # Datei verschieben
    Move-Item -Path $file.FullName -Destination $targetFilePath -Force
    #Write-Host "Würde verschieben: $($file.FullName) -> $targetFilePath"

    Write-Host "Verschoben: $($file.Name) -> $targetFolder"
}

Write-Host "Fertig."
