import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

Rectangle {
    id: toast
    width: 350
    height: 60
    radius: Style.radiusNormal
    color: toastType === "success" ? Style.success : 
           toastType === "error" ? Style.error :
           toastType === "warning" ? Style.warning :
           toastType === "info" ? Style.accent : Style.surface
    border.color: toastType === "success" ? "#22c55e" :
                  toastType === "error" ? "#ef4444" :
                  toastType === "warning" ? "#f59e0b" :
                  toastType === "info" ? "#00c2ff" : Style.border
    border.width: 1
    
    // Properties
    property string message: ""
    property string toastType: "info" // success, error, warning, info
    property int duration: 3000 // 3 Sekunden
    property bool isVisible: false
    
    // Position
    x: parent.width - width - 20
    y: isVisible ? 20 : -height
    z: 1000
    
    // Animation
    Behavior on y {
        NumberAnimation { 
            duration: Style.animationFast
            easing.type: Easing.OutCubic
        }
    }
    
    // Auto-hide Timer
    Timer {
        id: hideTimer
        interval: duration
        onTriggered: {
            toast.isVisible = false
        }
    }
    
    // Icon basierend auf Typ
    property string iconSource: toastType === "success" ? "assets/icons/check_white.svg" :
                               toastType === "error" ? "assets/icons/close_white.svg" :
                               toastType === "warning" ? "assets/icons/warning_white.svg" :
                               "assets/icons/info_white.svg"
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12
        
        // Icon
        Image {
            source: iconSource
            width: 24
            height: 24
            fillMode: Image.PreserveAspectFit
        }
        
        // Message
        Text {
            text: message
            color: Style.text
            font.pixelSize: Style.fontSizeNormal
            font.family: "Ubuntu"
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            elide: Text.ElideRight
        }
        
        // Close Button
        Rectangle {
            width: 24
            height: 24
            radius: 12
            color: "transparent"
            border.width: 0
            
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    hideTimer.stop()
                    toast.isVisible = false
                }
                
                Image {
                    anchors.centerIn: parent
                    source: parent.containsMouse ? "assets/icons/close_white.svg" : "assets/icons/close_gray.svg"
                    width: 16
                    height: 16
                    fillMode: Image.PreserveAspectFit
                }
            }
        }
    }
    
    // Funktionen
    function show(msg, type = "info", dur = 3000) {
        message = msg
        toastType = type
        duration = dur
        isVisible = true
        hideTimer.start()
    }
    
    function hide() {
        isVisible = false
        hideTimer.stop()
    }
} 