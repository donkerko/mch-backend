Option Explicit

Dim outlook, namespace, mailbox, folder, items, restrictedItems
Dim attachment, savePath, logPath, fso, logStream
Dim today, logFileName

' === CONFIG ===
savePath = "C:\Users\PV\OneDrive\Sicherheitssysteme Vöcklabruck GmbH\Angebote"
' =================

Set outlook = CreateObject("Outlook.Application")
Set namespace = outlook.GetNamespace("MAPI")

' === Specify logging ===

today = Year(Now) & "-" & Right("0" & Month(Now),2) & "-" & Right("0" & Day(Now),2)
logFileName = logPath & "outlook_pdf_log_" & today & ".txt"

Set logStream = fso.OpenTextFile(logFileName, 8, True)
logStream.WriteLine "==== Hourly Run Start: " & Now & " ===="



' === Access specific mailbox ===
Set mailbox = namespace.Folders("huetter@mchvertrieb.at")

If mailbox Is Nothing Then
    MsgBox "Mailbox not found!"
    WScript.Quit
End If

' === Access top-level folder ===
Set folder = mailbox.Folders("Sicherheitssysteme")

If folder Is Nothing Then
    MsgBox "Folder 'Sicherheitssysteme' not found!"
    WScript.Quit
End If

Set items = folder.Items
Set fso = CreateObject("Scripting.FileSystemObject")

For Each mail In items

    If mail.Class = 43 Then

        If mail.Categories <> "Processed" Then

            For Each attachment In mail.Attachments

                If LCase(Right(attachment.FileName, 4)) = ".pdf" Then

                    fileName = attachment.FileName
                    newFilePath = savePath & fileName
                    counter = 1

                    While fso.FileExists(newFilePath)
                        newFilePath = savePath & counter & "_" & fileName
                        counter = counter + 1
                    Wend

                    attachment.SaveAsFile newFilePath
                    logStream.WriteLine Now & " | Saved: " & newFilePath

                End If

            Next

            mail.Categories = "Processed"
            mail.Save
            logStream.WriteLine Now & " | Marked Processed: " & mail.Subject

        End If
    End If
Next

logStream.WriteLine "==== Hourly Run End ===="
logStream.Close



--------------------------------

Option Explicit

Dim outlook, namespace, mailbox, folder, items, restrictedItems
Dim attachment, savePath, logPath, fso, logStream
Dim filter, lastCheckTime
Dim today, logFileName

' === CONFIG ===
savePath = "C:\Offers\Incoming\"
logPath = "C:\Users\PV\OneDrive\backend\logs\"
' =================

Set outlook = CreateObject("Outlook.Application")
Set namespace = outlook.GetNamespace("MAPI")
Set fso = CreateObject("Scripting.FileSystemObject")

today = Year(Now) & "-" & Right("0" & Month(Now),2) & "-" & Right("0" & Day(Now),2)
logFileName = logPath & "outlook_pdf_log_" & today & ".txt"

Set logStream = fso.OpenTextFile(logFileName, 8, True)
logStream.WriteLine "==== Hourly Run Start: " & Now & " ===="

' Access mailbox
Set mailbox = namespace.Folders("huetter@mchvertrieb.at")
Set folder = mailbox.Folders("Sicherheitssysteme")


Dim mail, attachment, fileName, newFilePath, counter

For Each mail In restrictedItems

    If mail.Class = 43 Then
        If mail.Categories <> "Processed" Then

            For Each attachment In mail.Attachments
                If LCase(Right(attachment.FileName, 4)) = ".pdf" Then

                    fileName = attachment.FileName
                    newFilePath = savePath & fileName
                    counter = 1

                    While fso.FileExists(newFilePath)
                        newFilePath = savePath & counter & "_" & fileName
                        counter = counter + 1
                    Wend

                    attachment.SaveAsFile newFilePath
                    logStream.WriteLine Now & " | Saved: " & newFilePath

                End If
            Next

            mail.Categories = "Processed"
            mail.Save
            logStream.WriteLine Now & " | Marked Processed: " & mail.Subject

        End If
    End If

Next

logStream.WriteLine "==== Hourly Run End ===="
logStream.Close