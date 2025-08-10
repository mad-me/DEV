import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: mainWindow
    width: 1400
    height: 900
    visible: true
    title: "Test MitarbeiterSeiteV2Cards"
    color: "#050505"

    // Font-Definition
    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
    }

    // Style-Definitionen
    QtObject {
        id: style
        property color background: "#050505"
        property int radiusNormal: 8
        property int spacingHuge: 32
        property int spacingLarge: 16
    }

    // Vollständige MitarbeiterSeiteV2Cards
    Rectangle {
        id: root
        anchors.fill: parent
        property var goHome: function() {
            console.log("Home-Button geklickt - Test-Umgebung")
        }
        color: Style.background
        radius: Style.radiusNormal

        // Home-Button (außerhalb des Headers, links)
        MouseArea {
            id: homeButton
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 48
            width: 60
            height: 60
            hoverEnabled: true
            onClicked: {
                if (typeof root.goHome === "function") {
                    root.goHome();
                } else {
                    console.warn("goHome ist nicht definiert oder keine Funktion!");
                }
            }
            cursorShape: Qt.PointingHandCursor
            
                         Image {
                 anchors.centerIn: parent
                 source: homeButton.containsMouse ? "assets/icons/home_orange.svg" : "assets/icons/home_gray.svg"
                 width: homeButton.containsMouse ? 44 : 40
                 height: width
                 fillMode: Image.PreserveAspectFit
                 
                 Behavior on width {
                     NumberAnimation { duration: 150; easing.type: Easing.OutQuad }
                 }
             }
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
                
                // Klickbarer Titel für Ansichtswechsel
                Rectangle {
                    Layout.fillWidth: true
                    height: 50
                    color: "transparent"
                    
                    MouseArea {
                        id: titleMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (typeof mitarbeiterBackendV2.toggleViewMode === "function") {
                                mitarbeiterBackendV2.toggleViewMode()
                            } else {
                                console.log("Titel geklickt - Ansichtswechsel")
                            }
                        }
                    }
                    
                    Text {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        text: mitarbeiterBackendV2 && mitarbeiterBackendV2.toggleView ? "Erweiterte Details" : "Mitarbeiterverwaltung"
                        font.pixelSize: 36
                        font.bold: true
                        color: titleMouseArea.containsMouse ? "#ff8c00" : "white"
                        
                        scale: titleMouseArea.containsMouse ? 1.05 : 1.0
                        
                        Behavior on scale {
                            NumberAnimation { duration: 150 }
                        }
                        
                        Behavior on color {
                            ColorAnimation { duration: 150 }
                        }
                    }
                }
                
                // Toggle Switch (nur in normaler Ansicht)
                Rectangle {
                    Layout.preferredWidth: 50
                    height: 50
                    radius: Style.radiusNormal
                    color: "transparent"
                    border.width: 0
                    visible: !mitarbeiterBackendV2 || !mitarbeiterBackendV2.toggleView
                    
                    // Toggle Switch Background
                    Rectangle {
                        width: 40
                        height: 20
                        radius: 10
                        color: mitarbeiterBackendV2 && mitarbeiterBackendV2.showOnlyActive ? "#ff8c00" : "#555555"
                        anchors.centerIn: parent
                        
                        // Toggle Knob
                        Rectangle {
                            id: toggleKnob
                            width: 16
                            height: 16
                            radius: 8
                            color: "white"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.leftMargin: mitarbeiterBackendV2 && mitarbeiterBackendV2.showOnlyActive ? 20 : 2
                            
                            Behavior on anchors.leftMargin {
                                NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
                            }
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (mitarbeiterBackendV2) {
                                mitarbeiterBackendV2.showOnlyActive = !mitarbeiterBackendV2.showOnlyActive
                            } else {
                                console.log("Toggle Switch geklickt")
                            }
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
                    border.color: "transparent"
                    border.width: 0
                   
                    property bool suchfeldAktiv: false
                    property bool iconHovered: false
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: !parent.suchfeldAktiv
                        onEntered: parent.iconHovered = true
                        onExited: parent.iconHovered = false
                        onClicked: {
                            console.log("Suchleiste aktiviert")
                            parent.suchfeldAktiv = true;
                            suchfeld.forceActiveFocus();
                        }
                    }
                    
                                         Image {
                         id: suchIcon
                         anchors.verticalCenter: parent.verticalCenter
                         anchors.horizontalCenter: parent.horizontalCenter
                         anchors.horizontalCenterOffset: 9
                         source: parent.iconHovered ? "assets/icons/person_search_orange.svg" : "assets/icons/person_search_gray.svg"
                         width: parent.iconHovered ? 32 : 24
                         height: parent.iconHovered ? 32 : 24
                         fillMode: Image.PreserveAspectFit
                         visible: !parent.suchfeldAktiv
                         opacity: 0.8
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
            color: "white"
                        background: null
                        padding: 32
                        horizontalAlignment: TextInput.AlignHCenter
                        verticalAlignment: TextInput.AlignVCenter
                        placeholderText: "Mitarbeiter suchen..."
                        selectionColor: "#a2ffb5"
                        selectedTextColor: "#232323"
                        visible: parent.suchfeldAktiv
                        cursorVisible: true
                        onTextChanged: {
                            console.log("Suchtext geändert:", text)
                            if (mitarbeiterBackendV2) {
                                mitarbeiterBackendV2.filterText = text
                            }
                        }
                        onActiveFocusChanged: {
                            if (!activeFocus && text.length === 0) {
                                parent.suchfeldAktiv = false;
                            }
                        }
                        Keys.onEscapePressed: {
                            text = ""
                            parent.suchfeldAktiv = false
                            focus = false
                        }
                    }
                }
            }

            // Cards-Container mit echtem Grid-Layout
            GridView {
                id: cardsGridView
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                
                // Performance-Optimierungen für Virtual Scrolling
                cacheBuffer: 2000  // Erhöht für bessere Performance
                maximumFlickVelocity: 3000  // Erhöht für flüssigere Scrolling
                boundsBehavior: Flickable.StopAtBounds
                flickDeceleration: 1500  // Schnelleres Abbremsen
                
                // Lazy Loading für große Listen
                property bool isLoadingMore: false
                property int currentPage: 0
                
                // Automatisches Laden der nächsten Seite
                onAtYEndChanged: {
                    if (atYEnd && !isLoadingMore && mitarbeiterBackendV2) {
                        isLoadingMore = true
                        mitarbeiterBackendV2.loadNextPage()
                        isLoadingMore = false
                    }
                }
                
                // Responsive Grid-Eigenschaften
                cellWidth: 396
                cellHeight: 296
                
                // Automatische Spaltenberechnung
                onWidthChanged: {
                    var availableWidth = width - 16
                    var cardsPerRow = Math.max(1, Math.floor(availableWidth / 396))
                    cellWidth = availableWidth / cardsPerRow
                }
                
                // Mitarbeiter-Cards (Backend-Daten oder Test-Daten)
                model: mitarbeiterBackendV2 ? mitarbeiterBackendV2.mitarbeiterList : []
                
                // Loading-Indikator
                Rectangle {
                    id: loadingIndicator
                    anchors.centerIn: parent
                    width: 200
                    height: 60
                    radius: Style.radiusNormal
                    color: "#1a1a1a"
                    border.color: "#333333"
                    border.width: 1
                    visible: mitarbeiterBackendV2 && mitarbeiterBackendV2.isLoading
                    z: 100
                    
                    RowLayout {
                        anchors.centerIn: parent
                        spacing: 12
                        
                        // Spinner-Animation
                        Rectangle {
                            width: 20
                            height: 20
                            radius: 10
                            color: "#ff8c00"
                            
                            RotationAnimation on rotation {
                                from: 0
                                to: 360
                                duration: 1000
                                loops: Animation.Infinite
                            }
                        }
                        
                        Text {
                            text: "Mitarbeiter werden geladen..."
                            font.pixelSize: 14
                            color: "#cccccc"
                        }
                    }
                }
                
                delegate: Rectangle {
                    id: employeeCard
                    width: 380
                    height: 280
                    radius: Style.radiusNormal
                    color: "transparent"
                    border.width: 0
                    z: 1
                    
                    // Performance-Optimierung: Nur bei Bedarf rendern
                    property bool isVisible: true
                    property bool isHovered: false
                    
                    // Optimierter Hover-Effekt: Vergrößerung um 1.05x
                    property real hoverScale: isHovered ? 1.05 : 1.0
                    
                    // Nur rendern wenn sichtbar
                    visible: isVisible
                    
                    // Transform mit Zentrierung
                    transform: Scale {
                        xScale: employeeCard.hoverScale
                        yScale: employeeCard.hoverScale
                        origin.x: employeeCard.width / 2
                        origin.y: employeeCard.height / 2
                    }
                    
                    // Animation für smooth Übergänge
                    Behavior on hoverScale {
                        NumberAnimation { 
                            duration: 150
                            easing.type: Easing.OutCubic
                        }
                    }
                
                    // Gradient-Hintergrund
                    Rectangle {
                        anchors.fill: parent
                        radius: Style.radiusNormal
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "#050505" }
                            GradientStop { position: 0.8; color: "#050505" }
                            GradientStop { position: 1.0; color: "#1a1a1a" }
                        }
                        z: -1
                    }
                    
                    MouseArea {
                        id: employeeCardMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        
                        // Optimierte Hover-Detection
                        onEntered: {
                            employeeCard.isHovered = true
                        }
                        onExited: {
                            employeeCard.isHovered = false
                        }
                        
                        onClicked: {
                            if (mitarbeiterBackendV2) {
                                mitarbeiterBackendV2.selectEmployee(model.driver_id)
                            } else {
                                console.log("Mitarbeiter geklickt:", modelData.first_name + " " + modelData.last_name)
                            }
                        }
                        onDoubleClicked: {
                            console.log("Doppelklick auf Mitarbeiter:", modelData.first_name + " " + modelData.last_name)
                        }
                    }
                    
                    // Card-Inhalt
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12
                        
                        // Header mit Name und Status
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12
                            
                            // Name in zwei Zeilen
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                
                                                                 Text {
                                     text: {
                                         if (mitarbeiterBackendV2) {
                                             return modelData.last_name || ""
                                         } else {
                                             return modelData.lastName || ""
                                         }
                                     }
                                     font.pixelSize: 18
                                     color: "#cccccc"
                                     Layout.fillWidth: true
                                 }
                                 
                                 Text {
                                     text: {
                                         if (mitarbeiterBackendV2) {
                                             return modelData.first_name || ""
                                         } else {
                                             return modelData.firstName || ""
                                         }
                                     }
                                     font.pixelSize: 20
                                     font.bold: true
                                     color: "white"
                                     Layout.fillWidth: true
                                 }
                            }
                            
                            // Status-Badge (klickbar)
                            Rectangle {
                                Layout.preferredWidth: 80
                                height: 28
                                radius: 14
                                color: "transparent"
                                border.width: 0
                                visible: !mitarbeiterBackendV2 || !mitarbeiterBackendV2.toggleView
                                
                                MouseArea {
                                    id: statusBadgeMouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        if (mitarbeiterBackendV2) {
                                            // Status-Toggle: active → suspended → inactive → active
                                            var currentStatus = modelData.status || "active"
                                            var newStatus
                                            if (currentStatus === "active") newStatus = "suspended"
                                            else if (currentStatus === "suspended") newStatus = "inactive"
                                            else newStatus = "active"
                                            
                                            mitarbeiterBackendV2.updateStatusById(modelData.driver_id, newStatus)
                                        } else {
                                            console.log("Status-Badge geklickt für:", modelData.first_name + " " + modelData.last_name)
                                        }
                                    }
                                }
                                
                                Text {
                                    anchors.centerIn: parent
                                                                    text: modelData.status || "active"
                                    font.pixelSize: 12
                                                                    color: {
                                    var status = modelData.status || "active"
                                    if (status === "active") return "#4CAF50"  // Grün
                                    else if (status === "suspended") return "#F44336"  // Rot
                                    else return "#9E9E9E"  // Grau (inactive)
                                }
                                    horizontalAlignment: Text.AlignCenter
                                }
                            }
                        }
                        
                        // Mitarbeiter-Details (Kompakte Ansicht)
                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: 2
                            rowSpacing: 8
                            columnSpacing: 16
                            visible: !mitarbeiterBackendV2 || !mitarbeiterBackendV2.toggleView
                            
                            // ID
                            Text {
                                text: "ID:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: mitarbeiterBackendV2 ? (modelData.driver_id || "-") : (modelData.id || "-")
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            // Deal-Typ
                            Text {
                                text: "Deal:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: mitarbeiterBackendV2 ? (modelData.deal || "-") : "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            

                            
                            // Pauschale (nur bei P-Deal)
                            Text {
                                text: "Pauschale:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: mitarbeiterBackendV2 && modelData.deal === "P"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: mitarbeiterBackendV2 && modelData.deal === "P" ? (modelData.pauschale || "-") : "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: mitarbeiterBackendV2 && modelData.deal === "P"
                            }
                        }
                        
                        // Erweiterte Details (Toggle-Ansicht)
                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: 2
                            rowSpacing: 8
                            columnSpacing: 16
                            visible: mitarbeiterBackendV2 && mitarbeiterBackendV2.toggleView
                            
                            // Telefon
                            Text {
                                text: "Telefon:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: mitarbeiterBackendV2 ? (modelData.phone || "-") : (modelData.phone || "-")
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            // Email
                            Text {
                                text: "Email:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: mitarbeiterBackendV2 ? (modelData.email || "-") : (modelData.email || "-")
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            // Einstellungsdatum
                            Text {
                                text: "Einstellungsdatum:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: mitarbeiterBackendV2 ? (modelData.hire_date || "-") : "01.01.2024"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            // Umsatzgrenze (nur bei P-Deal)
                            Text {
                                text: "Umsatzgrenze:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: mitarbeiterBackendV2 && modelData.deal === "P"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: mitarbeiterBackendV2 && modelData.deal === "P" ? (modelData.umsatzgrenze || "-") : "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: mitarbeiterBackendV2 && modelData.deal === "P"
                            }
                            
                            // Garage
                            Text {
                                text: "Garage:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: mitarbeiterBackendV2 ? (modelData.garage || "-") : "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        
                        // Aktions-Buttons (rechts)
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            
                            // Spacer um Buttons nach rechts zu schieben
                            Item {
                                Layout.fillWidth: true
                            }
                            
                            // Edit/Check-Button
                            Rectangle {
                                Layout.preferredWidth: 32
                                height: 32
                                radius: 16
                                color: "transparent"
                                border.width: 0
                                
                                MouseArea {
                                    id: editButtonMouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        if (mitarbeiterBackendV2) {
                                            // Mitarbeiter-Daten für das Formular sammeln
                                            var mitarbeiterData = {
                                                driver_id: modelData.driver_id,
                                                original_driver_id: modelData.driver_id,  // Für Update-Logik
                                                driver_license_number: modelData.driver_license_number,
                                                first_name: modelData.first_name,
                                                last_name: modelData.last_name,
                                                phone: modelData.phone,
                                                email: modelData.email,
                                                hire_date: modelData.hire_date,
                                                status: modelData.status
                                            }
                                            showMitarbeiterFormOverlayForEdit(mitarbeiterData)
                                        } else {
                                            console.log("Edit-Button geklickt für:", modelData.first_name + " " + modelData.last_name)
                                        }
                                    }
                                    
                                                                         Image {
                                         anchors.centerIn: parent
                                         source: parent.containsMouse ? "assets/icons/edit_orange.svg" : "assets/icons/edit_white.svg"
                                         width: parent.containsMouse ? 20 : 16
                                         height: width
                                         fillMode: Image.PreserveAspectFit
                                     }
                                }
                            }
                            
                            // Deal-Button
                            Rectangle {
                                Layout.preferredWidth: 32
                                height: 32
                                radius: 16
                                color: "transparent"
                                border.width: 0
                                
                                MouseArea {
                                    id: dealButtonMouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        if (mitarbeiterBackendV2) {
                                            console.log("Deal-Button geklickt für:", modelData.first_name + " " + modelData.last_name + " (ID: " + modelData.driver_id + ")")
                                            showDealFormOverlay(modelData.driver_id, modelData.first_name + " " + modelData.last_name)
                                        } else {
                                            console.log("Deal-Button geklickt für:", modelData.first_name + " " + modelData.last_name)
                                        }
                                    }
                                    
                                    Image {
                                        anchors.centerIn: parent
                                        source: parent.containsMouse ? "assets/icons/deal_orange.svg" : "assets/icons/deal_white.svg"
                                        width: parent.containsMouse ? 20 : 16
                                        height: width
                                        fillMode: Image.PreserveAspectFit
                                    }
                                }
                            }
                            
                            // Delete-Button
                            Rectangle {
                                Layout.preferredWidth: 32
                                height: 32
                                radius: 16
                                color: "transparent"
                                border.width: 0
                                
                                MouseArea {
                                    id: deleteButtonMouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        if (mitarbeiterBackendV2) {
                                            mitarbeiterBackendV2.deleteEmployeeWithConfirmation(modelData.driver_id)
                                        } else {
                                            console.log("Delete-Button geklickt für:", modelData.first_name + " " + modelData.last_name)
                                        }
                                    }
                                    
                                    Image {
                                        anchors.centerIn: parent
                                        source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_white.svg"
                                        width: parent.containsMouse ? 20 : 16
                                        height: width
                                        fillMode: Image.PreserveAspectFit
                                    }
                                }
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
            
            // Add-Button
            MouseArea {
                id: addArea
                width: 56; height: 56
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true
                onClicked: {
                    if (mitarbeiterBackendV2) {
                        showMitarbeiterFormOverlay()
                    } else {
                        console.log("Add-Button geklickt")
                    }
                }
                
                                 Image {
                     anchors.centerIn: parent
                     source: addArea.pressed ? "assets/icons/add_gray.svg"
                         : addArea.containsMouse ? "assets/icons/add_orange.svg" : "assets/icons/add_white.svg"
                     width: addArea.pressed ? 40 : addArea.containsMouse ? 48 : 40
                     height: width
                     fillMode: Image.PreserveAspectFit
                     
                     Behavior on width {
                         NumberAnimation { duration: 150 }
                     }
                 }
            }
        }
    }
    
    // Funktionen für das Mitarbeiter-Formular
    function showMitarbeiterFormOverlay() {
        // Felder zurücksetzen
        driverIdField.text = ""
        licenseNumberField.text = ""
        firstNameField.text = ""
        lastNameField.text = ""
        phoneField.text = ""
        emailField.text = ""
        // Heutiges Datum als Voreinstellung für Einstellungsdatum
        var today = new Date()
        var year = today.getFullYear()
        var month = String(today.getMonth() + 1).padStart(2, '0')
        var day = String(today.getDate()).padStart(2, '0')
        hireDateField.text = year + "-" + month + "-" + day
        statusField = "active"
        
        // Original Driver ID zurücksetzen (für neue Mitarbeiter)
        originalDriverId = ""
        
        // Validierung zurücksetzen
        isDriverIdValid = false
        isLicenseNumberValid = false
        isFirstNameValid = false
        isLastNameValid = false
        isEmailValid = false
        isPhoneValid = false
        isDateValid = false
        
        driverIdError = ""
        licenseNumberError = ""
        firstNameError = ""
        lastNameError = ""
        emailError = ""
        phoneError = ""
        dateError = ""
        
        // Titel setzen
        mitarbeiterFormTitle.text = "Neuen Mitarbeiter anlegen"
        
        mitarbeiterFormOverlay.visible = true
        mitarbeiterFormOverlay.forceActiveFocus()
    }
    
    // Globale Variable für original_driver_id
    property string originalDriverId: ""
    
    // Globale Variable für Delete-Bestätigung
    property var deleteEmployeeData: null
    
    // Global Properties für Duplikat-Dialog
    property var duplicateDialogData: null
    
    // Global Properties für Deal-Formular
    property int currentDealDriverId: -1
    property string currentDealEmployeeName: ""
    property string dealTypeField: "P"  // Standard Deal-Typ
    
    // Global Property für Status-Feld
    property string statusField: "active"  // Standard Status
    
    // Validierungs-Properties
    property bool isDriverIdValid: false
    property bool isLicenseNumberValid: false
    property bool isFirstNameValid: false
    property bool isLastNameValid: false
    property bool isEmailValid: false  // Default false für neutrale Anzeige
    property bool isPhoneValid: false  // Default false für neutrale Anzeige
    property bool isDateValid: false   // Default false für neutrale Anzeige
    
    // Validierungs-Nachrichten
    property string driverIdError: ""
    property string licenseNumberError: ""
    property string firstNameError: ""
    property string lastNameError: ""
    property string emailError: ""
    property string phoneError: ""
    property string dateError: ""
    
    // Validierungs-Funktionen
    function validateDriverId(text) {
        var trimmedText = text.trim()
        if (!trimmedText) {
            isDriverIdValid = false
            driverIdError = ""
            return false
        }
        if (!/^\d+$/.test(trimmedText)) {
            isDriverIdValid = false
            driverIdError = "Driver ID darf nur Ziffern enthalten"
            return false
        }
        isDriverIdValid = true
        driverIdError = ""
        return true
    }
    
    function validateLicenseNumber(text) {
        var trimmedText = text.trim()
        if (!trimmedText) {
            isLicenseNumberValid = false
            licenseNumberError = ""
            return false
        }
        if (trimmedText.length < 5) {
            isLicenseNumberValid = false
            licenseNumberError = "Führerscheinnummer muss mindestens 5 Zeichen haben"
            return false
        }
        if (!/^[A-Z0-9]+$/.test(trimmedText)) {
            isLicenseNumberValid = false
            licenseNumberError = "Führerscheinnummer darf nur Großbuchstaben und Zahlen enthalten"
            return false
        }
        isLicenseNumberValid = true
        licenseNumberError = ""
        return true
    }
    
    function validateFirstName(text) {
        var trimmedText = text.trim()
        if (!trimmedText) {
            isFirstNameValid = false
            firstNameError = ""
            return false
        }
        if (trimmedText.length < 2) {
            isFirstNameValid = false
            firstNameError = "Vorname muss mindestens 2 Zeichen haben"
            return false
        }
        if (!/^[A-Za-zÄäÖöÜüß\s]+$/.test(trimmedText)) {
            isFirstNameValid = false
            firstNameError = "Vorname darf nur Buchstaben enthalten"
            return false
        }
        isFirstNameValid = true
        firstNameError = ""
        return true
    }
    
    function validateLastName(text) {
        var trimmedText = text.trim()
        if (!trimmedText) {
            isLastNameValid = false
            lastNameError = ""
            return false
        }
        if (trimmedText.length < 2) {
            isLastNameValid = false
            lastNameError = "Nachname muss mindestens 2 Zeichen haben"
            return false
        }
        if (!/^[A-Za-zÄäÖöÜüß\s]+$/.test(trimmedText)) {
            isLastNameValid = false
            lastNameError = "Nachname darf nur Buchstaben enthalten"
            return false
        }
        isLastNameValid = true
        lastNameError = ""
        return true
    }
    
    function validateEmail(text) {
        var trimmedText = text.trim()
        if (!trimmedText) {
            isEmailValid = false  // Neutral für leere Felder
            emailError = ""
            return true  // Email ist optional
        }
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(trimmedText)) {
            isEmailValid = false
            emailError = "Ungültiges Email-Format"
            return false
        }
        isEmailValid = true
        emailError = ""
        return true
    }
    
    function validatePhone(text) {
        var trimmedText = text.trim()
        if (!trimmedText) {
            isPhoneValid = false  // Neutral für leere Felder
            phoneError = ""
            return true  // Telefon ist optional
        }
        var phoneRegex = /^[\+]?[0-9\s\-\(\)]+$/
        if (!phoneRegex.test(trimmedText)) {
            isPhoneValid = false
            phoneError = "Ungültiges Telefon-Format"
            return false
        }
        if (trimmedText.length < 10) {
            isPhoneValid = false
            phoneError = "Telefonnummer muss mindestens 10 Zeichen haben"
            return false
        }
        isPhoneValid = true
        phoneError = ""
        return true
    }
    
    function validateDate(text) {
        var trimmedText = text.trim()
        if (!trimmedText) {
            isDateValid = false  // Neutral für leere Felder
            dateError = ""
            return true  // Datum ist optional
        }
        var dateRegex = /^\d{4}-\d{2}-\d{2}$/
        if (!dateRegex.test(trimmedText)) {
            isDateValid = false
            dateError = "Datum muss im Format YYYY-MM-DD sein"
            return false
        }
        var date = new Date(trimmedText)
        if (isNaN(date.getTime())) {
            isDateValid = false
            dateError = "Ungültiges Datum"
            return false
        }
        isDateValid = true
        dateError = ""
        return true
    }
    
    function validateAllFields() {
        var driverIdOk = validateDriverId(driverIdField.text)
        var licenseOk = validateLicenseNumber(licenseNumberField.text)
        var firstNameOk = validateFirstName(firstNameField.text)
        var lastNameOk = validateLastName(lastNameField.text)
        var emailOk = validateEmail(emailField.text)
        var phoneOk = validatePhone(phoneField.text)
        var dateOk = validateDate(hireDateField.text)
        
        return driverIdOk && licenseOk && firstNameOk && lastNameOk && emailOk && phoneOk && dateOk
    }
    
    // Computed Property für Speichern-Button Status
    property bool canSave: {
        // Erforderliche Felder müssen ausgefüllt und gültig sein
        var driverIdFilled = driverIdField.text.trim() !== ""
        var licenseFilled = licenseNumberField.text.trim() !== ""
        var firstNameFilled = firstNameField.text.trim() !== ""
        var lastNameFilled = lastNameField.text.trim() !== ""
        
        // Alle Validierungen müssen erfolgreich sein
        var allValid = validateAllFields()
        
        return driverIdFilled && licenseFilled && firstNameFilled && lastNameFilled && allValid
    }
    
    // Funktion zum Anzeigen des Mitarbeiter-Formular-Overlays im Edit-Modus
    function showMitarbeiterFormOverlayForEdit(mitarbeiterData) {
        // Original Driver ID speichern (verwende original_driver_id falls vorhanden)
        originalDriverId = mitarbeiterData.original_driver_id || mitarbeiterData.driver_id || ""
        
        // Felder mit Mitarbeiterdaten vorausfüllen
        driverIdField.text = mitarbeiterData.driver_id || ""
        licenseNumberField.text = mitarbeiterData.driver_license_number || ""
        firstNameField.text = mitarbeiterData.first_name || ""
        lastNameField.text = mitarbeiterData.last_name || ""
        phoneField.text = mitarbeiterData.phone || ""
        emailField.text = mitarbeiterData.email || ""
        hireDateField.text = mitarbeiterData.hire_date || ""
        
        // Status setzen
        statusField = mitarbeiterData.status || "active"
        
        // Titel ändern
        mitarbeiterFormTitle.text = "Mitarbeiter bearbeiten: " + mitarbeiterData.first_name + " " + mitarbeiterData.last_name
        
        mitarbeiterFormOverlay.visible = true
        mitarbeiterFormOverlay.forceActiveFocus()
    }
    
    // Funktion zum Anzeigen des Deal-Formular-Overlays
    function showDealFormOverlay(driverId, employeeName) {
        currentDealDriverId = driverId
        currentDealEmployeeName = employeeName
        
        // Titel setzen
        dealFormTitle.text = employeeName
        
        // Bestehende Deal-Daten laden
        if (mitarbeiterBackendV2) {
            console.log("Lade Deal-Daten für:", employeeName)
            
            // Lade bestehende Deal-Daten aus der Datenbank
            var dealData = mitarbeiterBackendV2.getDealByDriverId(driverId)
            console.log("Rohe Deal-Daten vom Backend:", dealData)
            
            if (dealData && typeof dealData === 'object' && dealData.hasOwnProperty('deal_type')) {
                try {
                    // Sichere Zuweisung mit Fallback-Werten
                    dealTypeField = (dealData.deal_type && dealData.deal_type !== "") ? dealData.deal_type : "P"
                    pauschaleField.text = (dealData.pauschale && dealData.pauschale !== "") ? dealData.pauschale : ""
                    umsatzgrenzeField.text = (dealData.umsatzgrenze && dealData.umsatzgrenze !== "") ? dealData.umsatzgrenze : ""
                    garageField.text = (dealData.garage && dealData.garage !== "") ? dealData.garage : ""
                    console.log("Deal-Daten erfolgreich geladen und zugewiesen")
                } catch (error) {
                    console.error("Fehler beim Verarbeiten der Deal-Daten:", error)
                    // Fallback: Standard-Deal
                    dealTypeField = "P"
                    pauschaleField.text = ""
                    umsatzgrenzeField.text = ""
                    garageField.text = ""
                }
            } else {
                // Fallback: Standard-Deal
                dealTypeField = "P"
                pauschaleField.text = ""
                umsatzgrenzeField.text = ""
                garageField.text = ""
                console.log("Keine gültigen Deal-Daten gefunden, verwende Standard")
            }
        }
        
        dealFormOverlay.visible = true
        dealFormOverlay.forceActiveFocus()
    }
    
    // Overlay für Mitarbeiter-Formular
    Rectangle {
        id: mitarbeiterFormOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 2000
        
        MouseArea {
            anchors.fill: parent
            onClicked: mitarbeiterFormOverlay.visible = false
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(parent.width * 0.5, 500)
            height: Math.min(parent.height * 0.8, 600)
            color: "#1a1a1a"
            border.color: "#333333"
            border.width: 1
            radius: 8
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                // Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    Text {
                        id: mitarbeiterFormTitle
                        text: "Neuen Mitarbeiter anlegen"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        font.bold: true
                        color: "white"
                        Layout.fillWidth: true
                        visible: !text.includes("bearbeiten")
                    }
                }
                
                // Abstand zwischen Titel und Formular
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 20
                }
                
                // Formular
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    GridLayout {
                        width: parent.width
                        anchors.horizontalCenter: parent.horizontalCenter
                        columns: 2
                        rowSpacing: 20
                        columnSpacing: 20
                        
                        // Driver ID
                        Text {
                            text: "Driver ID"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: driverIdField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: driverIdError ? "#F44336" : isDriverIdValid ? "#4CAF50" : "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. 40100"
                            onTextChanged: {
                                validateDriverId(text)
                                // canSave Property wird automatisch aktualisiert
                            }
                        }
                        
                        // Error-Nachricht für Driver ID
                        Text {
                            text: driverIdError
                            font.family: ubuntuFont.name
                            font.pixelSize: 12
                            color: "#F44336"
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            visible: driverIdError !== ""
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Führerscheinnummer
                        Text {
                            text: "Führerscheinnummer *"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: licenseNumberField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: licenseNumberError ? "#F44336" : isLicenseNumberValid ? "#4CAF50" : "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. B123456789"
                            onTextChanged: {
                                validateLicenseNumber(text)
                                // canSave Property wird automatisch aktualisiert
                            }
                        }
                        
                        // Error-Nachricht für Führerscheinnummer
                        Text {
                            text: licenseNumberError
                            font.family: ubuntuFont.name
                            font.pixelSize: 12
                            color: "#F44336"
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            visible: licenseNumberError !== ""
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Vorname
                        Text {
                            text: "Vorname *"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: firstNameField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: firstNameError ? "#F44336" : isFirstNameValid ? "#4CAF50" : "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. Max"
                            onTextChanged: {
                                validateFirstName(text)
                                // canSave Property wird automatisch aktualisiert
                            }
                        }
                        
                        // Error-Nachricht für Vorname
                        Text {
                            text: firstNameError
                            font.family: ubuntuFont.name
                            font.pixelSize: 12
                            color: "#F44336"
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            visible: firstNameError !== ""
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Nachname
                        Text {
                            text: "Nachname *"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: lastNameField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: lastNameError ? "#F44336" : isLastNameValid ? "#4CAF50" : "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. Mustermann"
                            onTextChanged: {
                                validateLastName(text)
                                // canSave Property wird automatisch aktualisiert
                            }
                        }
                        
                        // Error-Nachricht für Nachname
                        Text {
                            text: lastNameError
                            font.family: ubuntuFont.name
                            font.pixelSize: 12
                            color: "#F44336"
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            visible: lastNameError !== ""
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Telefon
                        Text {
                            text: "Telefon"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: phoneField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: phoneError ? "#F44336" : isPhoneValid ? "#4CAF50" : "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. +49 123 456789"
                            onTextChanged: {
                                validatePhone(text)
                                // canSave Property wird automatisch aktualisiert
                            }
                        }
                        
                        // Error-Nachricht für Telefon
                        Text {
                            text: phoneError
                            font.family: ubuntuFont.name
                            font.pixelSize: 12
                            color: "#F44336"
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            visible: phoneError !== ""
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Email
                        Text {
                            text: "Email"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: emailField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: emailError ? "#F44336" : isEmailValid ? "#4CAF50" : "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. max@example.com"
                            onTextChanged: {
                                validateEmail(text)
                                // canSave Property wird automatisch aktualisiert
                            }
                        }
                        
                        // Error-Nachricht für Email
                        Text {
                            text: emailError
                            font.family: ubuntuFont.name
                            font.pixelSize: 12
                            color: "#F44336"
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            visible: emailError !== ""
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Einstellungsdatum
                        Text {
                            text: "Einstellungsdatum"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: hireDateField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: dateError ? "#F44336" : isDateValid ? "#4CAF50" : "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. 2024-01-15"
                            onTextChanged: {
                                validateDate(text)
                                // canSave Property wird automatisch aktualisiert
                            }
                        }
                        
                        // Error-Nachricht für Datum
                        Text {
                            text: dateError
                            font.family: ubuntuFont.name
                            font.pixelSize: 12
                            color: "#F44336"
                            Layout.fillWidth: true
                            Layout.columnSpan: 2
                            visible: dateError !== ""
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Status
                        Text {
                            text: "Status"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        // Status Toggle Field
                        Rectangle {
                            id: statusToggleField
                            Layout.fillWidth: true
                            height: 48
                            radius: 6
                            color: "#2a2a2a"
                            border.color: "#555555"
                            border.width: 2
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    // Zyklisch zwischen active, suspended, inactive wechseln
                                    if (statusField === "active") {
                                        statusField = "suspended"
                                    } else if (statusField === "suspended") {
                                        statusField = "inactive"
                                    } else {
                                        statusField = "active"
                                    }
                                }
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: statusField
                                font.family: ubuntuFont.name
                                font.pixelSize: 16
                                font.bold: true
                                color: "white"
                            }
                        }
                    }
                }
                
                // Buttons mit Icons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    Item { Layout.fillWidth: true }
                    
                    // Abbrechen-Button mit Close-Icon
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: mitarbeiterFormOverlay.visible = false
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                width: parent.containsMouse ? 32 : 28
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                    
                    // Speichern-Button mit Save-Icon
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: canSave ? Qt.PointingHandCursor : Qt.ArrowCursor
                            enabled: canSave
                            onClicked: {
                                if (!canSave) return
                                
                                // Daten sammeln
                                var mitarbeiterData = {
                                    driver_id: driverIdField.text.trim(),
                                    original_driver_id: originalDriverId,  // Für Update-Logik
                                    driver_license_number: licenseNumberField.text.trim(),
                                    first_name: firstNameField.text.trim(),
                                    last_name: lastNameField.text.trim(),
                                    phone: phoneField.text.trim(),
                                    email: emailField.text.trim(),
                                    hire_date: hireDateField.text.trim(),
                                    status: statusField
                                }
                                
                                // Mitarbeiter speichern (sowohl neue als auch Updates)
                                mitarbeiterBackendV2.saveEmployee(mitarbeiterData)
                                
                                // Overlay schließen
                                mitarbeiterFormOverlay.visible = false
                                
                                // Felder zurücksetzen
                                driverIdField.text = ""
                                licenseNumberField.text = ""
                                firstNameField.text = ""
                                lastNameField.text = ""
                                phoneField.text = ""
                                emailField.text = ""
                                hireDateField.text = ""
                                statusField.currentIndex = 0
                            }
                            
                            Image {
                                anchors.centerIn: parent
                                source: {
                                    if (!canSave) return "assets/icons/save_gray.svg"
                                    return parent.containsMouse ? "assets/icons/save_orange.svg" : "assets/icons/save_white.svg"
                                }
                                width: {
                                    if (!canSave) return 24
                                    return parent.containsMouse ? 32 : 28
                                }
                                height: width
                                fillMode: Image.PreserveAspectFit
                                
                                opacity: canSave ? 1.0 : 0.5
                            }
                        }
                    }
                }
            }
            
            // ESC-Taste zum Schließen
            Keys.onEscapePressed: mitarbeiterFormOverlay.visible = false
        }
    }
    
    // Overlay für Deal-Formular
    Rectangle {
        id: dealFormOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 2000
        
        MouseArea {
            anchors.fill: parent
            onClicked: dealFormOverlay.visible = false
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(parent.width * 0.4, 450)
            height: Math.min(parent.height * 0.6, 400)
            color: "#1a1a1a"
            border.color: "#333333"
            border.width: 1
            radius: 8
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                // Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    Text {
                        id: dealFormTitle
                        text: "Deal bearbeiten"
                        font.family: ubuntuFont.name
                        font.pixelSize: 24
                        font.bold: true
                        color: "white"
                        Layout.fillWidth: true
                    }
                }
                
                // Abstand zwischen Titel und Formular
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 12
                }
                
                // Formular
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    GridLayout {
                        width: parent.width
                        columns: 2
                        rowSpacing: 20
                        columnSpacing: 20
                        
                        // Garage (erste Zeile)
                        Text {
                            text: "Garage (€)"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            Layout.preferredWidth: 120
                        }
                        
                        TextField {
                            id: garageField
                            Layout.preferredWidth: 200
                            height: 40
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. 50.00"
                            inputMethodHints: Qt.ImhFormattedNumbersOnly
                            padding: 8
                        }
                        
                        // Deal-Typ (zweite Zeile)
                        Text {
                            text: "Deal-Typ *"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            Layout.preferredWidth: 120
                        }
                        
                        // Deal-Typ Toggle Field
                        Rectangle {
                            id: dealTypeToggleField
                            Layout.preferredWidth: 200
                            height: 40
                            radius: 6
                            color: "#2a2a2a"
                            border.color: "#555555"
                            border.width: 2
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    // Zyklisch zwischen P, %, C wechseln
                                    if (dealTypeField === "P") {
                                        dealTypeField = "%"
                                        // Bei %-Deal Pauschale und Umsatzgrenze ausblenden
                                        pauschaleField.visible = false
                                        umsatzgrenzeField.visible = false
                                        pauschaleLabel.visible = false
                                        umsatzgrenzeLabel.visible = false
                                    } else if (dealTypeField === "%") {
                                        dealTypeField = "C"
                                        // Bei C-Deal Pauschale und Umsatzgrenze ausblenden
                                        pauschaleField.visible = false
                                        umsatzgrenzeField.visible = false
                                        pauschaleLabel.visible = false
                                        umsatzgrenzeLabel.visible = false
                                    } else {
                                        dealTypeField = "P"
                                        // Bei P-Deal Pauschale und Umsatzgrenze anzeigen
                                        pauschaleField.visible = true
                                        umsatzgrenzeField.visible = true
                                        pauschaleLabel.visible = true
                                        umsatzgrenzeLabel.visible = true
                                    }
                                }
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: dealTypeField
                                font.family: ubuntuFont.name
                                font.pixelSize: 18
                                font.bold: true
                                color: "white"
                            }
                        }
                        
                        // Pauschale (nur bei P-Deal)
                        Text {
                            id: pauschaleLabel
                            text: "Pauschale (€) *"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            Layout.preferredWidth: 120
                            visible: dealTypeField === "P"
                        }
                        
                        TextField {
                            id: pauschaleField
                            Layout.preferredWidth: 200
                            height: 40
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. 500.00"
                            visible: dealTypeField === "P"
                            inputMethodHints: Qt.ImhFormattedNumbersOnly
                            padding: 8
                        }
                        
                        // Umsatzgrenze (nur bei P-Deal)
                        Text {
                            id: umsatzgrenzeLabel
                            text: "Umsatzgrenze (€) *"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                            Layout.preferredWidth: 120
                            visible: dealTypeField === "P"
                        }
                        
                        TextField {
                            id: umsatzgrenzeField
                            Layout.preferredWidth: 200
                            height: 40
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 2
                                radius: 6
                            }
                            placeholderText: "z.B. 1200.00"
                            visible: dealTypeField === "P"
                            inputMethodHints: Qt.ImhFormattedNumbersOnly
                            padding: 8
                        }
                    }
                }
                
                // Buttons mit Icons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    Layout.alignment: Qt.AlignRight
                    
                    // Abbrechen-Button mit Close-Icon
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: dealFormOverlay.visible = false
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                width: parent.containsMouse ? 32 : 28
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                    
                    // Speichern-Button mit Save-Icon
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                // Deal-Daten sammeln
                                var dealData = {
                                    driver_id: currentDealDriverId,
                                    employee_name: currentDealEmployeeName,
                                    deal_type: dealTypeField,
                                    pauschale: pauschaleField.text.trim(),
                                    umsatzgrenze: umsatzgrenzeField.text.trim(),
                                    garage: garageField.text.trim()
                                }
                                
                                // Validierung
                                if (dealData.deal_type === "P") {
                                    if (!dealData.pauschale || !dealData.umsatzgrenze) {
                                        console.log("Fehler: Bei P-Deal müssen Pauschale und Umsatzgrenze angegeben werden.")
                                        return
                                    }
                                }
                                
                                // Deal speichern über Backend
                                if (mitarbeiterBackendV2) {
                                    var result = mitarbeiterBackendV2.saveDealData(
                                        currentDealDriverId,
                                        dealData.deal_type,
                                        dealData.pauschale,
                                        dealData.umsatzgrenze,
                                        dealData.garage
                                    )
                                    if (result && result.success) {
                                        console.log("Deal erfolgreich gespeichert:", result.message)
                                    } else {
                                        console.log("Fehler beim Speichern des Deals:", result ? result.message : "Unbekannter Fehler")
                                    }
                                }
                                
                                // Overlay schließen
                                dealFormOverlay.visible = false
                                
                                // Felder zurücksetzen
                                dealTypeField = "P"
                                pauschaleField.text = ""
                                umsatzgrenzeField.text = ""
                                garageField.text = ""
                            }
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.containsMouse ? "assets/icons/save_orange.svg" : "assets/icons/save_white.svg"
                                width: parent.containsMouse ? 32 : 28
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                }
            }
            
            // ESC-Taste zum Schließen
            Keys.onEscapePressed: dealFormOverlay.visible = false
        }
    }
    
    // Delete-Bestätigungsdialog
    Rectangle {
        id: deleteConfirmationOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 2001
        
        MouseArea {
            anchors.fill: parent
            onClicked: deleteConfirmationOverlay.visible = false
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(parent.width * 0.4, 400)
            height: Math.min(parent.height * 0.3, 200)
            color: "#1a1a1a"
            border.color: "#F44336"
            border.width: 2
            radius: 8
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                // Header
                Text {
                    text: "Mitarbeiter löschen"
                    font.family: ubuntuFont.name
                    font.pixelSize: 20
                    font.bold: true
                    color: "#F44336"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                }
                
                // Nachricht
                Text {
                    text: deleteEmployeeData ? 
                          `Möchten Sie "${deleteEmployeeData.first_name} ${deleteEmployeeData.last_name}" (Driver ID: ${deleteEmployeeData.driver_id}) wirklich löschen?` :
                          "Möchten Sie diesen Mitarbeiter wirklich löschen?"
                    font.family: ubuntuFont.name
                    font.pixelSize: 14
                    color: "white"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                    wrapMode: Text.WordWrap
                }
                
                // Warnung
                Text {
                    text: "⚠️ Diese Aktion kann nicht rückgängig gemacht werden!"
                    font.family: ubuntuFont.name
                    font.pixelSize: 12
                    color: "#FF9800"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                }
                
                // Buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    // Abbrechen-Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 20
                        color: "transparent"
                        border.color: "#666666"
                        border.width: 1
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: deleteConfirmationOverlay.visible = false
                            
                            Text {
                                anchors.centerIn: parent
                                text: "Abbrechen"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: parent.containsMouse ? "#cccccc" : "#999999"
                            }
                        }
                    }
                    
                    // Löschen-Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 20
                        color: parent.containsMouse ? "#666666" : "#444444"
                        border.width: 0
                        
                        MouseArea {
                            id: confirmDeleteArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (mitarbeiterBackendV2 && deleteEmployeeData) {
                                    mitarbeiterBackendV2.confirmDeleteEmployee(deleteEmployeeData)
                                }
                                deleteConfirmationOverlay.visible = false
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: "Löschen"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                font.bold: true
                                color: "white"
                            }
                        }
                    }
                }
            }
            
            // ESC-Taste zum Schließen
            Keys.onEscapePressed: deleteConfirmationOverlay.visible = false
        }
    }
    
    // Duplikat-Dialog
    Rectangle {
        id: duplicateDialogOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 2001
        
        MouseArea {
            anchors.fill: parent
            onClicked: duplicateDialogOverlay.visible = false
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(parent.width * 0.6, 600)
            height: Math.min(parent.height * 0.5, 400)
            color: "#1a1a1a"
            border.color: "#FFA500"
            border.width: 2
            radius: 8
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                // Header
                Text {
                    text: "Duplikat gefunden"
                    font.family: ubuntuFont.name
                    font.pixelSize: 20
                    font.bold: true
                    color: "#FFA500"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                }
                
                // Nachricht
                Text {
                    text: duplicateDialogData ? duplicateDialogData.message : "Ein Duplikat wurde gefunden."
                    font.family: ubuntuFont.name
                    font.pixelSize: 14
                    color: "white"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                    wrapMode: Text.WordWrap
                }
                
                // Frage
                Text {
                    text: "Was möchten Sie tun?"
                    font.family: ubuntuFont.name
                    font.pixelSize: 16
                    font.bold: true
                    color: "#FFA500"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                }
                
                // Buttons
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    
                    // Ersetzen-Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 20
                        color: parent.containsMouse ? "#666666" : "#444444"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (mitarbeiterBackendV2 && duplicateDialogData) {
                                    mitarbeiterBackendV2.handleDuplicateChoice({
                                        'choice': 'replace',
                                        'employee_data': duplicateDialogData.employee_data
                                    })
                                }
                                duplicateDialogOverlay.visible = false
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: "Ersetzen"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                font.bold: true
                                color: "white"
                            }
                        }
                    }
                    
                    // Neue ID-Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 20
                        color: parent.containsMouse ? "#666666" : "#444444"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (mitarbeiterBackendV2 && duplicateDialogData) {
                                    mitarbeiterBackendV2.handleDuplicateChoice({
                                        'choice': 'new_id',
                                        'employee_data': duplicateDialogData.employee_data
                                    })
                                }
                                duplicateDialogOverlay.visible = false
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: "Neue ID verwenden"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                font.bold: true
                                color: "white"
                            }
                        }
                    }
                    
                    // Bearbeiten-Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 20
                        color: parent.containsMouse ? "#666666" : "#444444"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (mitarbeiterBackendV2 && duplicateDialogData) {
                                    var existingDriverId = null
                                    if (duplicateDialogData.duplicates.driver_id_exists) {
                                        existingDriverId = duplicateDialogData.duplicates.existing_employee.driver_id
                                    } else if (duplicateDialogData.duplicates.license_exists) {
                                        existingDriverId = duplicateDialogData.duplicates.existing_license_employee.driver_id
                                    }
                                    mitarbeiterBackendV2.handleDuplicateChoice({
                                        'choice': 'edit_existing',
                                        'existing_driver_id': existingDriverId
                                    })
                                }
                                duplicateDialogOverlay.visible = false
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: "Bestehenden bearbeiten"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                font.bold: true
                                color: "white"
                            }
                        }
                    }
                    
                    // Abbrechen-Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        radius: 20
                        color: "transparent"
                        border.color: "#666666"
                        border.width: 1
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: duplicateDialogOverlay.visible = false
                            
                            Text {
                                anchors.centerIn: parent
                                text: "Abbrechen"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: parent.containsMouse ? "#cccccc" : "#999999"
                            }
                        }
                    }
                }
            }
            
            // ESC-Taste zum Schließen
            Keys.onEscapePressed: duplicateDialogOverlay.visible = false
        }
    }
    
    // Connections für Backend-Signale
    Connections {
        target: mitarbeiterBackendV2

        function onDeleteConfirmationRequested(employeeData) {
            deleteEmployeeData = employeeData
            deleteConfirmationOverlay.visible = true
            deleteConfirmationOverlay.forceActiveFocus()
        }
        
        function onDuplicateCheckRequested(dialogData) {
            duplicateDialogData = dialogData
            duplicateDialogOverlay.visible = true
            duplicateDialogOverlay.forceActiveFocus()
        }
        
        function onEditEmployeeInForm(driverId) {
            console.log("onEditEmployeeInForm aufgerufen mit driverId:", driverId)
            // Mitarbeiter-Daten laden und Formular öffnen
            var employeeData = mitarbeiterBackendV2.getEmployeeById(driverId)
            console.log("employeeData geladen:", employeeData)
            if (employeeData) {
                console.log("Formular öffnen für:", employeeData)
                // original_driver_id setzen für Update-Modus
                employeeData.original_driver_id = driverId
                showMitarbeiterFormOverlayForEdit(employeeData)
            } else {
                console.log("Keine Mitarbeiter-Daten gefunden für ID:", driverId)
            }
        }
    }
} 