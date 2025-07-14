import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property var goHome: function() {
        // Fallback: Blende die Fahrzeugseite aus und zeige das MainMenu
        root.visible = false;
        if (typeof mainWindow !== 'undefined') {
            mainWindow.stackVisible = false;
        }
    }
    color: Style.background

    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
    }

    // Tabelle direkt anzeigen und wie bei Abrechnung positionieren
    Component.onCompleted: fahrzeugBackend.anzeigenFahrzeuge()
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        anchors.topMargin: 52
        anchors.bottomMargin: 115
        anchors.rightMargin: 100
        anchors.leftMargin: 100
        spacing: 8
        ListView {
            id: fahrzeugListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: fahrzeugBackend.fahrzeugList
            spacing: Style.spacingSmall
            clip: true
            header: Rectangle {
                width: fahrzeugListView.width
                height: 40
                color: "transparent"
                GridLayout {
                    columns: 6
                    anchors.fill: parent
                    rowSpacing: 0
                    columnSpacing: Style.spacingLarge
                    // Leere Felder für die ersten vier Spalten
                    Item { Layout.preferredWidth: 120 }
                    Item { Layout.preferredWidth: 80 }
                    Item { Layout.preferredWidth: 100 }
                    Item { Layout.preferredWidth: 80 }
                    // Überschrift Versicherung
            Text {
                        text: "Versicherung"
                font.bold: true
                        color: "#b0b0b0"
                        font.family: ubuntuFont.name
                        font.pixelSize: Style.fontSizeTitle
                        Layout.preferredWidth: 100
                        horizontalAlignment: Text.AlignRight
                    }
                    // Überschrift Finanzierung
                    Text {
                        text: "Finanzierung"
                        font.bold: true
                        color: "#b0b0b0"
                        font.family: ubuntuFont.name
                        font.pixelSize: Style.fontSizeTitle
                        Layout.preferredWidth: 100
                        horizontalAlignment: Text.AlignRight
                    }
                }
            }
            delegate: Rectangle {
                width: fahrzeugListView.width
                height: 40
                property bool hovered: false
                color: hovered ? "#222" : (index % 2 === 0 ? Style.background : Style.border)
                        radius: Style.radiusNormal
                        border.color: Style.border
                        border.width: 1
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.hovered = true
                    onExited: parent.hovered = false
                    onDoubleClicked: {
                        // Hier kann ein Bearbeitungsdialog geöffnet werden
                        console.log("Bearbeiten: ", modelData)
                        // Beispiel: fahrzeugBackend.bearbeiteFahrzeug(modelData)
                    }
                }
                GridLayout {
                    columns: 6
                    anchors.fill: parent
                    rowSpacing: 0
                    columnSpacing: Style.spacingLarge
                    Text {
                        text: modelData.kennzeichen !== undefined && modelData.kennzeichen !== "" ? modelData.kennzeichen : "-"
                        color: "white"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        Layout.preferredWidth: 120
                        horizontalAlignment: modelData.kennzeichen !== undefined && modelData.kennzeichen !== "" ? Text.AlignLeft : Text.AlignHCenter
                    }
                    Text {
                        text: modelData.rfrnc !== undefined && modelData.rfrnc !== "" ? modelData.rfrnc : "-"
                        color: "white"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        Layout.preferredWidth: 80
                        horizontalAlignment: modelData.rfrnc !== undefined && modelData.rfrnc !== "" ? Text.AlignLeft : Text.AlignHCenter
                    }
                    Text {
                        text: modelData.modell !== undefined && modelData.modell !== "" ? modelData.modell : "-"
                        color: "white"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        Layout.preferredWidth: 100
                        horizontalAlignment: modelData.modell !== undefined && modelData.modell !== "" ? Text.AlignLeft : Text.AlignHCenter
                    }
                    Text {
                        text: modelData.baujahr !== undefined && modelData.baujahr !== "" ? modelData.baujahr : "-"
                        color: "white"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        Layout.preferredWidth: 80
                        horizontalAlignment: modelData.baujahr !== undefined && modelData.baujahr !== "" ? Text.AlignLeft : Text.AlignHCenter
                    }
                    Text {
                        text: (modelData.versicherung !== undefined && modelData.versicherung !== "") ? modelData.versicherung + " €" : "-"
                        color: "white"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        Layout.preferredWidth: 100
                        horizontalAlignment: (modelData.versicherung !== undefined && modelData.versicherung !== "") ? Text.AlignRight : Text.AlignHCenter
                    }
                    Text {
                        text: (modelData.finanzierung !== undefined && modelData.finanzierung !== "") ? modelData.finanzierung + " €" : "-"
                        color: "white"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        Layout.preferredWidth: 100
                        horizontalAlignment: (modelData.finanzierung !== undefined && modelData.finanzierung !== "") ? Text.AlignRight : Text.AlignHCenter
                    }
                }
            }
        }
    }
    // BottomBar von Abrechnung (außerhalb des ColumnLayouts)
    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        anchors.topMargin: 100
        spacing: 32
        // Home-Button
        MouseArea {
            id: homeArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                if (typeof root.goHome === "function") {
                    root.goHome();
                } else {
                    console.warn("goHome ist nicht definiert oder keine Funktion!");
                }
            }
            Image {
                                    anchors.centerIn: parent
                source: homeArea.pressed ? "assets/icons/home_gray.svg"
                    : homeArea.containsMouse ? "assets/icons/home_orange.svg" : "assets/icons/home_white.svg"
                width: homeArea.pressed ? 32 : homeArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        // Add-Button (statt Check-Button)
                        MouseArea {
            id: addArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
                            hoverEnabled: true
                            onClicked: {
                fahrzeugBackend.showVehicleWizard()
            }
            Image {
                anchors.centerIn: parent
                source: addArea.pressed ? "assets/icons/add_gray.svg"
                    : addArea.containsMouse ? "assets/icons/add_orange.svg" : "assets/icons/add_white.svg"
                width: addArea.pressed ? 40 : addArea.containsMouse ? 48 : 40
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        // Edit-Button (statt Redo-Button)
        MouseArea {
            id: editArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: fahrzeugBackend.editVehicleWizard()
            Image {
                anchors.centerIn: parent
                source: editArea.pressed ? "assets/icons/edit_gray.svg"
                    : editArea.containsMouse ? "assets/icons/edit_orange.svg" : "assets/icons/edit_white.svg"
                width: editArea.pressed ? 32 : editArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
    }
} 