import QtQuick 2.15
import QtQuick.Controls 2.15
import Style 1.0

Rectangle {
    id: loadingSpinner
    width: 80
    height: 80
    radius: Style.radiusLarge
    color: Style.surface
    border.color: Style.border
    border.width: 1
    
    // Properties
    property bool isVisible: false
    property string message: "Lädt..."
    property int spinnerSize: 40
    property color spinnerColor: Style.primary
    
    // Position
    anchors.centerIn: parent
    z: 2000
    
    // Animation
    opacity: isVisible ? 1.0 : 0.0
    scale: isVisible ? 1.0 : 0.8
    
    Behavior on opacity {
        NumberAnimation { 
            duration: Style.animationFast
            easing.type: Easing.OutCubic
        }
    }
    
    Behavior on scale {
        NumberAnimation { 
            duration: Style.animationFast
            easing.type: Easing.OutBack
        }
    }
    
    // Spinner Animation
    Rectangle {
        id: spinner
        width: spinnerSize
        height: spinnerSize
        radius: spinnerSize / 2
        color: "transparent"
        border.color: spinnerColor
        border.width: 3
        anchors.centerIn: parent
        
        // Rotation Animation
        RotationAnimation {
            target: spinner
            from: 0
            to: 360
            duration: 1000
            loops: Animation.Infinite
            running: loadingSpinner.isVisible
        }
        
        // Gradient für besseren Effekt
        gradient: Gradient {
            GradientStop { position: 0.0; color: "transparent" }
            GradientStop { position: 0.5; color: spinnerColor }
            GradientStop { position: 1.0; color: "transparent" }
        }
    }
    
    // Message
    Text {
        text: message
        color: Style.text
        font.pixelSize: Style.fontSizeNormal
        font.family: "Ubuntu"
        anchors {
            top: spinner.bottom
            horizontalCenter: parent.horizontalCenter
            topMargin: 12
        }
    }
    
    // Funktionen
    function show(msg = "Lädt...") {
        message = msg
        isVisible = true
    }
    
    function hide() {
        isVisible = false
    }
    
    function setMessage(msg) {
        message = msg
    }
} 