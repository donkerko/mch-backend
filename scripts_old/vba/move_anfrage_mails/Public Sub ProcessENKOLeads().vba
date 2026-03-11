Public Sub ProcessENKOLeads()

    Dim ns As Outlook.NameSpace
    Dim rootFolder As Outlook.MAPIFolder
    Dim inbox As Outlook.MAPIFolder
    Dim targetFolder As Outlook.MAPIFolder
    Dim mail As Object
    
    Set ns = Application.GetNamespace("MAPI")
    Set rootFolder = ns.Folders("huetter@enko.at")
    Set inbox = rootFolder.Folders("Posteingang")
    Set targetFolder = inbox.Folders("in Liste eingetragen")
    
    Dim i As Long
    
    For i = inbox.Items.Count To 1 Step -1
    
        Set mail = inbox.Items(i)
        
        If TypeName(mail) = "MailItem" Then
        
            ' ================= SENDER FILTER =================
            Dim smtp As String
            smtp = LCase(GetSMTPAddress(mail))
            
            If (smtp <> "anfrage@enko.at") And (smtp <> "mayrhofer@enko.at") And (smtp <> "office@enko.at") Then
                GoTo NextMail
            End If
            ' ================================================
            
            Dim body As String
            body = LCase(mail.body)
            'Debug.Print "----- BODY START -----"
            'Debug.Print body
            'Debug.Print "----- BODY END -----"

            Dim receivedDate As String
            receivedDate = Format(mail.ReceivedTime, "yymmdd")
            
            Dim success As Boolean
            success = False
            
            ' ======================================================
            ' ===================== PVALARM ========================
            ' ======================================================
            
            If InStr(body, "anfragealarm") > 0 Then
            
                Dim lastNamePVALARM As String
                lastNamePVALARM = CleanFileName(GetLastNamePVALARM(mail.body))
                
                If lastNamePVALARM = "" Then lastNamePVALARM = "Unbekannt"
                
                Dim saveFolder3 As String
                saveFolder3 = "C:\Users\PV\OneDrive\ENKO GmbH\Anfragen\PVALARM\"
                
                CreateFolderIfNotExists saveFolder3
                
                Dim savePath3 As String
                savePath3 = saveFolder3 & receivedDate & "_" & lastNamePVALARM & ".msg"
                savePath3 = GetUniqueFileName(savePath3)
                
                mail.SaveAs savePath3, olMSG
                success = True
                
            End If
            
            ' ======================================================
            ' ==================== VOLTALUX ========================
            ' ======================================================
            
            If mail.Attachments.Count > 0 Then
            
                Dim att As Attachment
                Dim hasPDF As Boolean
                hasPDF = False
                
                For Each att In mail.Attachments
                    If LCase(Right(att.FileName, 4)) = ".pdf" Then
                        hasPDF = True
                    End If
                Next att
                
                If hasPDF = True Then
                
                    Dim lastName As String
                    lastName = CleanFileName(GetLastNameVoltalux(mail.body))
                    
                    If lastName = "" Then lastName = "Unbekannt"
                    
                    Dim saveFolder As String
                    saveFolder = "C:\Users\PV\OneDrive\ENKO GmbH\Anfragen\voltalux\"
                    
                    CreateFolderIfNotExists saveFolder
                    
                    For Each att In mail.Attachments
                        If LCase(Right(att.FileName, 4)) = ".pdf" Then
                        
                            Dim savePath As String
                            savePath = saveFolder & receivedDate & "_" & lastName & ".pdf"
                            savePath = GetUniqueFileName(savePath)
                            
                            att.SaveAsFile savePath
                            success = True
                            
                        End If
                    Next att
                    
                End If
                
            End If
            
            
            ' ======================================================
            ' ============== PHOTOVOLTAIKANLAGE ====================
            ' ======================================================
            
            If InStr(body, "photovoltaikanlage") > 0 Then
            
                Dim lastNamePV As String
                lastNamePV = CleanFileName(GetLastNamePVAT(mail.body))
                
                If lastNamePV = "" Then lastNamePV = "Unbekannt"
                
                Dim saveFolder2 As String
                saveFolder2 = "C:\Users\PV\OneDrive\ENKO GmbH\Anfragen\photovoltaikAT\"
                
                CreateFolderIfNotExists saveFolder2
                
                Dim savePath2 As String
                savePath2 = saveFolder2 & receivedDate & "_" & lastNamePV & ".msg"
                savePath2 = GetUniqueFileName(savePath2)
                
                mail.SaveAs savePath2, olMSG
                success = True
                
            End If
            
            
            ' ======================================================
            ' ==================== VERSCHIEBEN =====================
            ' ======================================================
            
            If success = True Then
                mail.Move targetFolder
            End If
            
        End If
        
