import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

Rectangle {
    id: platformDialog
    width: 420
    height: 220
    radius: 12
    color: Style.background
    border.color: Style.border
    border.width: 1
    
    // Zentrieren im Parent
    anchors.centerIn: parent
    z: 1000
    
    property string filename: ""
    property string platforms: ""
    property string selectedPlatform: ""
    
    signal platformSelected(string platform)
    signal dialogClosed()
    
    // Hintergrund-Overlay für Fokus
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        z: -1
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 24
        anchors.margins: 28
        
        // Header
        Text {
            text: "Taxi-Umsatz Import"
            font.pixelSize: 20
            color: Style.text
            font.family: "Ubuntu"
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }
        
        // Dateiname (vereinfacht)
        Text {
            text: filename.length > 35 ? filename.substring(0, 35) + "..." : filename
            font.pixelSize: 12
            color: Style.textMuted
            font.family: "Space Mono"
            Layout.alignment: Qt.AlignHCenter
        }
        
        // Plattform-Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 20
            
            Button {
                id: btn40100
                text: "40100"
                Layout.fillWidth: true
                height: 50
                
                background: Rectangle {
                    color: parent.pressed ? Style.primary : (btn40100.hovered ? Style.accent : Style.primary)
                    radius: 8
                    border.color: Style.border
                    border.width: 1
                }
                
                contentItem: ColumnLayout {
                    spacing: 2
                    
                    Text {
                        text: "40100"
                        color: "white"
                        font.pixelSize: 16
                        font.family: "Ubuntu"
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    Text {
                        text: "Hauptstelle"
                        color: "white"
                        font.pixelSize: 11
                        font.family: "Ubuntu"
                        opacity: 0.9
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
                
                onClicked: {
                    selectedPlatform = "40100"
                    platformSelected("40100")
                    platformDialog.dialogClosed()
                }
            }
            
            Button {
                id: btn31300
                text: "31300"
                Layout.fillWidth: true
                height: 50
                
                background: Rectangle {
                    color: parent.pressed ? Style.primary : (btn31300.hovered ? Style.accent : Style.primary)
                    radius: 8
                    border.color: Style.border
                    border.width: 1
                }
                
                contentItem: ColumnLayout {
                    spacing: 2
                    
                    Text {
                        text: "31300"
                        color: "white"
                        font.pixelSize: 16
                        font.family: "Ubuntu"
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    Text {
                        text: "Zweigstelle"
                        color: "white"
                        font.pixelSize: 11
                        font.family: "Ubuntu"
                        opacity: 0.9
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
                
                onClicked: {
                    selectedPlatform = "31300"
                    platformSelected("31300")
                    platformDialog.dialogClosed()
                }
            }
        }
        
        // Abbrechen-Button (kleiner und dezenter)
        Button {
            text: "Abbrechen"
            Layout.fillWidth: true
            height: 36
            
            background: Rectangle {
                color: parent.pressed ? Style.background : "transparent"
                border.color: Style.border
                border.width: 1
                radius: 6
            }
            
            contentItem: Text {
                text: parent.text
                color: Style.textMuted
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 12
                font.family: "Ubuntu"
            }
            
            onClicked: {
                platformDialog.dialogClosed()
            }
        }
    }
}
