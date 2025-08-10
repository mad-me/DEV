import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#0a0a0a"
    
    // Test-Titel
    Text {
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 20
        text: "TEST: Neue Mitarbeiterseite V2"
        font.pixelSize: 24
        color: "#ff8c00"
        font.bold: true
    }
    
    // Zurück-Button
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.margins: 20
        width: 100
        height: 40
        color: "#333333"
        radius: 8
        
        Text {
            anchors.centerIn: parent
            text: "← Zurück"
            color: "white"
            font.pixelSize: 16
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: {
                // Hier können Sie später zur Hauptanwendung zurückkehren
                console.log("Zurück zur Hauptanwendung")
            }
        }
    }
    
    // Neue Mitarbeiterseite V2 einbetten
    MitarbeiterSeiteV2 {
        anchors.fill: parent
        anchors.margins: 20
        anchors.topMargin: 80
    }
} 