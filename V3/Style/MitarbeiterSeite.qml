import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property var goHome: function() {
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

    Component.onCompleted: mitarbeiterBackend.anzeigenMitarbeiter()
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
            Rectangle {
                Layout.preferredWidth: 520
                Layout.minimumWidth: 520
                Layout.maximumWidth: 520
                height: 40
                color: "transparent"
                RowLayout {
                    anchors.fill: parent
                    spacing: Style.spacingLarge
                    Text { text: "ID"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 70; Layout.maximumWidth: 70; Layout.minimumWidth: 70; horizontalAlignment: Text.AlignRight }
                    Text { text: "Vorname"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 200; Layout.minimumWidth: 200; Layout.maximumWidth: 200; horizontalAlignment: Text.AlignLeft }
                    Text { text: "Nachname"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 250; Layout.minimumWidth: 250; Layout.maximumWidth: 250; horizontalAlignment: Text.AlignLeft }
                }
            }
            Item {
                Layout.fillWidth: true
                height: 40
                // Dynamischer Header-Bereich
                RowLayout {
                    anchors.fill: parent
                    spacing: Style.spacingLarge
                    visible: !mitarbeiterBackend.toggleView
                    Item { Layout.preferredWidth: 450 }
                    // Suchleiste statt Telefon/E-Mail-Titel
                    Rectangle {
                        Layout.preferredWidth: 300
                        Layout.minimumWidth: 300
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
                        // Icon nur anzeigen, wenn das Suchfeld nicht aktiv ist
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
                            source: parent.iconHovered ? "assets/icons/person_search_orange.svg" : "assets/icons/person_search_gray.svg"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: parent.iconHovered ? 40 : 28
                            height: parent.iconHovered ? 40 : 28
                            visible: !parent.suchfeldAktiv
                            opacity: 0.7
                        }
                        // Suchfeld nur anzeigen, wenn aktiv
                        TextField {
                            id: suchfeld
                            anchors.fill: parent
                            anchors.margins: 2
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
                            onTextChanged: function(newText) { mitarbeiterBackend.filterText = newText }
                            onActiveFocusChanged: {
                                if (!activeFocus && text.length === 0) {
                                    parent.suchfeldAktiv = false;
                                }
                            }
                        }
                    }
                    Item { Layout.preferredWidth: 370 }
                    Text {
                        text: "Einstellungsdatum"
                        font.bold: true
                        color: "#b0b0b0"
                        font.family: ubuntuFont.name
                        font.pixelSize: Style.fontSizeTitle
                        Layout.preferredWidth: 120
                        Layout.leftMargin: 257
                        visible: root.width >= 1400
                        horizontalAlignment: Text.AlignLeft
                    }
                    Item {
                        Layout.preferredWidth: 300
                        Layout.fillWidth: true
                    }
                    Switch {
                        id: statusFilterSwitch
                        checked: mitarbeiterBackend.showOnlyActive
                        onToggled: mitarbeiterBackend.showOnlyActive = checked
                        Layout.preferredWidth: 100
                        ToolTip.visible: statusFilterSwitch.hovered
                        ToolTip.text: "Nur aktive Fahrer anzeigen"
                    }
                }
                RowLayout {
                    anchors.fill: parent
                    spacing: Style.spacingLarge
                    visible: mitarbeiterBackend.toggleView
                    Text {
                        text: "Deals"
                        font.bold: true
                        color: "#b0b0b0"
                        font.family: ubuntuFont.name
                        font.pixelSize: Style.fontSizeTitle
                        Layout.preferredWidth: 80
                        horizontalAlignment: Text.AlignHCenter
                    }
                    Text {
                        text: "Pauschale"
                        font.bold: true
                        color: "#b0b0b0"
                        font.family: ubuntuFont.name
                        font.pixelSize: Style.fontSizeTitle
                        Layout.preferredWidth: 100
                    }
                    Text {
                        text: "Umsatzgrenze"
                        font.bold: true
                        color: "#b0b0b0"
                        font.family: ubuntuFont.name
                        font.pixelSize: Style.fontSizeTitle
                        Layout.preferredWidth: 120
                        visible: root.width >= 1400
                    }
                    Text {
                        text: "Garage"
                        font.bold: true
                        color: "#b0b0b0"
                        font.family: ubuntuFont.name
                        font.pixelSize: Style.fontSizeTitle
                        Layout.preferredWidth: 100
                    }
                }
            }
        }
        // Abstand zwischen Header und Tabelle
        Item { height: 8 }
        // Die eigentliche Tabelle
        ListView {
            id: mitarbeiterListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: mitarbeiterBackend.mitarbeiterList
            spacing: Style.spacingSmall
            clip: true
            delegate: Rectangle {
                width: mitarbeiterListView.width
                height: 40
                property bool hovered: false
                color: hovered ? "transparent" : Style.background
                radius: Style.radiusNormal
                border.color: "transparent"
                border.width: 0
                opacity: modelData.status !== "active" ? 0.3 : 1.0
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
                    propagateComposedEvents: true
                    onEntered: parent.hovered = true
                    onExited: parent.hovered = false
                    onDoubleClicked: {
                        if (mitarbeiterBackend.toggleView) {
                            mitarbeiterBackend.editDealsWizard_by_id(modelData.driver_id)
                        } else {
                            mitarbeiterBackend.editMitarbeiterWizard_by_id(modelData.driver_id)
                        }
                    }
                }
                RowLayout {
                    anchors.fill: parent
                    spacing: Style.spacingLarge
                    
                    // Statischer Bereich - immer sichtbar
                    Rectangle {
                        Layout.preferredWidth: 520  // 70 + 200 + 250
                        Layout.minimumWidth: 520
                        Layout.maximumWidth: 520
                        height: 40
                        color: "transparent"
                        RowLayout {
                            anchors.fill: parent
                            spacing: Style.spacingLarge
                            Text { text: modelData.driver_id !== undefined && modelData.driver_id !== "" ? modelData.driver_id : "-"; color: "white"; font.family: ubuntuFont.name; font.pixelSize: hovered ? 28 : 24; Layout.preferredWidth: 70; Layout.maximumWidth: 70; Layout.minimumWidth: 70; horizontalAlignment: modelData.driver_id !== undefined && modelData.driver_id !== "" ? Text.AlignRight : Text.AlignHCenter }
                            Text { text: modelData.first_name !== undefined && modelData.first_name !== "" ? modelData.first_name : "-"; color: "white"; font.family: ubuntuFont.name; font.pixelSize: hovered ? 28 : 24; Layout.preferredWidth: 200; Layout.minimumWidth: 200; Layout.maximumWidth: 200; horizontalAlignment: modelData.first_name !== undefined && modelData.first_name !== "" ? Text.AlignLeft : Text.AlignHCenter }
                            Text { text: modelData.last_name !== undefined && modelData.last_name !== "" ? modelData.last_name : "-"; color: "white"; font.family: ubuntuFont.name; font.pixelSize: hovered ? 28 : 24; Layout.preferredWidth: 250; Layout.minimumWidth: 250; Layout.maximumWidth: 250; horizontalAlignment: modelData.last_name !== undefined && modelData.last_name !== "" ? Text.AlignLeft : Text.AlignHCenter }
                        }
                    }
                    
                    // Dynamischer Bereich - je nach Ansicht
                    Item {
                        Layout.fillWidth: true
                        height: 40
                        
                        // Standard-Ansicht Spalten
                        RowLayout {
                            anchors.fill: parent
                            spacing: Style.spacingLarge
                            visible: !mitarbeiterBackend.toggleView
                            
                            Item { Layout.preferredWidth: 400 }
                            Text {
                                text: modelData.phone !== undefined && modelData.phone !== "" ? modelData.phone : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 28 : 24
                                Layout.preferredWidth: 120
                                Layout.minimumWidth: 150
                                horizontalAlignment: modelData.phone !== undefined && modelData.phone !== "" ? Text.AlignLeft : Text.AlignHCenter
                                visible: root.width >= 1000
                            }
                            Item { Layout.preferredWidth: 100 }
                            Text {
                                text: modelData.email !== undefined && modelData.email !== "" ? modelData.email : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 28 : 24
                                Layout.preferredWidth: 180
                                Layout.minimumWidth: 300
                                horizontalAlignment: modelData.email !== undefined && modelData.email !== "" ? Text.AlignLeft : Text.AlignHCenter
                                visible: root.width >= 1650
                            }
                            Item { Layout.preferredWidth: 400 }
                            Text {
                                text: modelData.hire_date !== undefined && modelData.hire_date !== "" ? modelData.hire_date : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 28 : 24
                                Layout.preferredWidth: 120
                                horizontalAlignment: modelData.hire_date !== undefined && modelData.hire_date !== "" ? Text.AlignLeft : Text.AlignHCenter
                                visible: root.width >= 1400
                            }
                            Item {
                                Layout.preferredWidth: 300
                                Layout.fillWidth: true
                            }
                            Switch {
                                checked: modelData.status === "active"
                                Layout.preferredWidth: 100
                                scale: hovered ? 1.15 : 1.0
                                onToggled: mitarbeiterBackend.updateStatusById(modelData.driver_id, checked ? "active" : "inactive")
                            }
                        }
                        
                        // Deals-Ansicht Spalten
                        RowLayout {
                            anchors.fill: parent
                            spacing: Style.spacingLarge
                            visible: mitarbeiterBackend.toggleView
                            
                            Text {
                                text: modelData.deal !== undefined ? modelData.deal : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 28 : 24
                                Layout.preferredWidth: 80
                                horizontalAlignment: Text.AlignHCenter
                            }
                            Text {
                                text: modelData.pauschale !== undefined ? modelData.pauschale : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 28 : 24
                                Layout.preferredWidth: 100
                                horizontalAlignment: modelData.pauschale !== undefined && modelData.pauschale !== "-" ? Text.AlignRight : Text.AlignHCenter
                            }
                            Text {
                                text: modelData.umsatzgrenze !== undefined ? modelData.umsatzgrenze : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 28 : 24
                                Layout.preferredWidth: 120
                                horizontalAlignment: modelData.umsatzgrenze !== undefined && modelData.umsatzgrenze !== "-" ? Text.AlignRight : Text.AlignHCenter
                                visible: root.width >= 1400
                            }
                            Text {
                                text: modelData.garage !== undefined ? modelData.garage : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 28 : 24
                                Layout.preferredWidth: 100
                                horizontalAlignment: modelData.garage !== undefined && modelData.garage !== "-" ? Text.AlignRight : Text.AlignHCenter
                            }
                        }
                    }
                }
            }
        }
        
        // Toggle Button - außerhalb der Tabelle rechts unten
        Rectangle {
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 18
            width: 56
            height: 56
            radius: 28
            color: "transparent"
            property bool hovered: false
            visible: mitarbeiterBackend.showOnlyActive
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true
                onEntered: parent.hovered = true
                onExited: parent.hovered = false
                onClicked: mitarbeiterBackend.toggleViewMode()
            }
            Image {
                anchors.centerIn: parent
                source: mitarbeiterBackend.toggleView ? 
                    (parent.hovered ? "assets/icons/contact_details_orange.svg" : "assets/icons/contact_details_gray.svg") :
                    (parent.hovered ? "assets/icons/deal_orange.svg" : "assets/icons/deal_gray.svg")
                width: parent.hovered ? 40 : 32
                height: parent.hovered ? 40 : 32
                fillMode: Image.PreserveAspectFit
            }
        }
    }
                        RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        anchors.topMargin: 100
        spacing: 32
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
        MouseArea {
            id: addArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: mitarbeiterBackend.showMitarbeiterWizard()
            Image {
                anchors.centerIn: parent
                source: addArea.pressed ? "assets/icons/add_gray.svg"
                    : addArea.containsMouse ? "assets/icons/add_orange.svg" : "assets/icons/add_white.svg"
                width: addArea.pressed ? 40 : addArea.containsMouse ? 48 : 40
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        MouseArea {
            id: editArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: mitarbeiterBackend.editMitarbeiterWizard()
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