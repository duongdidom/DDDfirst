Attribute VB_Name = "NewMacros"
'Option Explicit

Sub savePDF()
' Purpose save current document in PDF without markup

Dim path As String, filename As String

path = ActiveDocument.path
filename = ActiveDocument.Name

    ActiveDocument.ExportAsFixedFormat OutputFileName:= _
    path & "\" & Mid(filename, 1, InStr(1, filename, ".") - 1) & ".pdf" _
    , ExportFormat:=wdExportFormatPDF, OpenAfterExport:=False, OptimizeFor:= _
    wdExportOptimizeForPrint, Range:=wdExportAllDocument, From:=1, To:=1, _
    Item:=wdExportDocumentContent, _
    IncludeDocProps:=True, KeepIRM:=True, _
    CreateBookmarks:=wdExportCreateNoBookmarks, DocStructureTags:=True, _
    BitmapMissingFonts:=True, UseISO19005_1:=False

ActiveDocument.Save
        
End Sub

Sub PicturesFitPageWidth()
' Purpose: Resize pic Macro, resizes an image


'''Sets the variables to loop through all shapes in the document, one for shapes and one for inline shapes.
    Shapes = ActiveDocument.Shapes.Count
    InLines = ActiveDocument.InlineShapes.Count


'''Calculate usable width of page
    With ActiveDocument.PageSetup
        WidthAvail = .PageWidth - .LeftMargin - .RightMargin
    End With


'''Loops through all shapes in the document.  Checks to see if they're too wide, and if they are, resizes them.
    For ShapeLoop = 1 To Shapes
        MsgBox Prompt:="Shape " & ShapeLoop & " width: " & ActiveDocument.Shapes(ShapeLoop).Width
        If ActiveDocument.Shapes(ShapeLoop).Width > WidthAvail Then
            ActiveDocument.Shapes(ShapeLoop).Width = WidthAvail
        End If
    Next ShapeLoop


'''Loops through all shapes in the document.  Checks to see if they're too wide, and if they are, resizes them.
    For InLineLoop = 1 To InLines
        MsgBox Prompt:="Inline " & InLineLoop & " width: " & ActiveDocument.InlineShapes(InLineLoop).Width
        If ActiveDocument.InlineShapes(InLineLoop).Width > WidthAvail Then
            ActiveDocument.InlineShapes(InLineLoop).Width = WidthAvail
        End If
    Next InLineLoop

End Sub
