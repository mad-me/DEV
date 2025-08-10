import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

Rectangle {
    id: confirmationDialog
    anchors.fill: parent
    color: "#80000000" // Semi-transparent background
    z: 3000
    
    // Properties
    property bool isVisible: false
    property string title: "Bestätigung"
    property string message: "Sind Sie sicher?"
    property string confirmText: "Bestätigen"
    property string cancelText: "Abbrechen"
    property string dialogType: "info" // info, warning, error, success
    property var onConfirm: function() {}
    property var onCancel: function() {}
    
    // Signals
    signal confirmed()
    signal cancelled()
    
    // Animation
    opacity: isVisible ? 1.0 : 0.0
    visible: isVisible
    
    Behavior on opacity {
        NumberAnimation { 
            duration: Style.animationFast
            easing.type: Easing.OutCubic
        }
    }
    
    // Icon basierend auf Typ
    property string iconSource: dialogType === "success" ? "assets/icons/check_orange.svg" :
                               dialogType === "error" ? "assets/icons/close_red.svg" :
                               dialogType === "warning" ? "assets/icons/warning_orange.svg" :
                               "assets/icons/info_orange.svg"
    
    // Dialog Container
    Rectangle {
        id: dialogContainer
        width: 400
        height: 200
        radius: Style.radiusLarge
        color: Style.surface
        border.color: Style.border
        border.width: 1
        anchors.centerIn: parent
        
        // Shadow Effect
        layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 0
            verticalOffset: 4
            radius: 8.0
            samples: 17
            color: "#40000000"
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16
            
            // Header mit Icon und Titel
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                
                // Icon
                Image {
                    source: iconSource
                    width: 32
                    height: 32
                    fillMode: Image.PreserveAspectFit
                }
                
                // Title
                Text {
                    text: title
                    color: Style.text
                    font.pixelSize: Style.fontSizeTitle
                    font.family: "Ubuntu"
                    font.bold: true
                    Layout.fillWidth: true
                }
                
                // Close Button
                Rectangle {
                    width: 32
                    height: 32
                    radius: 16
                    color: "transparent"
                    border.width: 0
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            confirmationDialog.cancel()
                        }
                        
                        Image {
                            anchors.centerIn: parent
                            source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                            width: 20
                            height: 20
                            fillMode: Image.PreserveAspectFit
                        }
                    }
                }
            }
            
            // Message
            Text {
                text: message
                color: Style.textMuted
                font.pixelSize: Style.fontSizeNormal
                font.family: "Ubuntu"
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }
            
            // Spacer
            Item {
                Layout.fillHeight: true
            }
            
            // Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                
                // Spacer
                Item {
                    Layout.fillWidth: true
                }
                
                // Cancel Button
                Rectangle {
                    width: 100
                    height: 40
                    radius: Style.radiusNormal
                    color: "transparent"
                    border.color: Style.border
                    border.width: 1
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            confirmationDialog.cancel()
                        }
                        
                        Rectangle {
                            anchors.fill: parent
                            color: parent.containsMouse ? Style.buttonHover : "transparent"
                            radius: Style.radiusNormal
                        }
                        
                        Text {
                            text: cancelText
                            color: Style.text
                            font.pixelSize: Style.fontSizeNormal
                            font.family: "Ubuntu"
                            anchors.centerIn: parent
                        }
                    }
                }
                
                // Confirm Button
                Rectangle {
                    width: 100
                    height: 40
                    radius: Style.radiusNormal
                    color: dialogType === "error" ? Style.error :
                           dialogType === "warning" ? Style.warning :
                           dialogType === "success" ? Style.success :
                           Style.primary
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            confirmationDialog.confirm()
                        }
                        
                        Rectangle {
                            anchors.fill: parent
                            color: parent.containsMouse ? Qt.darker(parent.color, 1.2) : "transparent"
                            radius: Style.radiusNormal
                        }
                        
                        Text {
                            text: confirmText
                            color: Style.text
                            font.pixelSize: Style.fontSizeNormal
                            font.family: "Ubuntu"
                            font.bold: true
                            anchors.centerIn: parent
                        }
                    }
                }
            }
        }
    }
    
    // Background Click to Close
    MouseArea {
        anchors.fill: parent
        onClicked: {
            confirmationDialog.cancel()
        }
    }
    
    // Funktionen
    function show(title, message, confirmText = "Bestätigen", cancelText = "Abbrechen", type = "info", onConfirmFunc, onCancelFunc) {
        confirmationDialog.title = title
        confirmationDialog.message = message
        confirmationDialog.confirmText = confirmText
        confirmationDialog.cancelText = cancelText
        confirmationDialog.dialogType = type
        confirmationDialog.onConfirm = onConfirmFunc || function() {}
        confirmationDialog.onCancel = onCancelFunc || function() {}
        confirmationDialog.isVisible = true
    }
    
    function hide() {
        confirmationDialog.isVisible = false
    }
    
    function confirm() {
        onConfirm()
        confirmed()
        hide()
    }
    
    function cancel() {
        onCancel()
        cancelled()
        hide()
    }
} 