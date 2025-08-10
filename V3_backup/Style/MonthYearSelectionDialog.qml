import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

Rectangle {
    id: monthYearDialog
    width: 420
    height: 280
    radius: 12
    color: Style.background
    border.color: Style.border
    border.width: 1
    
    // Zentrieren im Parent
    anchors.centerIn: parent
    z: 1000
    
    property string filename: ""
    property string suggestedDate: ""
    
    signal monthYearSelected(string month, string year)
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
            text: "Funk-Rechnung Import"
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
        
        // Monat/Jahr Eingabe
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Text {
                text: "Bitte Monat und Jahr für diese Rechnung eingeben:"
                font.pixelSize: 14
                color: Style.text
                font.family: "Ubuntu"
                Layout.alignment: Qt.AlignHCenter
            }
            
            RowLayout {
                Layout.fillWidth: true
                spacing: 16
                
                // Monat ComboBox
                ComboBox {
                    id: monthComboBox
                    Layout.fillWidth: true
                    height: 50
                    model: [
                        "01 - Januar", "02 - Februar", "03 - März", "04 - April",
                        "05 - Mai", "06 - Juni", "07 - Juli", "08 - August",
                        "09 - September", "10 - Oktober", "11 - November", "12 - Dezember"
                    ]
                    
                    background: Rectangle {
                        color: parent.pressed ? Style.primary : (parent.hovered ? Style.accent : Style.primary)
                        radius: 8
                        border.color: Style.border
                        border.width: 1
                    }
                    
                    contentItem: Text {
                        text: parent.displayText
                        color: "white"
                        font.pixelSize: 14
                        font.family: "Ubuntu"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    Component.onCompleted: {
                        // Aktuellen Monat als Standard setzen
                        if (suggestedDate) {
                            let parts = suggestedDate.split("/")
                            if (parts.length === 2) {
                                let suggestedMonth = parseInt(parts[0])
                                if (suggestedMonth >= 1 && suggestedMonth <= 12) {
                                    currentIndex = suggestedMonth - 1
                                }
                            }
                        }
                    }
                }
                
                // Jahr SpinBox
                SpinBox {
                    id: yearSpinBox
                    Layout.fillWidth: true
                    height: 50
                    from: 2020
                    to: 2030
                    value: 2025
                    
                    background: Rectangle {
                        color: parent.pressed ? Style.primary : (parent.hovered ? Style.accent : Style.primary)
                        radius: 8
                        border.color: Style.border
                        border.width: 1
                    }
                    
                    contentItem: Text {
                        text: parent.value
                        color: "white"
                        font.pixelSize: 16
                        font.family: "Ubuntu"
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    Component.onCompleted: {
                        // Vorgeschlagenes Jahr als Standard setzen
                        if (suggestedDate) {
                            let parts = suggestedDate.split("/")
                            if (parts.length === 2) {
                                let suggestedYear = parseInt(parts[1])
                                if (suggestedYear >= 2020 && suggestedYear <= 2030) {
                                    value = suggestedYear
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Button {
                text: "Abbrechen"
                Layout.fillWidth: true
                height: 40
                
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
                    monthYearDialog.dialogClosed()
                }
            }
            
            Button {
                text: "Importieren"
                Layout.fillWidth: true
                height: 40
                
                background: Rectangle {
                    color: parent.pressed ? Style.primary : (parent.hovered ? Style.accent : Style.primary)
                    radius: 6
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 12
                    font.family: "Ubuntu"
                    font.bold: true
                }
                
                onClicked: {
                    let selectedMonth = (monthComboBox.currentIndex + 1).toString().padStart(2, '0')
                    let selectedYear = yearSpinBox.value.toString()
                    monthYearSelected(selectedMonth, selectedYear)
                    monthYearDialog.dialogClosed()
                }
            }
        }
    }
}
