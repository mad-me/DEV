import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: validationErrorDialog
    anchors.fill: parent
    color: "#000000"
    opacity: 0.9
    visible: false
    z: 4000 // Höchster Z-Index für Validierungsfehler
    
    // Eigenschaften für Validierungsfehler
    property var validationErrors: []
    property string operation: ""
    property bool isVisible: false
    
    // Signal für Dialog-Aktionen
    signal dialogClosed()
    signal retryRequested()
    signal editRequested()
    
    // Animation für das Erscheinen
    Behavior on opacity {
        NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
    }
    
    // ESC-Taste zum Schließen
    Keys.onEscapePressed: closeDialog()
    
    // Hauptcontainer
    Rectangle {
        width: Math.min(parent.width * 0.8, 600)
        height: Math.min(parent.height * 0.8, 500)
        anchors.centerIn: parent
        radius: Style.radiusNormal
        color: "#1a1a1a"
        border.color: "#ff4444"
        border.width: 2
        
        // Schatten-Effekt
        layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 0
            verticalOffset: 4
            radius: 8.0
            samples: 17
            color: "#80000000"
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 20
            
            // Header
            Rectangle {
                Layout.fillWidth: true
                height: 60
                color: "transparent"
                
                RowLayout {
                    anchors.fill: parent
                    spacing: 16
                    
                    // Warnsymbol
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "#ff4444"
                        
                        Text {
                            anchors.centerIn: parent
                            text: "⚠️"
                            font.pixelSize: 24
                            color: "white"
                        }
                    }
                    
                    // Titel
                    Text {
                        text: "Validierungsfehler"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        font.bold: true
                        color: "#ff4444"
                        Layout.fillWidth: true
                    }
                    
                    // Schließen-Button
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 20
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: closeDialog()
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                width: parent.containsMouse ? 24 : 20
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                }
            }
            
            // Operation-Info
            Rectangle {
                Layout.fillWidth: true
                height: 40
                color: "#2a2a2a"
                radius: Style.radiusSmall
                
                Text {
                    anchors.centerIn: parent
                    text: operation ? `Operation: ${operation}` : "Validierungsfehler aufgetreten"
                    font.family: ubuntuFont.name
                    font.pixelSize: 14
                    color: "#cccccc"
                }
            }
            
            // Fehlerliste
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#2a2a2a"
                radius: Style.radiusSmall
                
                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 16
                    
                    ColumnLayout {
                        width: parent.width
                        spacing: 12
                        
                        // Überschrift
                        Text {
                            text: "Folgende Fehler wurden gefunden:"
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            font.bold: true
                            color: "#ff4444"
                            Layout.fillWidth: true
                        }
                        
                        // Fehlerliste
                        Repeater {
                            model: validationErrors
                            
                            Rectangle {
                                Layout.fillWidth: true
                                height: errorText.height + 16
                                color: "#3a3a3a"
                                radius: Style.radiusSmall
                                border.color: "#ff6666"
                                border.width: 1
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 12
                                    
                                    // Fehler-Symbol
                                    Rectangle {
                                        width: 20
                                        height: 20
                                        radius: 10
                                        color: "#ff4444"
                                        
                                        Text {
                                            anchors.centerIn: parent
                                            text: "✗"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: "white"
                                        }
                                    }
                                    
                                    // Fehlermeldung
                                    Text {
                                        id: errorText
                                        text: modelData
                                        font.family: ubuntuFont.name
                                        font.pixelSize: 14
                                        color: "#ffffff"
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }
                        
                        // Platzhalter wenn keine Fehler
                        Text {
                            text: "Keine spezifischen Fehler verfügbar"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "#888888"
                            Layout.fillWidth: true
                            visible: validationErrors.length === 0
                        }
                    }
                }
            }
            
            // Aktions-Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 16
                
                Item { Layout.fillWidth: true }
                
                // Abbrechen-Button
                Rectangle {
                    width: 120
                    height: 40
                    radius: Style.radiusSmall
                    color: "transparent"
                    border.color: "#666666"
                    border.width: 1
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: closeDialog()
                        
                        Text {
                            anchors.centerIn: parent
                            text: "Abbrechen"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: parent.containsMouse ? "#cccccc" : "#888888"
                        }
                        
                        Behavior on color {
                            ColorAnimation { duration: 150 }
                        }
                    }
                }
                
                // Bearbeiten-Button
                Rectangle {
                    width: 120
                    height: 40
                    radius: Style.radiusSmall
                    color: parent.containsMouse ? "#ff6666" : "#ff4444"
                    visible: validationErrors.length > 0
                    
                    MouseArea {
                        id: editMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            closeDialog()
                            editRequested()
                        }
                    }
                    
                    Text {
                        anchors.centerIn: parent
                        text: "Bearbeiten"
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        font.bold: true
                        color: "white"
                    }
                    
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
                
                // Wiederholen-Button
                Rectangle {
                    width: 120
                    height: 40
                    radius: Style.radiusSmall
                    color: parent.containsMouse ? "#ff8c00" : "#ff6600"
                    
                    MouseArea {
                        id: retryMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            closeDialog()
                            retryRequested()
                        }
                    }
                    
                    Text {
                        anchors.centerIn: parent
                        text: "Wiederholen"
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        font.bold: true
                        color: "white"
                    }
                    
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }
        }
    }
    
    // Font Loader
    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
    }
    
    // Funktionen
    function showDialog(errors, operationName) {
        validationErrors = errors || []
        operation = operationName || ""
        visible = true
        isVisible = true
        focus = true
    }
    
    function closeDialog() {
        visible = false
        isVisible = false
        focus = false
        dialogClosed()
    }
    
    function hideDialog() {
        closeDialog()
    }
} 