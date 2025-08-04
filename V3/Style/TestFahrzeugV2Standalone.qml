import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1920
    height: 1080
    title: "Fahrzeug V2 Standalone Test"
    color: "#0a0a0a"
    
    // Neue Fahrzeugseite V2 laden
    FahrzeugSeiteV2 {
        anchors.fill: parent
        goHome: function() {
            console.log("Home-Button geklickt - Beende Anwendung")
            Qt.quit()
        }
    }
    
    // Debug-Informationen
    Text {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 10
        text: "Fahrzeug V2 Standalone Test"
        color: "#ffffff"
        font.pixelSize: 14
        z: 1000
    }
} 