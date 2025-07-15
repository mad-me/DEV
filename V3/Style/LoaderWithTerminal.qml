import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: loaderRoot
    width: 900
    height: 600
    color: "#000000"
    radius: 12
    border.color: "#444"
    border.width: 2

    FontLoader { id: ubuntuFont; source: "assets/fonts/Ubuntu-Regular.ttf" }
    FontLoader { id: spaceMonoFont; source: "assets/fonts/SpaceMono-Regular.ttf" }

    property bool showTerminal: true
    property string statusText: "Import läuft..."
    property int animIndex: 0
    property string terminalContent: "[Terminal bereit]\n"
    property bool processFinished: false

    // Loader-Animation und Status
    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 30

        Text {
            text: loaderRoot.statusText
            font.pixelSize: 22
            font.family: ubuntuFont.name
            color: "#f7931e"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }

        // Animierte Blöcke
        Row {
            id: blockRow
            spacing: 8
            anchors.horizontalCenter: parent.horizontalCenter
            Repeater {
                model: 16
                Rectangle {
                    width: 22
                    height: 20
                    radius: 4
                    color: index === loaderRoot.animIndex ? "#f7931e" : "#1F2732"
                    Behavior on color { ColorAnimation { duration: 120 } }
                }
            }
            Timer {
                interval: 60; running: true; repeat: true
                onTriggered: {
                    loaderRoot.animIndex = (loaderRoot.animIndex + 1) % 16
                }
            }
        }

        // OK-Button
        Rectangle {
            width: 80
            height: 40
            color: "transparent"
            visible: loaderRoot.processFinished
            
            Text {
                text: "OK"
                anchors.centerIn: parent
                font.pixelSize: 18
                font.family: ubuntuFont.name
                font.bold: true
                color: "#f7931e"
            }
            
            MouseArea {
                anchors.fill: parent
                onClicked: loaderRoot.visible = false
                cursorShape: Qt.PointingHandCursor
            }
        }
    }

    // Movable Terminal-Panel
    Rectangle {
        id: terminalPanel
        visible: loaderRoot.showTerminal
        width: 600
        height: 500
        x: terminalX
        y: terminalY
        property real terminalX: parent.width - width - 20
        property real terminalY: (parent.height - height) / 2
        color: "#181818"
        radius: 8
        border.color: "#444"
        border.width: 1

        // Drag-Logik
        MouseArea {
            id: dragArea
            anchors.fill: parent
            drag.target: terminalPanel
            drag.axis: Drag.XAndYAxis
            cursorShape: Qt.OpenHandCursor
        }

        Column {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 8

            // Schließen-Button
            Rectangle {
                width: 30
                height: 30
                color: "transparent"
                anchors.right: parent.right
                
                Text {
                    text: "✕"
                    anchors.centerIn: parent
                    font.pixelSize: 16
                    font.family: ubuntuFont.name
                    font.bold: true
                    color: "#f7931e"
                }
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: loaderRoot.showTerminal = false
                    cursorShape: Qt.PointingHandCursor
                }
            }

            // Terminal-Ausgabe
            TextArea {
                id: terminalText
                text: loaderRoot.terminalContent
                readOnly: true
                font.family: spaceMonoFont.name
                font.pixelSize: 14
                color: "#f7931e"
                background: Rectangle { color: "#181818" }
                wrapMode: TextArea.Wrap
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: terminalInput.top
                
                // Automatisches Scrollen nach unten
                onTextChanged: {
                    cursorPosition = text.length
                }
            }

            // Terminal-Eingabe
            Rectangle {
                id: terminalInput
                height: 30
                color: "#222"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                
                TextInput {
                    id: inputText
                    anchors.fill: parent
                    anchors.margins: 8
                    font.family: spaceMonoFont.name
                    font.pixelSize: 14
                    color: "#f7931e"
                    text: ""
                    
                    onAccepted: {
                        if (text === "clear") {
                            loaderRoot.terminalContent = "[Terminal bereit]\n"
                        } else {
                            loaderRoot.terminalContent += "> " + text + "\n"
                        }
                        text = ""
                    }
                }
                
                Text {
                    text: "Befehl eingeben..."
                    anchors.fill: parent
                    anchors.margins: 8
                    font.family: spaceMonoFont.name
                    font.pixelSize: 14
                    color: "#666"
                    visible: inputText.text === ""
                }
            }
        }
    }
} 