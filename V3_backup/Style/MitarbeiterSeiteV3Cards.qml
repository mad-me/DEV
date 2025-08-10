import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: parent ? parent.width : 1200
    height: parent ? parent.height : 800
    property var goHome: function() {
        // Fallback: Blende die Mitarbeiterseite aus und zeige das MainMenu
        root.visible = false;
        if (typeof mainWindow !== 'undefined') {
            mainWindow.stackVisible = false;
        }
    }
    color: "#050505"
    radius: 8
    
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
    
    // Toast-Notification-System
    property var toastQueue: []
    property bool isToastVisible: false
    property string currentToastMessage: ""
    property string currentToastType: "info"
    property int toastDuration: 3000

    // Funktionen
    function showMitarbeiterFormOverlay() {
        driverIdField.text = ""
        licenseNumberField.text = ""
        firstNameField.text = ""
        lastNameField.text = ""
        phoneField.text = ""
        emailField.text = ""
        var today = new Date()
        var year = today.getFullYear()
        var month = String(today.getMonth() + 1).padStart(2, '0')
        var day = String(today.getDate()).padStart(2, '0')
        hireDateField.text = year + "-" + month + "-" + day
        statusField = "active"
        originalDriverId = ""
        
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
        
        mitarbeiterFormTitle.text = "Neuen Mitarbeiter anlegen"
        mitarbeiterFormOverlay.visible = true
        mitarbeiterFormOverlay.forceActiveFocus()
    }
    
    function showMitarbeiterFormOverlayForEdit(mitarbeiterData) {
        originalDriverId = mitarbeiterData.original_driver_id || mitarbeiterData.driver_id || ""
        driverIdField.text = mitarbeiterData.driver_id || ""
        licenseNumberField.text = mitarbeiterData.driver_license_number || ""
        firstNameField.text = mitarbeiterData.first_name || ""
        lastNameField.text = mitarbeiterData.last_name || ""
        phoneField.text = mitarbeiterData.phone || ""
        emailField.text = mitarbeiterData.email || ""
        hireDateField.text = mitarbeiterData.hire_date || ""
        statusField = mitarbeiterData.status || "active"
        mitarbeiterFormTitle.text = mitarbeiterData.first_name + " " + mitarbeiterData.last_name
        mitarbeiterFormOverlay.visible = true
        mitarbeiterFormOverlay.forceActiveFocus()
    }
    
    function showDealFormOverlay(driverId, employeeName) {
        currentDealDriverId = driverId
        currentDealEmployeeName = employeeName
        dealFormTitle.text = employeeName
        
        if (mitarbeiterBackendV2) {
            var dealData = mitarbeiterBackendV2.getDealByDriverId(driverId)
            if (dealData && typeof dealData === 'object' && dealData.hasOwnProperty('deal_type')) {
                dealTypeField = (dealData.deal_type && dealData.deal_type !== "") ? dealData.deal_type : "P"
                pauschaleField.text = (dealData.pauschale && dealData.pauschale !== "") ? dealData.pauschale : ""
                umsatzgrenzeField.text = (dealData.umsatzgrenze && dealData.umsatzgrenze !== "") ? dealData.umsatzgrenze : ""
                garageField.text = (dealData.garage && dealData.garage !== "") ? dealData.garage : ""
            } else {
                dealTypeField = "P"
                pauschaleField.text = ""
                umsatzgrenzeField.text = ""
                garageField.text = ""
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
            return true
        }
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(trimmedText)) {
            isEmailValid = false
            emailError = "Ungültige E-Mail-Adresse"
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
            return true
        }
        var phoneRegex = /^[\d\s\-\+\(\)]+$/
        if (!phoneRegex.test(trimmedText)) {
            isPhoneValid = false
            phoneError = "Ungültige Telefonnummer"
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
            return false
        }
        var dateRegex = /^\d{4}-\d{2}-\d{2}$/
        if (!dateRegex.test(trimmedText)) {
            isDateValid = false
            dateError = "Datum muss im Format YYYY-MM-DD sein"
            return false
        }
        isDateValid = true
        dateError = ""
        return true
    }
    
    function validateAllFields() {
        var isValid = true
        isValid = validateDriverId(driverIdField.text) && isValid
        isValid = validateLicenseNumber(licenseNumberField.text) && isValid
        isValid = validateFirstName(firstNameField.text) && isValid
        isValid = validateLastName(lastNameField.text) && isValid
        isValid = validateEmail(emailField.text) && isValid
        isValid = validatePhone(phoneField.text) && isValid
        isValid = validateDate(hireDateField.text) && isValid
        return isValid
    }
    
    function clearValidationErrors() {
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
    }

    // Home-Button
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

            // Suchfeld
            RowLayout {
                Layout.fillWidth: true
                spacing: Style.spacingLarge
                
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

            // Cards-Container mit erweiterten Performance-Optimierungen
            GridView {
                id: cardsGridView
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                
                // Erweiterte Performance-Optimierungen für Virtual Scrolling
                cacheBuffer: 2000  // Erhöht für bessere Performance
                maximumFlickVelocity: 3000  // Erhöht für flüssigere Scrolling
                boundsBehavior: Flickable.StopAtBounds
                flickDeceleration: 1500  // Schnelleres Abbremsen
                
                // Lazy Loading für große Listen
                property bool isLoadingMore: false
                property int currentPage: 0
                
                onAtYEndChanged: {
                    if (atYEnd && !isLoadingMore && mitarbeiterBackendV2) {
                        isLoadingMore = true
                        mitarbeiterBackendV2.loadNextPage()
                        isLoadingMore = false
                    }
                }
                
                cellWidth: 396
                cellHeight: 296
                
                onWidthChanged: {
                    var availableWidth = width - 16
                    var cardsPerRow = Math.max(1, Math.floor(availableWidth / 396))
                    cellWidth = availableWidth / cardsPerRow
                }
                
                model: mitarbeiterBackendV2 ? mitarbeiterBackendV2.mitarbeiterList : []
                
                // Erweiterter Loading-Indikator
                Rectangle {
                    id: loadingIndicator
                    anchors.centerIn: parent
                    width: 300
                    height: 80
                    radius: Style.radiusNormal
                    color: "#1a1a1a"
                    border.color: "#333333"
                    border.width: 1
                    visible: mitarbeiterBackendV2 && mitarbeiterBackendV2.isLoading
                    z: 100
                    
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 8
                        
                        // Spinner-Animation
                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter
                            width: 30
                            height: 30
                            radius: 15
                            color: "#ff8c00"
                            
                            RotationAnimation on rotation {
                                from: 0
                                to: 360
                                duration: 1000
                                loops: Animation.Infinite
                            }
                        }
                        
                        // Loading-Nachricht
                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: mitarbeiterBackendV2 && mitarbeiterBackendV2.loadingMessage ? 
                                  mitarbeiterBackendV2.loadingMessage : "Mitarbeiter werden geladen..."
                            font.pixelSize: 14
                            color: "#cccccc"
                            horizontalAlignment: Text.AlignHCenter
                        }
                        
                        // Fortschrittsbalken (falls verfügbar)
                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.preferredWidth: 200
                            Layout.preferredHeight: 4
                            radius: 2
                            color: "#333333"
                            visible: mitarbeiterBackendV2 && mitarbeiterBackendV2.loadingProgress > 0
                            
                            Rectangle {
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.bottom: parent.bottom
                                width: parent.width * (mitarbeiterBackendV2 ? mitarbeiterBackendV2.loadingProgress / 100 : 0)
                                radius: 2
                                color: "#ff8c00"
                                
                                Behavior on width {
                                    NumberAnimation { duration: 300 }
                                }
                            }
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
                    
                    property bool isVisible: true
                    property bool isHovered: false
                    property real hoverScale: isHovered ? 1.05 : 1.0
                    
                    visible: isVisible
                    
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
                        
                        onEntered: {
                            employeeCard.isHovered = true
                        }
                        onExited: {
                            employeeCard.isHovered = false
                        }
                        
                        onClicked: {
                            if (mitarbeiterBackendV2) {
                                mitarbeiterBackendV2.selectEmployee(model.driver_id)
                            }
                        }
                    }
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12
        
        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                
                                Text {
                                    text: modelData.last_name || ""
                                    font.pixelSize: 18
                                    color: "#cccccc"
                                    Layout.fillWidth: true
                                }
                                 
                                Text {
                                    text: modelData.first_name || ""
                                    font.pixelSize: 20
                                    font.bold: true
                                    color: "white"
                                    Layout.fillWidth: true
                                }
                            }
                            
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
                                            var currentStatus = modelData.status || "active"
                                            var newStatus
                                            if (currentStatus === "active") newStatus = "suspended"
                                            else if (currentStatus === "suspended") newStatus = "inactive"
                                            else newStatus = "active"
                                            
                                            mitarbeiterBackendV2.updateStatusById(modelData.driver_id, newStatus)
                                        }
                                    }
                                }
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.status || "active"
                                    font.pixelSize: 12
                                    color: {
                                        var status = modelData.status || "active"
                                        if (status === "active") return "#4CAF50"
                                        else if (status === "suspended") return "#F44336"
                                        else return "#9E9E9E"
                                    }
                                    horizontalAlignment: Text.AlignCenter
                                }
                            }
                        }
                        
                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: 2
                            rowSpacing: 8
                            columnSpacing: 16
                            visible: !mitarbeiterBackendV2 || !mitarbeiterBackendV2.toggleView
                            
                            Text {
                                text: "ID:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.driver_id || "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            Text {
                                text: "Deal:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.deal || "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            Text {
                                text: "Pauschale:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: modelData.deal === "P"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.deal === "P" ? (modelData.pauschale || "-") : "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: modelData.deal === "P"
                            }
                        }
                        
                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: 2
                            rowSpacing: 8
                            columnSpacing: 16
                            visible: mitarbeiterBackendV2 && mitarbeiterBackendV2.toggleView
                            
                            Text {
                                text: "Telefon:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.phone || "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            Text {
                                text: "Email:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.email || "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            Text {
                                text: "Einstellungsdatum:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.hire_date || "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            Text {
                                text: "Umsatzgrenze:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: modelData.deal === "P"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.deal === "P" ? (modelData.umsatzgrenze || "-") : "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: modelData.deal === "P"
                            }
                            
                            Text {
                                text: "Garage:"
                                font.pixelSize: 14
                                color: "#b0b0b0"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.garage || "-"
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            
                            Item {
                                Layout.fillWidth: true
                            }
                            
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
                                            var mitarbeiterData = {
                                                driver_id: modelData.driver_id,
                                                original_driver_id: modelData.driver_id,
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
                                        console.log("Delete-Button geklickt für:", modelData.first_name + " " + modelData.last_name + " (ID: " + modelData.driver_id + ")")
                                        
                                        if (mitarbeiterBackendV2) {
                                            // Direkte Löschung ohne Bestätigungsdialog
                                            try {
                                                console.log("Versuche direkte Löschung...")
                                                mitarbeiterBackendV2.deleteEmployee(modelData.driver_id)
                                                console.log("deleteEmployee erfolgreich aufgerufen")
                                            } catch (error) {
                                                console.error("Fehler bei deleteEmployee:", error)
                                                
                                                // Fallback: Bestätigungsdialog
                                                try {
                                                    console.log("Versuche Bestätigungsdialog...")
                                                    mitarbeiterBackendV2.deleteEmployeeWithConfirmation(modelData.driver_id)
                                                    console.log("deleteEmployeeWithConfirmation erfolgreich aufgerufen")
                                                } catch (fallbackError) {
                                                    console.error("Fehler bei deleteEmployeeWithConfirmation:", fallbackError)
                                                }
                                            }
                                        } else {
                                            console.log("mitarbeiterBackendV2 nicht verfügbar")
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
        
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 24
            spacing: 32
            
            MouseArea {
                id: addArea
                width: 56; height: 56
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true
                onClicked: {
                    if (mitarbeiterBackendV2) {
                        showMitarbeiterFormOverlay()
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

        // Signal-Handler für Backend-Events
    Connections {
        target: mitarbeiterBackendV2
        
        function onDeleteConfirmationRequested(employeeData) {
            console.log("DeleteConfirmationRequested Signal empfangen:", employeeData)
            deleteEmployeeData = employeeData
            deleteConfirmationOverlay.visible = true
        }
        
        function onDuplicateCheckRequested(dialogData) {
            console.log("DuplicateCheckRequested Signal empfangen:", dialogData)
            duplicateDialogData = dialogData
            duplicateDialogOverlay.visible = true
        }
        
        function onEditEmployeeInForm(driverId) {
            console.log("EditEmployeeInForm Signal empfangen für driver_id:", driverId)
            if (mitarbeiterBackendV2) {
                var employeeData = mitarbeiterBackendV2.getEmployeeById(driverId)
                if (employeeData) {
                    showMitarbeiterFormOverlayForEdit(employeeData)
                }
            }
        }
        
        function onErrorOccurred(errorMessage) {
            console.log("ErrorOccurred Signal empfangen:", errorMessage)
        }
        
        function onStatusMessageChanged() {
            console.log("StatusMessageChanged Signal empfangen")
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
        
        // canSave Funktion entfernt - funktioniert nicht in diesem QML-Kontext
        
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
                
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 20
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    GridLayout {
                        width: parent.width
                        anchors.horizontalCenter: parent.horizontalCenter
                        columns: 2
                        rowSpacing: 20
                        columnSpacing: 20
                        
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
                        
                        Text {
                            text: "Status"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
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
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    Item { Layout.fillWidth: true }
                    
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
                    
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor  // Hardcoded - canSave() funktioniert nicht
                            enabled: true  // Hardcoded - canSave() funktioniert nicht
                            onClicked: {
                                // if (!canSave()) return  // Deaktiviert - canSave() funktioniert nicht
                                
                                var mitarbeiterData = {
                                    driver_id: driverIdField.text.trim(),
                                    original_driver_id: originalDriverId,
                                    driver_license_number: licenseNumberField.text.trim(),
                                    first_name: firstNameField.text.trim(),
                                    last_name: lastNameField.text.trim(),
                                    phone: phoneField.text.trim(),
                                    email: emailField.text.trim(),
                                    hire_date: hireDateField.text.trim(),
                                    status: statusField
                                }
                                
                                mitarbeiterBackendV2.saveEmployee(mitarbeiterData)
                                mitarbeiterFormOverlay.visible = false
                                
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
                                source: parent.containsMouse ? "assets/icons/save_orange.svg" : "assets/icons/save_white.svg"  // Hardcoded - canSave() funktioniert nicht
                                width: parent.containsMouse ? 32 : 28  // Hardcoded - canSave() funktioniert nicht
                                height: width
                                fillMode: Image.PreserveAspectFit
                                opacity: 1.0  // Hardcoded - canSave() funktioniert nicht
                            }
                        }
                    }
                }
            }
            
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
            
            Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 12
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    GridLayout {
                        width: parent.width
                        columns: 2
                        rowSpacing: 20
                        columnSpacing: 20
                        
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
                                    if (dealTypeField === "P") {
                                        dealTypeField = "%"
                                        pauschaleField.visible = false
                                        umsatzgrenzeField.visible = false
                                        pauschaleLabel.visible = false
                                        umsatzgrenzeLabel.visible = false
                                    } else if (dealTypeField === "%") {
                                        dealTypeField = "C"
                                        pauschaleField.visible = false
                                        umsatzgrenzeField.visible = false
                                        pauschaleLabel.visible = false
                                        umsatzgrenzeLabel.visible = false
                                    } else {
                                        dealTypeField = "P"
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
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    Layout.alignment: Qt.AlignRight
                    
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
                                var dealData = {
                                    driver_id: currentDealDriverId,
                                    employee_name: currentDealEmployeeName,
                                    deal_type: dealTypeField,
                                    pauschale: pauschaleField.text.trim(),
                                    umsatzgrenze: umsatzgrenzeField.text.trim(),
                                    garage: garageField.text.trim()
                                }
                                
                                if (dealData.deal_type === "P") {
                                    if (!dealData.pauschale || !dealData.umsatzgrenze) {
                                        return
                                    }
                                }
                                
                                if (mitarbeiterBackendV2) {
                                    var result = mitarbeiterBackendV2.saveDealData(
                                        currentDealDriverId,
                                        dealData.deal_type,
                                        dealData.pauschale,
                                        dealData.umsatzgrenze,
                                        dealData.garage
                                    )
                                }
                                
                                dealFormOverlay.visible = false
                                
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
                
                Text {
                    text: "Mitarbeiter löschen"
                    font.family: ubuntuFont.name
                    font.pixelSize: 20
                    font.bold: true
                    color: "#F44336"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                }
                
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
                
                Text {
                    text: "⚠️ Diese Aktion kann nicht rückgängig gemacht werden!"
                    font.family: ubuntuFont.name
                    font.pixelSize: 12
                    color: "#FF9800"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
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
                
        Text {
                    text: "Duplikat gefunden"
                    font.family: ubuntuFont.name
                    font.pixelSize: 20
                    font.bold: true
                    color: "#FFA500"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                }
                
                Text {
                    text: duplicateDialogData ? duplicateDialogData.message : "Ein Duplikat wurde gefunden."
            font.family: ubuntuFont.name
            font.pixelSize: 14
                    color: "white"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                    wrapMode: Text.WordWrap
                }
                
                Text {
                    text: "Was möchten Sie tun?"
                    font.family: ubuntuFont.name
                    font.pixelSize: 16
                    font.bold: true
                    color: "#FFA500"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignCenter
                }
                
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    
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
            
            Keys.onEscapePressed: duplicateDialogOverlay.visible = false
        }
    }
    
    // Toast-Notification-System
    Rectangle {
        id: toastNotification
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 20
        width: Math.min(400, parent.width - 40)
        height: 60
        radius: Style.radiusNormal
        color: {
            switch(root.currentToastType) {
                case "success": return "#4CAF50"
                case "error": return "#F44336"
                case "warning": return "#FF9800"
                default: return "#2196F3"
            }
        }
        border.color: "white"
        border.width: 1
        visible: root.isToastVisible
        z: 1000
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12
            
            // Icon basierend auf Toast-Typ
            Text {
                text: {
                    switch(root.currentToastType) {
                        case "success": return "✓"
                        case "error": return "✗"
                        case "warning": return "⚠"
                        default: return "ℹ"
                    }
                }
                font.pixelSize: 20
                font.bold: true
                color: "white"
            }
            
            // Toast-Nachricht
            Text {
                Layout.fillWidth: true
                text: root.currentToastMessage
                font.family: ubuntuFont.name
                font.pixelSize: 14
                color: "white"
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
            }
            
            // Schließen-Button
            MouseArea {
                width: 20
                height: 20
                onClicked: hideToast()
                cursorShape: Qt.PointingHandCursor
                
                Text {
                    anchors.centerIn: parent
                    text: "×"
                    font.pixelSize: 18
                    font.bold: true
                    color: "white"
                }
            }
        }
        
        // Animation für Ein-/Ausblenden
        Behavior on opacity {
            NumberAnimation { duration: 300 }
        }
        
        // Timer für automatisches Ausblenden
        Timer {
            id: toastTimer
            interval: root.toastDuration
            onTriggered: hideToast()
        }
    }
    


    
    // Erweiterte Error-Handling-Funktionen
    function handleBackendError(error, operation) {
        console.error("Backend-Fehler bei", operation, ":", error)
        console.log("Fehler bei " + operation + ": " + error)
    }
    
    function handleSuccessMessage(message, operation) {
        console.log("Erfolgreich:", operation, message)
    }
    
    function handleWarningMessage(message) {
        console.warn("Warnung:", message)
    }
    
    function handleInfoMessage(message) {
        console.log("Info:", message)
    }
    
    // Performance-Monitoring-Funktionen
    function logPerformance(operation, duration) {
        console.log("Performance:", operation, "dauerte", duration, "ms")
    }
    
    function optimizeRendering() {
        // Rendering-Optimierungen
        cardsGridView.cacheBuffer = Math.max(cardsGridView.cacheBuffer, 2000)
        cardsGridView.maximumFlickVelocity = Math.max(cardsGridView.maximumFlickVelocity, 3000)
    }
    
    // Memory-Management-Funktionen
    function cleanupMemory() {
        // Memory-Cleanup für bessere Performance
        if (cardsGridView) {
            cardsGridView.cacheBuffer = 1000  // Temporär reduzieren
            cardsGridView.cacheBuffer = 2000  // Wieder erhöhen
        }
    }
    
    // Automatische Performance-Optimierung beim Start
    Component.onCompleted: {
        optimizeRendering()
        console.log("Mitarbeiterseite geladen")
    }
} 