NextMail:
    
    Next i
    
    MsgBox "Verarbeitung abgeschlossen."
    
End Sub


' ===================== SMTP RESOLVER =====================
Function GetSMTPAddress(mail As Outlook.MailItem) As String

    Dim sender As Outlook.AddressEntry
    Dim exchUser As Outlook.ExchangeUser
    
    On Error Resume Next
    
    Set sender = mail.sender
    
    If sender Is Nothing Then
        GetSMTPAddress = ""
        Exit Function
    End If
    
    If sender.Type = "EX" Then
        Set exchUser = sender.GetExchangeUser
        If Not exchUser Is Nothing Then
            GetSMTPAddress = exchUser.PrimarySmtpAddress
        Else
            GetSMTPAddress = ""
        End If
    Else
        GetSMTPAddress = mail.SenderEmailAddress
    End If
    
End Function


' ===================== Nachname Voltalux =====================
Function GetLastNameVoltalux(body As String) As String

    Dim regEx As Object
    Set regEx = CreateObject("VBScript.RegExp")
    
    regEx.Pattern = "Nachname:\s*(.+)"
    regEx.IgnoreCase = True
    
    If regEx.Test(body) Then
        GetLastNameVoltalux = Trim(regEx.Execute(body)(0).SubMatches(0))
    Else
        GetLastNameVoltalux = ""
    End If
    
End Function


' ===================== Nachname PVAT =====================
Function GetLastNamePVAT(body As String) As String

    Dim regEx As Object
    Set regEx = CreateObject("VBScript.RegExp")
    
    regEx.Pattern = "Ihr Name\s+([A-Za-zÄÖÜäöüß\-]+)\s+([A-Za-zÄÖÜäöüß\-]+)"
    regEx.IgnoreCase = True
    
    If regEx.Test(body) Then
        GetLastNamePVAT = regEx.Execute(body)(0).SubMatches(1)
    Else
        GetLastNamePVAT = ""
    End If
    
End Function

' ===================== Nachname PVALARM =====================
Function GetLastNamePVALARM(body As String) As String

    Dim regEx As Object
    Set regEx = CreateObject("VBScript.RegExp")
    
    regEx.Pattern = "Name:\s+([A-Za-zÄÖÜäöüß\-]+)\s+([A-Za-zÄÖÜäöüß\-]+)"
    regEx.IgnoreCase = True
    
    If regEx.Test(body) Then
        GetLastNamePVALARM = regEx.Execute(body)(0).SubMatches(1)
    Else
        GetLastNamePVALARM = ""
    End If
    
End Function


' ===================== Dateiname bereinigen =====================
Function CleanFileName(str As String) As String

    str = Replace(str, "ä", "ae")
    str = Replace(str, "ö", "oe")
    str = Replace(str, "ü", "ue")
    str = Replace(str, "Ä", "Ae")
    str = Replace(str, "Ö", "Oe")
    str = Replace(str, "Ü", "Ue")
    str = Replace(str, "ß", "ss")
    
    Dim invalidChars As Variant
    invalidChars = Array("\", "/", ":", "*", "?", """", "<", ">", "|")
    
    Dim i As Integer
    For i = 0 To UBound(invalidChars)
        str = Replace(str, invalidChars(i), "")
    Next i
    
    CleanFileName = Trim(str)
    
End Function


' ===================== Ordner erstellen =====================
Sub CreateFolderIfNotExists(path As String)

    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If Not fso.FolderExists(path) Then
        fso.CreateFolder path
    End If
    
End Sub


' ===================== Duplikat-Schutz =====================
Function GetUniqueFileName(path As String) As String

    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If Not fso.FileExists(path) Then
        GetUniqueFileName = path
        Exit Function
    End If
    
    Dim base As String
    Dim ext As String
    Dim counter As Integer
    
    ext = Mid(path, InStrRev(path, "."))
    base = Left(path, InStrRev(path, ".") - 1)
    
    counter = 1
    
    Do While fso.FileExists(base & "_" & counter & ext)
        counter = counter + 1
    Loop
    
    GetUniqueFileName = base & "_" & counter & ext
    
End Function

