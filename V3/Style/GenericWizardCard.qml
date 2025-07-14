import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: wizardCard
    width: 500
    height: 350
    radius: 24
    color: "#000"
    border.color: "#f79009"
    border.width: 2
    z: 100
    property int currentStep: 0
    property var fahrerList: []
    property var fahrzeugList: []
    property var kwList: []
    property string selectedFahrer: ""
    property string selectedFahrzeug: ""
    property string selectedKW: ""
    signal wizardFertig(string fahrer, string fahrzeug, string kw)

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 32
        spacing: 24
        // Eingabezeile absolut zentriert
        Item {
            Layout.alignment: Qt.AlignCenter
            width: parent.width
            height: 80
            RowLayout {
                id: wizardRow
                width: parent.width
                height: 80
                spacing: 0
                // Linker Pfeil (nur wenn nicht erste Seite)
                Button {
                    text: "<"
                    visible: currentStep > 0
                    onClicked: currentStep--
                    font.pixelSize: 32
                    Layout.preferredWidth: 44
                    Layout.preferredHeight: 80
                    background: Rectangle {
                        color: parent.pressed ? "#f79009" : "transparent"
                        radius: 22
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#aaa"
                        font: parent.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
                // Platzhalter für linken Pfeil wenn nicht sichtbar
                Rectangle {
                    visible: currentStep === 0
                    Layout.preferredWidth: 44
                    Layout.preferredHeight: 80
                    color: "transparent"
                }
                // Eingabefeld
                Loader {
                    id: stepLoader
                    Layout.fillWidth: true
                    Layout.preferredHeight: 80
                    sourceComponent: currentStep === 0 ? fahrerStep : currentStep === 1 ? fahrzeugStep : kwStep
                }
                // Rechter Pfeil oder Speichern-Button
                Button {
                    text: currentStep < 2 ? ">" : "Speichern"
                    onClicked: {
                        if (currentStep < 2) {
                            currentStep++
                        } else {
                            wizardCard.wizardFertig(selectedFahrer, selectedFahrzeug, selectedKW)
                        }
                    }
                    font.pixelSize: currentStep < 2 ? 32 : 16
                    Layout.preferredWidth: currentStep < 2 ? 44 : 120
                    Layout.preferredHeight: 80
                    background: Rectangle {
                        color: parent.pressed ? "#f79009" : currentStep < 2 ? "transparent" : "#2ecc71"
                        radius: currentStep < 2 ? 22 : 10
                    }
                    contentItem: Text {
                        text: parent.text
                        color: currentStep < 2 ? "#2ecc71" : "white"
                        font: parent.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
        // Abbrechen-Button unten
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Button {
                text: "❌"
                onClicked: wizardCard.visible = false
                font.pixelSize: 22
                Layout.preferredWidth: 60
                Layout.preferredHeight: 60
                background: Rectangle {
                    color: "transparent"
                }
                contentItem: Text {
                    text: parent.text
                    color: "red"
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }
    
    // Schritt 1: Fahrer
    Component {
        id: fahrerStep
        ComboBox {
            id: fahrerCombo
            model: wizardCard.fahrerList || []
            currentIndex: wizardCard.fahrerList ? wizardCard.fahrerList.indexOf(wizardCard.selectedFahrer) : -1
            editable: true
            font.pixelSize: 44
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            background: Rectangle {
                color: "#111"
                border.color: "#f79009"
                border.width: 2
                radius: 20
            }
            contentItem: TextInput {
                color: "#fff"
                font: parent && parent.ComboBox && parent.ComboBox.font ? parent.ComboBox.font : Qt.font({pixelSize: 16})
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                readOnly: false
                text: typeof parent !== 'undefined' && parent.ComboBox && typeof parent.ComboBox.editText !== 'undefined' ? parent.ComboBox.editText : ""
                onTextChanged: wizardCard.selectedFahrer = text
            }
            onCurrentTextChanged: wizardCard.selectedFahrer = currentText
            onEditTextChanged: wizardCard.selectedFahrer = editText
        }
    }
    
    // Schritt 2: Fahrzeug
    Component {
        id: fahrzeugStep
        ComboBox {
            id: fahrzeugCombo
            model: wizardCard.fahrzeugList || []
            currentIndex: wizardCard.fahrzeugList ? wizardCard.fahrzeugList.indexOf(wizardCard.selectedFahrzeug) : -1
            editable: true
            font.pixelSize: 44
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            background: Rectangle {
                color: "#111"
                border.color: "#f79009"
                border.width: 2
                radius: 20
            }
            contentItem: TextInput {
                color: "#fff"
                font: parent && parent.ComboBox && parent.ComboBox.font ? parent.ComboBox.font : Qt.font({pixelSize: 16})
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                readOnly: false
                text: typeof parent !== 'undefined' && parent.ComboBox && typeof parent.ComboBox.editText !== 'undefined' ? parent.ComboBox.editText : ""
                onTextChanged: wizardCard.selectedFahrzeug = text
            }
            onCurrentTextChanged: wizardCard.selectedFahrzeug = currentText
            onEditTextChanged: wizardCard.selectedFahrzeug = editText
        }
    }
    
    // Schritt 3: KW
    Component {
        id: kwStep
        ComboBox {
            id: kwCombo
            model: wizardCard.kwList || []
            currentIndex: wizardCard.kwList ? wizardCard.kwList.indexOf(wizardCard.selectedKW) : -1
            editable: true
            font.pixelSize: 44
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            background: Rectangle {
                color: "#111"
                border.color: "#f79009"
                border.width: 2
                radius: 20
            }
            contentItem: TextInput {
                color: "#fff"
                font: parent && parent.ComboBox && parent.ComboBox.font ? parent.ComboBox.font : Qt.font({pixelSize: 16})
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                readOnly: false
                text: typeof parent !== 'undefined' && parent.ComboBox && typeof parent.ComboBox.editText !== 'undefined' ? parent.ComboBox.editText : ""
                onTextChanged: wizardCard.selectedKW = text
            }
            onCurrentTextChanged: wizardCard.selectedKW = currentText
            onEditTextChanged: wizardCard.selectedKW = editText
        }
    }
} 