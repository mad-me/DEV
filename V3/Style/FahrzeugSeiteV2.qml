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

    // Hauptlayout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        anchors.topMargin: 52
        anchors.bottomMargin: 115
        anchors.rightMargin: 100
        anchors.leftMargin: 100
        spacing: 16

        // Header mit Titel und Status
        RowLayout {
            Layout.fillWidth: true
            spacing: Style.spacingLarge
            
            Text {
                text: "Fahrzeugverwaltung"
                font.family: ubuntuFont.name
                font.pixelSize: 36
                font.bold: true
                color: "white"
                Layout.fillWidth: true
            }
            
            // Status-Anzeige
            Rectangle {
                Layout.preferredWidth: 300
                height: 50
                radius: Style.radiusNormal
                color: "transparent"
                border.color: "#333333"
                border.width: 1
                
                Text {
                    anchors.centerIn: parent
                    text: fahrzeugBackendV2.statusMessage || "Bereit"
                    font.family: ubuntuFont.name
                    font.pixelSize: 16
                    color: "#cccccc"
                    horizontalAlignment: Text.AlignHCenter
                }
            }
            
            // Filter-Toggle
            Rectangle {
                Layout.preferredWidth: 120
                height: 50
                radius: Style.radiusNormal
                color: fahrzeugBackendV2.showOnlyActive ? "#2a5a2a" : "#5a2a2a"
                border.color: "#333333"
                border.width: 1
                
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: fahrzeugBackendV2.showOnlyActive = !fahrzeugBackendV2.showOnlyActive
                    
                    Text {
                        anchors.centerIn: parent
                        text: fahrzeugBackendV2.showOnlyActive ? "Nur Aktiv" : "Alle"
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
        }

        // Suchfeld und Aktionen
        RowLayout {
            Layout.fillWidth: true
            spacing: Style.spacingLarge
            
            // Erweiterte Suchleiste
            Rectangle {
                Layout.fillWidth: true
                height: 64
                radius: Style.radiusNormal
                color: "transparent"
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#1a1a1a" }
                    GradientStop { position: 0.1; color: "#1a1a1a" }
                    GradientStop { position: 1.0; color: "#050505" }
                }
                border.color: "#333333"
                border.width: 1
                
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
                    placeholderText: "Fahrzeug suchen..."
                    selectionColor: "#a2ffb5"
                    selectedTextColor: "#232323"
                    visible: parent.suchfeldAktiv
                    cursorVisible: true
                    onTextChanged: function(newText) { fahrzeugBackendV2.filterText = newText }
                    onActiveFocusChanged: {
                        if (!activeFocus && text.length === 0) {
                            parent.suchfeldAktiv = false;
                        }
                    }
                }
            }
            
            // Refresh-Button
            Rectangle {
                Layout.preferredWidth: 64
                height: 64
                radius: Style.radiusNormal
                color: "transparent"
                border.color: "#333333"
                border.width: 1
                
                MouseArea {
                    id: refreshArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: fahrzeugBackendV2.refreshData()
                    
                    Text {
                        anchors.centerIn: parent
                        text: "↻"
                        font.pixelSize: 24
                        color: refreshArea.containsMouse ? "#ff8c00" : "#cccccc"
                    }
                }
            }
        }

        // Tabelle mit erweiterten Spalten
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: Style.radiusNormal
            color: "transparent"
            border.color: "#333333"
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                
                // Tabellen-Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    Text { 
                        text: "Kennzeichen"; 
                        font.bold: true; 
                        color: "#b0b0b0"; 
                        font.family: ubuntuFont.name; 
                        font.pixelSize: 16; 
                        Layout.preferredWidth: 120; 
                        horizontalAlignment: Text.AlignLeft 
                    }
                    Text { 
                        text: "Referenz"; 
                        font.bold: true; 
                        color: "#b0b0b0"; 
                        font.family: ubuntuFont.name; 
                        font.pixelSize: 16; 
                        Layout.preferredWidth: 120; 
                        horizontalAlignment: Text.AlignLeft 
                    }
                    Text { 
                        text: "Modell"; 
                        font.bold: true; 
                        color: "#b0b0b0"; 
                        font.family: ubuntuFont.name; 
                        font.pixelSize: 16; 
                        Layout.preferredWidth: 150; 
                        horizontalAlignment: Text.AlignLeft 
                    }
                    Text { 
                        text: "Baujahr"; 
                        font.bold: true; 
                        color: "#b0b0b0"; 
                        font.family: ubuntuFont.name; 
                        font.pixelSize: 16; 
                        Layout.preferredWidth: 80; 
                        horizontalAlignment: Text.AlignLeft 
                    }
                    Text { 
                        text: "Versicherung"; 
                        font.bold: true; 
                        color: "#b0b0b0"; 
                        font.family: ubuntuFont.name; 
                        font.pixelSize: 16; 
                        Layout.preferredWidth: 120; 
                        horizontalAlignment: Text.AlignRight 
                    }
                    Text { 
                        text: "Finanzierung"; 
                        font.bold: true; 
                        color: "#b0b0b0"; 
                        font.family: ubuntuFont.name; 
                        font.pixelSize: 16; 
                        Layout.preferredWidth: 120; 
                        horizontalAlignment: Text.AlignRight 
                    }
                    Text { 
                        text: "Status"; 
                        font.bold: true; 
                        color: "#b0b0b0"; 
                        font.family: ubuntuFont.name; 
                        font.pixelSize: 16; 
                        Layout.preferredWidth: 100; 
                        horizontalAlignment: Text.AlignCenter 
                    }
                    Item { Layout.fillWidth: true }
                }
                
                // Trennlinie
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#333333"
                }
                
                // Fahrzeug-Liste
                ListView {
                    id: fahrzeugListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: fahrzeugBackendV2.fahrzeugList
                    spacing: 4
                    clip: true
                    
                    delegate: Rectangle {
                        width: fahrzeugListView.width
                        height: 50
                        property bool hovered: false
                        color: hovered ? "#1a1a1a" : "transparent"
                        radius: Style.radiusNormal
                        border.color: hovered ? "#ff8c00" : "transparent"
                        border.width: 1
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: parent.hovered = true
                            onExited: parent.hovered = false
                            onClicked: fahrzeugBackendV2.selectVehicle(modelData.kennzeichen)
                            onDoubleClicked: fahrzeugBackendV2.editVehicleWizard_by_id(modelData.kennzeichen)
                        }
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 16
                            
                            Text {
                                text: modelData.kennzeichen || ""
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 18 : 16
                                Layout.preferredWidth: 120
                                horizontalAlignment: Text.AlignLeft
                                elide: Text.ElideRight
                            }
                            
                            Text {
                                text: modelData.rfrnc || ""
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 18 : 16
                                Layout.preferredWidth: 120
                                horizontalAlignment: Text.AlignLeft
                                elide: Text.ElideRight
                            }
                            
                            Text {
                                text: modelData.modell || ""
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 18 : 16
                                Layout.preferredWidth: 150
                                horizontalAlignment: Text.AlignLeft
                                elide: Text.ElideRight
                            }
                            
                            Text {
                                text: modelData.baujahr || ""
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 18 : 16
                                Layout.preferredWidth: 80
                                horizontalAlignment: Text.AlignLeft
                            }
                            
                            Text {
                                text: modelData.versicherung ? modelData.versicherung + " €" : ""
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 18 : 16
                                Layout.preferredWidth: 120
                                horizontalAlignment: Text.AlignRight
                            }
                            
                            Text {
                                text: modelData.finanzierung ? modelData.finanzierung + " €" : ""
                                color: "white"
                                font.family: ubuntuFont.name
                                font.pixelSize: hovered ? 18 : 16
                                Layout.preferredWidth: 120
                                horizontalAlignment: Text.AlignRight
                            }
                            
                            // Status-Badge
                            Rectangle {
                                Layout.preferredWidth: 100
                                height: 24
                                radius: 12
                                color: {
                                    if (modelData.status === "Aktiv") return "#2a5a2a"
                                    else if (modelData.status === "Wartung") return "#5a5a2a"
                                    else return "#5a2a2a"
                                }
                                border.color: "#333333"
                                border.width: 1
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.status || "Aktiv"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: 12
                                    color: "white"
                                    horizontalAlignment: Text.AlignCenter
                                }
                            }
                            
                            Item { Layout.fillWidth: true }
                        }
                    }
                }
            }
        }
    }
    
    // BottomBar mit erweiterten Aktionen
    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
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
        
        // Add-Button
        MouseArea {
            id: addArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: fahrzeugBackendV2.showVehicleWizard()
            Image {
                anchors.centerIn: parent
                source: addArea.pressed ? "assets/icons/add_gray.svg"
                    : addArea.containsMouse ? "assets/icons/add_orange.svg" : "assets/icons/add_white.svg"
                width: addArea.pressed ? 40 : addArea.containsMouse ? 48 : 40
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        
        // Edit-Button
        MouseArea {
            id: editArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: fahrzeugBackendV2.editVehicleWizard()
            Image {
                anchors.centerIn: parent
                source: editArea.pressed ? "assets/icons/edit_gray.svg"
                    : editArea.containsMouse ? "assets/icons/edit_orange.svg" : "assets/icons/edit_white.svg"
                width: editArea.pressed ? 32 : editArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        
        // Delete-Button (neu)
        MouseArea {
            id: deleteArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                if (fahrzeugBackendV2.selectedVehicle) {
                    fahrzeugBackendV2.deleteVehicle(fahrzeugBackendV2.selectedVehicle.kennzeichen)
                }
            }
            Image {
                anchors.centerIn: parent
                source: deleteArea.pressed ? "assets/icons/close_gray.svg"
                    : deleteArea.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_white.svg"
                width: deleteArea.pressed ? 32 : deleteArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
    }
} 