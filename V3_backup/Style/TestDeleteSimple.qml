import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: window
    width: 800
    height: 600
    visible: true
    title: "Delete Test"

    Rectangle {
        anchors.fill: parent
        color: "#2b2b2b"

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 20

            Text {
                text: "Delete Test"
                font.pixelSize: 24
                color: "white"
                Layout.alignment: Qt.AlignHCenter
            }

            // Test-Button für direkte Löschung
            Button {
                text: "Teste deleteEmployee (ID: 99999)"
                Layout.alignment: Qt.AlignHCenter
                onClicked: {
                    console.log("Teste deleteEmployee...")
                    if (mitarbeiterBackendV2) {
                        try {
                            mitarbeiterBackendV2.deleteEmployee(99999)
                            console.log("deleteEmployee aufgerufen")
                        } catch (error) {
                            console.error("Fehler bei deleteEmployee:", error)
                        }
                    } else {
                        console.log("mitarbeiterBackendV2 nicht verfügbar")
                    }
                }
            }

            // Test-Button für Bestätigungsdialog
            Button {
                text: "Teste deleteEmployeeWithConfirmation (ID: 99999)"
                Layout.alignment: Qt.AlignHCenter
                onClicked: {
                    console.log("Teste deleteEmployeeWithConfirmation...")
                    if (mitarbeiterBackendV2) {
                        try {
                            mitarbeiterBackendV2.deleteEmployeeWithConfirmation(99999)
                            console.log("deleteEmployeeWithConfirmation aufgerufen")
                        } catch (error) {
                            console.error("Fehler bei deleteEmployeeWithConfirmation:", error)
                        }
                    } else {
                        console.log("mitarbeiterBackendV2 nicht verfügbar")
                    }
                }
            }

            // Status-Anzeige
            Text {
                id: statusText
                text: "Status: Bereit"
                color: "white"
                Layout.alignment: Qt.AlignHCenter
            }

            // Backend-Status
            Text {
                id: backendStatus
                text: "Backend: " + (mitarbeiterBackendV2 ? "Verfügbar" : "Nicht verfügbar")
                color: mitarbeiterBackendV2 ? "green" : "red"
                Layout.alignment: Qt.AlignHCenter
            }
        }

        // Signal-Handler
        Connections {
            target: mitarbeiterBackendV2
            
            function onStatusMessageChanged() {
                console.log("StatusMessageChanged Signal empfangen")
                statusText.text = "Status: " + mitarbeiterBackendV2.statusMessage
            }
            
            function onErrorOccurred(errorMessage) {
                console.log("ErrorOccurred Signal empfangen:", errorMessage)
                statusText.text = "Fehler: " + errorMessage
            }
            
            function onDeleteConfirmationRequested(employeeData) {
                console.log("DeleteConfirmationRequested Signal empfangen:", employeeData)
                statusText.text = "Delete-Dialog angefordert für: " + employeeData.first_name + " " + employeeData.last_name
            }
        }
    }
} 