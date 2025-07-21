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

    FontLoader { id: ubuntuFont; source: "Style/assets/fonts/Ubuntu-Regular.ttf" }
    FontLoader { id: spaceMonoFont; source: "Style/assets/fonts/SpaceMono-Regular.ttf" }

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
            anchors.horizontalCenter: parent.horizontalCenter
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

        Button {
            text: "OK"
            font.pixelSize: 18
            font.family: ubuntuFont.name
            font.bold: true
            background: Rectangle { color: "transparent" }
            onClicked: loaderRoot.visible = false
            visible: loaderRoot.processFinished
            contentItem: Text {
                text: parent.text
                color: "#f7931e"
                font.pixelSize: 18
                font.family: ubuntuFont.name
                font.bold: true
            }
        }
    }

    // Movable Terminal-Panel
    Rectangle {
        id: terminalPanel
        visible: loaderRoot.showTerminal
        width: 400
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
            Button {
                text: "✕"
                anchors.right: parent.right
                onClicked: loaderRoot.showTerminal = false
                background: Rectangle { color: "transparent" }
                font.pixelSize: 16
                font.family: ubuntuFont.name
                font.bold: true
                contentItem: Text {
                    text: parent.text
                    color: "#f7931e"
                    font.pixelSize: 16
                    font.family: ubuntuFont.name
                    font.bold: true
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
            }

            // Terminal-Eingabe
            TextField {
                id: terminalInput
                placeholderText: "Befehl eingeben..."
                font.family: spaceMonoFont.name
                font.pixelSize: 14
                color: "#f7931e"
                background: Rectangle { color: "#222" }
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                onAccepted: {
                    loaderRoot.terminalContent += "> " + text + "\n"
                    if (text === "clear") {
                        loaderRoot.terminalContent = "[Terminal bereit]\n"
                    }
                    text = ""
                }
            }
        }
    }
} 