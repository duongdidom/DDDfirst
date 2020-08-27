VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "ThisOutlookSession"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True

Option Explicit

Sub Download_EODStatement()
    ''' constant
    Dim FileNameFolder As String
    FileNameFolder = "\\ad.nzx.com\groups\market services\Clearing House\Risk Management\Daily Risk Task\EOD Derivative Statement\EOD statements\"   'Define the folder where you want to save attachments
    Const BPcount = 5
    
    '''Variables for the main functionality
    Dim NS As NameSpace
    Dim SubFolder As MAPIFolder
    Dim MsG As Outlook.MailItem
    Dim AtcHmt As attachment
    Dim ReceivedDate As Date, prevDay As Date
    Dim nStatementCount As Integer
    Dim strDownloadAtcHmt As String
    Dim bFound As Boolean
    '''Variables for unzipping
    Dim FSO As Object
    Dim ShellApp As Object
    Set FSO = CreateObject("Scripting.FileSystemObject")
    Set ShellApp = CreateObject("Shell.Application")
    Dim fileName As Variant

    '''Define the Outlook folder you want to scan
    Set NS = GetNamespace("MAPI")
    Set SubFolder = NS.Folders("G Suite - douglas.cao@nzx.com").Folders("risk@nzx").Folders("EOD Statement")    ' amend folder and subfolder here
    
    ''' define previous working day
    If Weekday(Date) = vbMonday Then
        prevDay = Date - 3
    Else
        prevDay = Date - 1
    End If
    
    ''' define boolean variable, if message is found or not. If the variable remain false, reduce 1 day from prevDay until found variable turn to true
    ''' this is to capture holiday period that is more than 1 day
    bFound = False
    
    ''' set starting value for statement count
    nStatementCount = 0
    
    ''' start looping all message in folder
SearchFolder:
    For Each MsG In SubFolder.Items
        ReceivedDate = DateValue(MsG.ReceivedTime)
        If ReceivedDate = prevDay Then
            ''' set boolean item to true
            bFound = True
            
            ''' add count to statement count variable
            nStatementCount = nStatementCount + 1
            
            ''' download attachment
            For Each AtcHmt In MsG.Attachments
                fileName = AtcHmt.fileName
                If InStrRev(fileName, "xls") <> 0 Then  ' check if statement is excel file
                    AtcHmt.SaveAsFile FileNameFolder & fileName
                    
                    strDownloadAtcHmt = strDownloadAtcHmt & nStatementCount & ". " & CStr(fileName) & vbNewLine
                End If
            Next AtcHmt
            
        End If
        
        ''' if found is true and count = constant value of bp count, get out of loop
        If bFound = True And nStatementCount = BPcount Then Exit For
    Next MsG
    
    ''' search folder again if found variable is fasle. I.e. the day before is a holiday date
    If bFound = False Then
        GoTo SearchFolder
    End If
    
    ''' print result: which file has been downloaded
    MsgBox strDownloadAtcHmt, vbOKOnly & vbInformation, nStatementCount & " Attachments downloaded this run:"
    
End Sub



Sub Toogle_rule()
' purpose: toggle on / off rule "Defer send message"



Dim olRules As Outlook.Rules
Dim olRule As Outlook.Rule
Dim intCount As Integer, userClick As Integer
Dim blnExecute As Boolean
Dim strStatus As String
 
    Set olRules = Application.Session.DefaultStore.GetRules
    Set olRule = olRules.Item("Defer send message")
    
    ''' Check current status of the rule
    If olRule.Enabled = True Then
        strStatus = "On"
    Else
        strStatus = "Off"
    End If
    
    ''' Ask user
    userClick = MsgBox("Deferring sending message is " & strStatus & vbNewLine & vbNewLine & "Click Yes to defer, No to send instantly", vbYesNo)
    If userClick = vbYes Then
        olRule.Enabled = True
    Else
        olRule.Enabled = False
    End If
    
'    ''' this is to toggle rule on/off ''''''' no longer need, better and more logical solution is above.
'    If olRule.Enabled = True Then
'        olRule.Enabled = False
'    Else
'        olRule.Enabled = True
'    End If
'    '''
    
    If blnExecute Then olRule.Execute ShowProgress:=True
       olRules.Save
  
    Set olRules = Nothing
    Set olRule = Nothing
    
    
End Sub
