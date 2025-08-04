import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

ColumnLayout {
    id: platformCard
    
    // Properties für die Card-Daten
    property var cardData: ({})
    property bool isVisible: true
    property string platformName: ""
    
    // Layout-Eigenschaften
    spacing: Math.max(12, parent.height * 0.01)
    Layout.alignment: Qt.AlignTop
    Layout.preferredWidth: Math.max(220, parent.width * 0.22)
    Layout.fillWidth: false
    visible: isVisible
    
    // Card-Titel
    Text { 
        text: platformName === "31300" ? "31300" : cardData.label || platformName
        font.pixelSize: Math.max(32, parent.width * 0.032)
        color: "#555555"
        font.bold: true
        font.family: ubuntuFont.name
    }
    
    // Card-Container
    Rectangle {
        Layout.preferredWidth: Math.max(240, parent.width * 0.24)
        Layout.preferredHeight: Math.max(240, parent.width * 0.24)
        radius: Style.radiusLarge
        border.width: 0
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#050505" }
            GradientStop { position: 0.8; color: "#050505" }
            GradientStop { position: 1.0; color: "#1a1a1a" }
        }
        
        ColumnLayout {
            anchors.fill: parent
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: Math.max(16, parent.width * 0.02)
            Layout.rightMargin: 16
            spacing: Math.max(12, parent.height * 0.01)
            
            // Zeile 1
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
                                 Text { 
                     anchors.right: parent.right
                     anchors.rightMargin: 16
                     anchors.verticalCenter: parent.verticalCenter
                     text: formatNumber(cardData.zeile1) + ' €'
                     font.pixelSize: Math.max(42, parent.width * 0.042)
                     color: "#808080"
                     font.family: ubuntuFont.name
                 }
            }
            
            // Zeile 2
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
                                 Text { 
                     anchors.right: parent.right
                     anchors.rightMargin: 16
                     anchors.verticalCenter: parent.verticalCenter
                     text: formatNumber(cardData.zeile2) + ' €'
                     font.pixelSize: Math.max(42, parent.width * 0.042)
                     color: "#808080"
                     font.family: ubuntuFont.name
                 }
            }
            
            // Zeile 3
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
                                 Text { 
                     anchors.right: parent.right
                     anchors.rightMargin: 16
                     anchors.verticalCenter: parent.verticalCenter
                     text: (abrechnungsBackend && abrechnungsBackend.deal === "P") ? formatNumber(cardData.zeile3) : formatNumber(cardData.zeile3) + ' €'
                     font.pixelSize: Math.max(42, parent.width * 0.042)
                     color: "#808080"
                     font.family: ubuntuFont.name
                 }
            }
        }
    }
    
    // Hilfsfunktion für Zahlenformatierung
    function formatNumber(value) {
        if (value === "-" || value === undefined || value === null) return "-"
        var num = parseFloat(value)
        if (isNaN(num)) return "-"
        return num.toFixed(2)
    }
} 