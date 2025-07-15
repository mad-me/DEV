import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: importStatusOverlay
    anchors.fill: parent
    color: "transparent"
    visible: root.isImporting
    
    // Hintergrund-Overlay
    Rectangle {
        anchors.fill: parent
        color: "#80000000"  // Semi-transparent schwarz
    }
    
    // Haupt-Container
    Rectangle {
        width: 400
        height: 300
        anchors.centerIn: parent
        radius: 10
        color: "#ffffff"
        border.color: "#cccccc"
        border.width: 1
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15
            
            // Titel
            Text {
                text: "Import läuft..."
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            // Spinner/Loader
            BusyIndicator {
                id: spinner
                running: root.isImporting
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 50
                Layout.preferredHeight: 50
            }
            
            // Status-Text
            Text {
                id: statusText
                text: "Bereite Import vor..."
                font.pixelSize: 14
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            // Fortschrittsbalken
            ProgressBar {
                id: progressBar
                value: root.importProgress / 100
                Layout.fillWidth: true
                Layout.preferredHeight: 20
            }
            
            // Fortschritts-Text
            Text {
                text: `${root.importCurrentFile} von ${root.importTotalFiles} Dateien verarbeitet`
                font.pixelSize: 12
                color: "#666666"
                Layout.alignment: Qt.AlignHCenter
            }
            
            // Abbrechen-Button
            Button {
                text: "Abbrechen"
                Layout.alignment: Qt.AlignHCenter
                onClicked: {
                    // TODO: Import abbrechen implementieren
                    console.log("Import abbrechen")
                }
            }
        }
    }
    
    // Connections für Status-Updates
    Connections {
        target: datenBackend
        
        function onImportStatusChanged(status) {
            statusText.text = status
        }
        
        function onImportFinished(success, message) {
            if (success) {
                // Erfolgs-Meldung anzeigen
                successDialog.open()
            } else {
                // Fehler-Meldung anzeigen
                errorDialog.open()
            }
        }
    }
    
    // Erfolgs-Dialog
    Dialog {
        id: successDialog
        title: "Import erfolgreich"
        standardButtons: Dialog.Ok
        modal: true
        anchors.centerIn: parent
        
        Text {
            text: "Der Import wurde erfolgreich abgeschlossen!"
            font.pixelSize: 14
        }
        
        onAccepted: {
            importStatusOverlay.visible = false
        }
    }
    
    // Fehler-Dialog
    Dialog {
        id: errorDialog
        title: "Import-Fehler"
        standardButtons: Dialog.Ok
        modal: true
        anchors.centerIn: parent
        
        Text {
            text: "Beim Import ist ein Fehler aufgetreten. Überprüfen Sie die Logs für Details."
            font.pixelSize: 14
        }
        
        onAccepted: {
            importStatusOverlay.visible = false
        }
    }
} 