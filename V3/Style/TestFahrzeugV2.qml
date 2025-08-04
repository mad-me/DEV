import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1920
    height: 1080
    title: "Fahrzeug V2 Test"
    color: "#0a0a0a"
    
    // Neue Fahrzeugseite V2 laden
    FahrzeugSeiteV2 {
        anchors.fill: parent
        goHome: function() {
            console.log("Home-Button geklickt")
            Qt.quit()
        }
    }
} 