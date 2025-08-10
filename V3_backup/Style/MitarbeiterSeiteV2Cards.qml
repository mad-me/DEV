import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property var goHome
    
    color: Style.background
    radius: Style.radiusNormal
    
    // Globale Properties für Overlays
    property string originalDriverId: ""
    property var deleteEmployeeData: null
    property var duplicateDialogData: null
    property int currentDealDriverId: -1
    property string currentDealEmployeeName: ""
    property string dealTypeField: "P"
    property string statusField: "active"
    
    // Validierungs-Properties
    property bool isDriverIdValid: false
    property bool isLicenseNumberValid: false
    property bool isFirstNameValid: false
    property bool isLastNameValid: false
    property bool isEmailValid: false
    property bool isPhoneValid: false
    property bool isDateValid: false
    
    // Validierungs-Nachrichten
    property string driverIdError: ""
    property string licenseNumberError: ""
    property string firstNameError: ""
    property string lastNameError: ""
    property string emailError: ""
    property string phoneError: ""
    property string dateError: ""

    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
    }

    FontLoader {
        id: spaceMonoFont
        source: "assets/fonts/SpaceMono-Regular.ttf"
    }

    // Header mit Zurück-Button
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 80
        color: "transparent"
        
        RowLayout {
                anchors.fill: parent
                anchors.margins: 20
            
            // Zurück-Button
                        MouseArea {
        width: 60
        height: 60
        onClicked: {
            if (typeof root.goHome === "function") {
                root.goHome();
            } else {
                        console.log("goHome nicht verfügbar");
            }
        }
        cursorShape: Qt.PointingHandCursor
        
        Image {
            anchors.centerIn: parent
                    source: "assets/icons/home_gray.svg"
                    width: 40
                    height: 40
            fillMode: Image.PreserveAspectFit
                }
            }
            
            // Titel (links) mit Hover/Click-Effekten
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
                        if (mitarbeiterBackendV2) {
                            mitarbeiterBackendV2.toggleViewMode()
                        } else {
                            console.log("Toggle View nicht verfügbar")
                        }
                    }
                }
                
                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Mitarbeiterverwaltung"
                    font.family: ubuntuFont.name
                    font.pixelSize: 24
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
            
            // Platzhalter für symmetrisches Layout
            Item {
                width: 60
                height: 60
            }
        }
    }

    // Hauptinhalt mit Cards
            Rectangle {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
                color: "transparent"
        


        // Cards-Container mit echtem Grid-Layout
        GridView {
            id: cardsGridView
            anchors.fill: parent
            clip: true
            
            // Performance-Optimierungen
            cacheBuffer: 1000
            maximumFlickVelocity: 2500
            boundsBehavior: Flickable.StopAtBounds
            
            // Responsive Grid-Eigenschaften
            cellWidth: 396  // 380 + 16 spacing
            cellHeight: 296 // 280 + 16 spacing
            
            // Automatische Spaltenberechnung
            onWidthChanged: {
                var availableWidth = width - 16
                var cardsPerRow = Math.max(1, Math.floor(availableWidth / 396))
                cellWidth = availableWidth / cardsPerRow
            }
            
            // Mitarbeiter-Cards
            model: mitarbeiterBackendV2 ? mitarbeiterBackendV2.mitarbeiterList : []
            
            // Loading-Indikator
            Rectangle {
                id: loadingIndicator
                anchors.centerIn: parent
                width: 200
                height: 60
                radius: 8
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
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        color: "#cccccc"
                    }
                }
            }
            
            delegate: Rectangle {
                id: employeeCard
                width: 380
                height: 280
                radius: 8
                color: "transparent"
                border.width: 0
                z: 1
                
                // Hover-Effekt
                property real hoverScale: employeeCardMouseArea.containsMouse ? 1.05 : 1.0
                
                transform: Scale {
                    xScale: employeeCard.hoverScale
                    yScale: employeeCard.hoverScale
                    origin.x: employeeCard.width / 2
                    origin.y: employeeCard.height / 2
                }
                
                Behavior on hoverScale {
                    NumberAnimation { 
                        duration: 150
                        easing.type: Easing.OutCubic
                    }
                }
            
                // Gradient-Hintergrund
                Rectangle {
                    anchors.fill: parent
                    radius: 8
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
                    onClicked: {
                        if (mitarbeiterBackendV2) {
                            mitarbeiterBackendV2.selectEmployee(modelData.driver_id)
                        }
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
                                text: modelData.last_name || ""
                                font.family: ubuntuFont.name
                                font.pixelSize: 18
                                color: "#cccccc"
                                Layout.fillWidth: true
                            }
                            
                            Text {
                                text: modelData.first_name || ""
                                font.family: ubuntuFont.name
                                font.pixelSize: 20
                                font.bold: true
                                color: "white"
                                Layout.fillWidth: true
                            }
                        }
                        
                        // Status-Badge
                        Rectangle {
                            Layout.preferredWidth: 80
                            height: 28
                            radius: 14
                            color: "transparent"
                            border.width: 0
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    // Status-Toggle: active → suspended → inactive → active
                                    var currentStatus = modelData.status || "active"
                                    var newStatus
                                    if (currentStatus === "active") newStatus = "suspended"
                                    else if (currentStatus === "suspended") newStatus = "inactive"
                                    else newStatus = "active"
                                    
                                    if (mitarbeiterBackendV2) {
                                    mitarbeiterBackendV2.updateEmployeeStatus(modelData.driver_id, newStatus)
                                    }
                                }
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: modelData.status || "active"
                                font.family: ubuntuFont.name
                                font.pixelSize: 12
                                color: {
                                    if (modelData.status === "active") return "#4CAF50"
                                    else if (modelData.status === "suspended") return "#9E9E9E"
                                    else return "#F44336"
                                }
                                horizontalAlignment: Text.AlignCenter
                            }
                        }
                    }
                    
                    // Mitarbeiter-Details
                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 2
                        rowSpacing: 8
                        columnSpacing: 16
                        
                        // ID
                        Text {
                            text: "ID:"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "#b0b0b0"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            height: 32
                            text: modelData.driver_id || "-"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        // Deal-Typ
                        Text {
                            text: "Deal:"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "#b0b0b0"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            height: 32
                            text: modelData.deal || "-"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        // Pauschale (nur bei P-Deal)
                        Text {
                            text: "Pauschale:"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "#b0b0b0"
                            visible: modelData.deal === "P"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            height: 32
                            text: modelData.deal === "P" ? (modelData.pauschale || "-") : "-"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                            visible: modelData.deal === "P"
                        }
                        
                        // Telefon
                        Text {
                            text: "Telefon:"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "#b0b0b0"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            height: 32
                            text: modelData.phone || "-"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        // Email
                        Text {
                            text: "Email:"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "#b0b0b0"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            height: 32
                            text: modelData.email || "-"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    // Aktions-Buttons
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        
                        // Spacer um Buttons nach rechts zu schieben
                        Item {
                            Layout.fillWidth: true
                        }
                        
                        // Edit-Button
                        Rectangle {
                            Layout.preferredWidth: 32
                            height: 32
                            radius: 16
                            color: "transparent"
                            border.width: 0
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    console.log("Edit-Button geklickt für:", modelData.first_name + " " + modelData.last_name)
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
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    console.log("Deal-Button geklickt für:", modelData.first_name + " " + modelData.last_name)
                                    if (mitarbeiterBackendV2) {
                                        showDealFormOverlay(modelData.driver_id, modelData.first_name + " " + modelData.last_name)
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
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    console.log("Delete-Button geklickt für:", modelData.first_name + " " + modelData.last_name)
                                    if (mitarbeiterBackendV2) {
                                        mitarbeiterBackendV2.deleteEmployeeWithConfirmation(modelData.driver_id)
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
    
    // Overlay-Funktionen
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
    
    function showMitarbeiterFormOverlayForEdit(mitarbeiterData) {
        // Original Driver ID speichern
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
            if (dealData) {
                dealTypeField = dealData.deal_type
                pauschaleField.text = dealData.pauschale || ""
                umsatzgrenzeField.text = dealData.umsatzgrenze || ""
                garageField.text = dealData.garage || ""
                console.log("Deal-Daten geladen:", dealData)
            } else {
                // Fallback: Standard-Deal
                dealTypeField = "P"
                pauschaleField.text = ""
                umsatzgrenzeField.text = ""
                garageField.text = ""
                console.log("Keine Deal-Daten gefunden, verwende Standard")
            }
        }
        
        dealFormOverlay.visible = true
        dealFormOverlay.forceActiveFocus()
    }
    
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
            isEmailValid = false
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
            isPhoneValid = false
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
            isDateValid = false
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
                                statusField = "active"
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
} 