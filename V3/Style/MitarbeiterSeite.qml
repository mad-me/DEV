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

    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
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
        
        ListView {
            id: mitarbeiterListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: mitarbeiterBackend.mitarbeiterList
            spacing: Style.spacingSmall
            clip: true
            header: Rectangle {
                width: mitarbeiterListView.width
                height: 40
                color: "transparent"
            RowLayout {
                anchors.fill: parent
                    spacing: Style.spacingLarge
                    
                    // Statischer Bereich - immer sichtbar
                    Rectangle {
                        Layout.preferredWidth: 470  // 70 + 200 + 200
                        Layout.minimumWidth: 470
                        Layout.maximumWidth: 470
                        height: 40
                        color: "transparent"
                        RowLayout {
                            anchors.fill: parent
                            spacing: Style.spacingLarge
                            Text { text: "ID"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 70; Layout.maximumWidth: 70; Layout.minimumWidth: 70; horizontalAlignment: Text.AlignRight }
                            Text { text: "Vorname"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 200; Layout.minimumWidth: 200; Layout.maximumWidth: 200; horizontalAlignment: Text.AlignLeft }
                            Text { text: "Nachname"; font.bold: true; color: "#b0b0b0"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeTitle; Layout.preferredWidth: 200; Layout.minimumWidth: 200; Layout.maximumWidth: 200; horizontalAlignment: Text.AlignLeft }
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
                            
                            Text {
                                text: "Telefon"
                                font.bold: true
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                font.pixelSize: Style.fontSizeTitle
                                Layout.preferredWidth: 120
                                Layout.minimumWidth: 150
                                visible: root.width >= 1000
                            }
                            Text {
                                text: "E-Mail"
                            font.bold: true
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                font.pixelSize: Style.fontSizeTitle
                                Layout.preferredWidth: 180
                                Layout.minimumWidth: 300
                                visible: root.width >= 1650
                            }
                            Text {
                                text: "Einstellungsdatum"
                                font.bold: true
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                font.pixelSize: Style.fontSizeTitle
                                Layout.preferredWidth: 120
                                visible: root.width >= 1400
                            }
                            Text { 
                                text: "Status"; 
                                font.bold: true; 
                                color: "#b0b0b0"; 
                                font.family: ubuntuFont.name; 
                                font.pixelSize: Style.fontSizeTitle; 
                                Layout.preferredWidth: 100;
                            }
                        }
                        
                        // Deals-Ansicht Spalten
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
            }
            delegate: Rectangle {
                width: mitarbeiterListView.width
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
                        if (mitarbeiterBackend.toggleView) {
                            // In Deals-Ansicht: Deals-Wizard öffnen
                            mitarbeiterBackend.editDealsWizard(index)
                        } else {
                            // In Standard-Ansicht: Standard-Wizard öffnen
                            mitarbeiterBackend.editMitarbeiterWizard_with_index(index)
                        }
                    }
                }
                RowLayout {
                    anchors.fill: parent
                    spacing: Style.spacingLarge
                    
                    // Statischer Bereich - immer sichtbar
                    Rectangle {
                        Layout.preferredWidth: 470  // 70 + 200 + 200
                        Layout.minimumWidth: 470
                        Layout.maximumWidth: 470
                        height: 40
                        color: "transparent"
                        RowLayout {
                            anchors.fill: parent
                            spacing: Style.spacingLarge
                            Text { text: modelData.driver_id !== undefined && modelData.driver_id !== "" ? modelData.driver_id : "-"; color: "white"; font.family: ubuntuFont.name; font.pixelSize: 24; Layout.preferredWidth: 70; Layout.maximumWidth: 70; Layout.minimumWidth: 70; horizontalAlignment: modelData.driver_id !== undefined && modelData.driver_id !== "" ? Text.AlignRight : Text.AlignHCenter }
                            Text { text: modelData.first_name !== undefined && modelData.first_name !== "" ? modelData.first_name : "-"; color: "white"; font.family: ubuntuFont.name; font.pixelSize: 24; Layout.preferredWidth: 200; Layout.minimumWidth: 200; Layout.maximumWidth: 200; horizontalAlignment: modelData.first_name !== undefined && modelData.first_name !== "" ? Text.AlignLeft : Text.AlignHCenter }
                            Text { text: modelData.last_name !== undefined && modelData.last_name !== "" ? modelData.last_name : "-"; color: "white"; font.family: ubuntuFont.name; font.pixelSize: 24; Layout.preferredWidth: 200; Layout.minimumWidth: 200; Layout.maximumWidth: 200; horizontalAlignment: modelData.last_name !== undefined && modelData.last_name !== "" ? Text.AlignLeft : Text.AlignHCenter }
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
                            
                            Text {
                                text: modelData.phone !== undefined && modelData.phone !== "" ? modelData.phone : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: 24
                                Layout.preferredWidth: 120
                                Layout.minimumWidth: 150
                                horizontalAlignment: modelData.phone !== undefined && modelData.phone !== "" ? Text.AlignLeft : Text.AlignHCenter
                                visible: root.width >= 1000
                            }
                            Text {
                                text: modelData.email !== undefined && modelData.email !== "" ? modelData.email : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: 24
                                Layout.preferredWidth: 180
                                Layout.minimumWidth: 300
                                horizontalAlignment: modelData.email !== undefined && modelData.email !== "" ? Text.AlignLeft : Text.AlignHCenter
                                visible: root.width >= 1650
                            }
                            Text {
                                text: modelData.hire_date !== undefined && modelData.hire_date !== "" ? modelData.hire_date : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: 24
                                Layout.preferredWidth: 120
                                horizontalAlignment: modelData.hire_date !== undefined && modelData.hire_date !== "" ? Text.AlignLeft : Text.AlignHCenter
                                visible: root.width >= 1400
                            }
                            Text { 
                                text: modelData.status !== undefined && modelData.status !== "" ? modelData.status : "-"; 
                                color: "white"; 
                                font.family: ubuntuFont.name; 
                                font.pixelSize: 24; 
                                Layout.preferredWidth: 100; 
                                horizontalAlignment: modelData.status !== undefined && modelData.status !== "" ? Text.AlignLeft : Text.AlignHCenter;
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
                                font.pixelSize: 24
                                Layout.preferredWidth: 80
                                horizontalAlignment: Text.AlignHCenter
                            }
                            Text {
                                text: modelData.pauschale !== undefined ? modelData.pauschale : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: 24
                                Layout.preferredWidth: 100
                                horizontalAlignment: modelData.pauschale !== undefined && modelData.pauschale !== "-" ? Text.AlignRight : Text.AlignHCenter
                            }
                            Text {
                                text: modelData.umsatzgrenze !== undefined ? modelData.umsatzgrenze : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: 24
                                Layout.preferredWidth: 120
                                horizontalAlignment: modelData.umsatzgrenze !== undefined && modelData.umsatzgrenze !== "-" ? Text.AlignRight : Text.AlignHCenter
                                visible: root.width >= 1400
                            }
                            Text {
                                text: modelData.garage !== undefined ? modelData.garage : "-"
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: 24
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
            anchors.margins: 8
            width: 56
            height: 56
            radius: 28
            color: "transparent"
            property bool hovered: false
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
                    (parent.hovered ? "assets/icons/tips_orange.svg" : "assets/icons/tips_gray.svg")
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