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
    radius: Style.radiusNormal

    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
    }

    FontLoader {
        id: spaceMonoFont
        source: "assets/fonts/SpaceMono-Regular.ttf"
    }

    // Tabelle wird beim Backend-Initialisieren geladen
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        anchors.topMargin: 52
        anchors.bottomMargin: 115
        anchors.rightMargin: 100
        anchors.leftMargin: 100
        spacing: 8

        // Sticky Header außerhalb der ListView
        RowLayout {
            Layout.fillWidth: true
            spacing: Style.spacingLarge
            RowLayout {
                Layout.fillWidth: true
                spacing: Style.spacingLarge
                Item { Layout.preferredWidth: 75 }
                Text { text: "Kennzeichen"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 120; horizontalAlignment: Text.AlignLeft }
                Item { Layout.preferredWidth: 100 }
                Text { text: "Referenz"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 120; horizontalAlignment: Text.AlignLeft }
                Item { Layout.preferredWidth: 350 }
                Item { Layout.preferredWidth: 100 }
                // Suchfeld exakt über Baujahr+Modell (80+100+150=330, daher Layout.preferredWidth: 330)
                Rectangle {
                    Layout.preferredWidth: 370
                    Layout.minimumWidth: 230
                    height: 64
                    radius: Style.radiusNormal
                    color: "transparent"
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#1a1a1a" }
                        GradientStop { position: 0.1; color: "#1a1a1a" }
                        GradientStop { position: 1.0; color: "#050505" }
                    }
                    property bool suchfeldAktiv: false
                    property bool iconHovered: false
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: !parent.suchfeldAktiv
                        onEntered: parent.iconHovered = true
                        onExited: parent.iconHovered = false
                        onClicked: {
                            parent.suchfeldAktiv = true;
                            suchfeld.forceActiveFocus();
                        }
                    }
                    Image {
                        id: suchIcon
                        source: parent.iconHovered ? "assets/icons/vehicle_orange.svg" : "assets/icons/vehicle_gray.svg"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.horizontalCenterOffset: 9
                        width: parent.iconHovered ? 40 : 28
                        height: parent.iconHovered ? 40 : 28
                        visible: !parent.suchfeldAktiv
                        opacity: 0.7
                    }
                    TextField {
                        id: suchfeld
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.margins: 2
                        anchors.rightMargin: 15
                        font.pixelSize: 32
                        font.family: spaceMonoFont.name
                        color: "white"
                        background: null
                        padding: 32
                        horizontalAlignment: TextInput.AlignHCenter
                        verticalAlignment: TextInput.AlignVCenter
                        placeholderText: ""
                        selectionColor: "#a2ffb5"
                        selectedTextColor: "#232323"
                        visible: parent.suchfeldAktiv
                        cursorVisible: true
                        onTextChanged: function(newText) { fahrzeugBackend.filterText = newText }
                        onActiveFocusChanged: {
                            if (!activeFocus && text.length === 0) {
                                parent.suchfeldAktiv = false;
                            }
                        }
                    }
                }
                Item { Layout.preferredWidth: 341 }
                Item { Layout.preferredWidth: 100 }
                Text { text: "Versicherung"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 120; horizontalAlignment: Text.AlignRight }
                Item { Layout.preferredWidth: 100 }
                Text { text: "Finanzierung"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 120; horizontalAlignment: Text.AlignRight }
            }
        }
        // Abstand zwischen Header und Tabelle
        Item { height: 8 }
        // Die eigentliche Tabelle
        ListView {
            id: fahrzeugListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: fahrzeugBackend.fahrzeugList
            spacing: Style.spacingSmall
            clip: true
            delegate: Rectangle {
                width: fahrzeugListView.width
                height: 40
                property bool hovered: false
                color: hovered ? "transparent" : Style.background
                radius: Style.radiusNormal
                border.color: "transparent"
                border.width: 0
                // Gradient nur beim Hover
                Rectangle {
                    anchors.fill: parent
                    radius: Style.radiusNormal
                    visible: hovered
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#1a1a1a" }
                        GradientStop { position: 0.1; color: "#1a1a1a" }
                        GradientStop { position: 1.0; color: "#050505" }
                    }
                    z: -1
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.hovered = true
                    onExited: parent.hovered = false
                    onDoubleClicked: {
                        fahrzeugBackend.editVehicleWizard_by_id(modelData.kennzeichen)
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Style.spacingLarge
                    // Tabelle über die ganze Zeile strecken
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Style.spacingLarge
                        Item { Layout.preferredWidth: 75 }
                        Text {
                            text: modelData.kennzeichen !== undefined && modelData.kennzeichen !== "" ? modelData.kennzeichen : ""
                            color: "white"
                            font.family: ubuntuFont.name
                            font.pixelSize: hovered ? 28 : 24
                            Layout.preferredWidth: 120
                            horizontalAlignment: modelData.kennzeichen !== undefined && modelData.kennzeichen !== "" ? Text.AlignLeft : Text.AlignHCenter
                        }
                        Item { Layout.preferredWidth: 100 }
                        Text {
                            text: modelData.rfrnc !== undefined && modelData.rfrnc !== "" ? modelData.rfrnc : ""
                            color: "white"
                            font.family: ubuntuFont.name
                            font.pixelSize: hovered ? 28 : 24
                            Layout.preferredWidth: 120
                            horizontalAlignment: modelData.rfrnc !== undefined && modelData.rfrnc !== "" ? Text.AlignLeft : Text.AlignHCenter
                        }
                        Item { Layout.preferredWidth: 350 }
                        Item { Layout.preferredWidth: 100 }
                        Text {
                            text: modelData.baujahr !== undefined && modelData.baujahr !== "" ? modelData.baujahr : ""
                            color: "white"
                            font.family: ubuntuFont.name
                            font.pixelSize: hovered ? 28 : 24
                            Layout.preferredWidth: 80
                            horizontalAlignment: modelData.baujahr !== undefined && modelData.baujahr !== "" ? Text.AlignLeft : Text.AlignHCenter
                        }
                        Item { Layout.preferredWidth: 100 }
                        Text {
                            text: modelData.modell !== undefined && modelData.modell !== "" ? modelData.modell : ""
                            color: "white"
                            font.family: ubuntuFont.name
                            font.pixelSize: hovered ? 28 : 24
                            Layout.preferredWidth: 150
                            horizontalAlignment: modelData.modell !== undefined && modelData.modell !== "" ? Text.AlignLeft : Text.AlignHCenter
                        }
                        Item { Layout.preferredWidth: 350 }
                        Item { Layout.preferredWidth: 100 }
                        Text {
                            text: (modelData.versicherung !== undefined && modelData.versicherung !== "") ? modelData.versicherung + " €" : ""
                            color: "white"
                            font.family: ubuntuFont.name
                            font.pixelSize: hovered ? 28 : 24
                            Layout.preferredWidth: 120
                            horizontalAlignment: (modelData.versicherung !== undefined && modelData.versicherung !== "") ? Text.AlignRight : Text.AlignHCenter
                        }
                        Item { Layout.preferredWidth: 100 }
                        Text {
                            text: (modelData.finanzierung !== undefined && modelData.finanzierung !== "") ? modelData.finanzierung + " €" : ""
                            color: "white"
                            font.family: ubuntuFont.name
                            font.pixelSize: hovered ? 28 : 24
                            Layout.preferredWidth: 120
                            horizontalAlignment: (modelData.finanzierung !== undefined && modelData.finanzierung !== "") ? Text.AlignRight : Text.AlignHCenter
                        }
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