import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0
import "." as Local

Rectangle {
    id: root
    width: parent ? parent.width : 1200
    height: parent ? parent.height : 800
    property var goHome: function() {
        // Fallback: Blende die Datenseite aus und zeige das MainMenu
        root.visible = false;
        if (typeof mainWindow !== 'undefined') {
            mainWindow.stackVisible = false;
        }
    }
    color: Style.background
    radius: Style.radiusNormal

    FontLoader { id: ubuntuFont; source: "assets/fonts/Ubuntu-Regular.ttf" }

    // Toggle Properties
    property bool showImport: true
    property bool showPreview: true
    property bool showFilters: true
    property bool showRevenue: true

    // Home-Button
    MouseArea {
        id: homeArea
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.top: parent.top
        anchors.topMargin: 48
        width: 60
        height: 60
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            if (typeof root.goHome === "function") {
                root.goHome();
            }
        }
        
        Image {
            anchors.centerIn: parent
            source: homeArea.containsMouse ? "assets/icons/home_orange.svg" : "assets/icons/home_gray.svg"
            width: homeArea.containsMouse ? 44 : 40
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

        // Header
        RowLayout {
            Layout.fillWidth: true
            spacing: Style.spacingLarge
            
            Rectangle {
                Layout.fillWidth: true
                height: 50
                color: "transparent"
                
                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Datenverwaltung"
                    font.family: ubuntuFont.name
                    font.pixelSize: 36
                    font.bold: true
                    color: Style.text
                }
            }
            
            Rectangle {
                Layout.preferredWidth: 280
                height: 50
                radius: Style.radiusNormal
                color: Style.surface
                border.color: datenBackend && datenBackend.isLoading ? Style.primary : Style.border
                border.width: 1
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8
                    Text { 
                        text: datenBackend && datenBackend.isLoading ? "🔄" : (datenBackend && datenBackend.hasData ? "📊" : "⚠️"); 
                        font.pixelSize: 18; 
                        color: Style.text 
                    }
                    Text {
                        text: datenBackend && datenBackend.isLoading ? "Lade..." : (datenBackend && datenBackend.hasData ? "Daten verfügbar" : "Keine Daten")
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        color: Style.text
                        Layout.fillWidth: true
                    }
                }
            }
        }

        // Dashboard Grid
        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: 3
            rows: 2
            rowSpacing: Style.spacingLarge
            columnSpacing: Style.spacingLarge

            // Card 1: Import/Export
            Rectangle {
                Layout.column: 0; Layout.row: 0
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: Style.radiusLarge
                opacity: 0.95
                
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#050505" }
                    GradientStop { position: 0.8; color: "#050505" }
                    GradientStop { position: 1.0; color: "#1a1a1a" }
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Style.spacingLarge
                    spacing: Style.spacingNormal

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: "transparent"
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: showImport = !showImport
                        }
                        Text { 
                            text: showImport ? "IMPORT" : "EXPORT"
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            font.bold: true
                            color: Style.text
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            opacity: 0.8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "transparent"
                        radius: Style.radiusNormal
                        opacity: 1.0
                        
                        Loader {
                            anchors.fill: parent
                            anchors.margins: Style.spacingSmall
                            sourceComponent: showImport ? importView : exportView
                        }
                    }
                }
            }

            // Card 2: Vorschau/Statistiken
            Rectangle {
                Layout.column: 1; Layout.row: 0
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: Style.radiusLarge
                opacity: 0.95
                
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#050505" }
                    GradientStop { position: 0.8; color: "#050505" }
                    GradientStop { position: 1.0; color: "#1a1a1a" }
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Style.spacingLarge
                    spacing: Style.spacingNormal

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: "transparent"
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: showPreview = !showPreview
                        }
                        Text { 
                            text: showPreview ? "VORSCHAU" : "STATISTIKEN"
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            font.bold: true
                            color: Style.text
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            opacity: 0.8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Style.background
                        radius: Style.radiusNormal
                        opacity: 0.8
                        
                        Loader {
                            anchors.fill: parent
                            anchors.margins: Style.spacingSmall
                            sourceComponent: showPreview ? previewView : statisticsView
                        }
                    }
                }
            }

            // Card 3: Filter/Einstellungen
            Rectangle {
                Layout.column: 0; Layout.row: 1
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: Style.radiusLarge
                opacity: 0.95
                
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#050505" }
                    GradientStop { position: 0.8; color: "#050505" }
                    GradientStop { position: 1.0; color: "#1a1a1a" }
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Style.spacingLarge
                    spacing: Style.spacingNormal

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: "transparent"
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: showFilters = !showFilters
                        }
                        Text { 
                            text: showFilters ? "FILTER" : "EINSTELLUNGEN"
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            font.bold: true
                            color: Style.text
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            opacity: 0.8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Style.background
                        radius: Style.radiusNormal
                        opacity: 0.8
                        
                        Loader {
                            anchors.fill: parent
                            anchors.margins: Style.spacingSmall
                            sourceComponent: showFilters ? filterView : settingsView
                        }
                    }
                }
            }

            // Card 4: Umsatz/Plattformen
            Rectangle {
                Layout.column: 1; Layout.row: 1
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: Style.radiusLarge
                opacity: 0.95
                
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#050505" }
                    GradientStop { position: 0.8; color: "#050505" }
                    GradientStop { position: 1.0; color: "#1a1a1a" }
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Style.spacingLarge
                    spacing: Style.spacingNormal

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: "transparent"
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: showRevenue = !showRevenue
                        }
                        Text { 
                            text: showRevenue ? "UMSATZ" : "PLATTFORMEN"
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            font.bold: true
                            color: Style.text
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            opacity: 0.8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Style.background
                        radius: Style.radiusNormal
                        opacity: 0.8
                        
                        Loader {
                            anchors.fill: parent
                            anchors.margins: Style.spacingSmall
                            sourceComponent: showRevenue ? revenueView : platformView
                        }
                    }
                }
            }

            // Card 5: Case Management
            Rectangle {
                Layout.column: 2; Layout.row: 0
                Layout.rowSpan: 2
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: Style.radiusLarge
                opacity: 0.95
                
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#050505" }
                    GradientStop { position: 0.8; color: "#050505" }
                    GradientStop { position: 1.0; color: "#1a1a1a" }
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Style.spacingLarge
                    spacing: Style.spacingNormal

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: "transparent"
                        Text { 
                            text: "CASE MANAGEMENT"
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            font.bold: true
                            color: Style.text
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            opacity: 0.8
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Style.background
                        radius: Style.radiusNormal
                        opacity: 0.8
                        
                        Loader {
                            anchors.fill: parent
                            anchors.margins: Style.spacingSmall
                            sourceComponent: caseManagementView
                        }
                    }
                }
            }
        }
    }

    // Error Handling
    Connections {
        target: datenBackend
        function onErrorOccurred(title, message) {
            console.log("Fehler:", title, message)
        }
    }

    Component.onCompleted: {
        if (datenBackend) datenBackend.loadData("week", "all", "all")
    }

    // View Components
    Component {
        id: importView
        
        // Drag & Drop Area
        Rectangle {
            id: dropArea
            anchors.fill: parent
            color: "transparent"
            border.color: dropAreaInner.containsDrag ? Style.primary : "transparent"
            border.width: dropAreaInner.containsDrag ? 3 : 0
                
            // Drag & Drop Events
            DropArea {
                id: dropAreaInner
                anchors.fill: parent
                
                onDropped: function(drop) {
                    console.log("Dateien gedroppt:", drop.urls)
                    if (datenBackend && typeof datenBackend.addDroppedFiles === "function") {
                        datenBackend.addDroppedFiles(drop.urls)
                    } else {
                        console.log("Backend addDroppedFiles Funktion nicht verfügbar")
                    }
                }
                
                onEntered: function(drag) {
                    console.log("Drag entered")
                }
                
                onExited: function(drag) {
                    console.log("Drag exited")
                }
            }
            
            // Click to select files
            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (datenBackend && typeof datenBackend.openFileDialog === "function") {
                        datenBackend.openFileDialog()
                    } else {
                        console.log("Backend openFileDialog Funktion nicht verfügbar")
                    }
                }
            }
            
            // Content
            ColumnLayout {
                anchors.centerIn: parent
                spacing: Style.spacingSmall
                Layout.alignment: Qt.AlignCenter
                
                Text {
                    text: dropAreaInner.containsDrag ? "📁 Dateien hier ablegen" : "📁 Dateien hier ablegen oder klicken"
                    color: Style.text
                    font.pixelSize: 16
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    text: "Unterstützte Formate: PDF, CSV, Excel"
                    color: Style.textMuted
                    font.pixelSize: 12
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    text: "Gehalt, Umsatz, Funk-Daten"
                    color: Style.textMuted
                    font.pixelSize: 12
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    text: "Uber, Bolt, 40100, 31300"
                    color: Style.textMuted
                    font.pixelSize: 12
                    Layout.alignment: Qt.AlignHCenter
                }
            }
            
            // Import Status Feedback
            Rectangle {
                id: importFeedback
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: Style.spacingSmall
                height: 0
                radius: Style.radiusSmall
                color: "transparent"
                opacity: 0
                
                property string feedbackText: ""
                property string feedbackType: "info" // info, success, error
                
                Text {
                    anchors.centerIn: parent
                    text: importFeedback.feedbackText
                    color: Style.text
                    font.pixelSize: 12
                    font.bold: true
                }
                
                states: [
                    State {
                        name: "visible"
                        when: importFeedback.feedbackText !== ""
                        PropertyChanges {
                            target: importFeedback
                            height: 30
                            opacity: 1
                            color: {
                                if (importFeedback.feedbackType === "success") return "#4CAF50"
                                else if (importFeedback.feedbackType === "error") return "#F44336"
                                else return Style.primary
                            }
                        }
                    }
                ]
                
                transitions: [
                    Transition {
                        to: "visible"
                        reversible: true
                        NumberAnimation {
                            properties: "height,opacity"
                            duration: 300
                            easing.type: Easing.OutQuad
                        }
                    }
                ]
                
                // Funktion zum Anzeigen von Feedback
                function showFeedback(type, message) {
                    feedbackType = type
                    feedbackText = message
                    
                    // Auto-hide nach 5 Sekunden
                    feedbackTimer.restart()
                }
                
                Timer {
                    id: feedbackTimer
                    interval: 5000
                    repeat: false
                    onTriggered: {
                        importFeedback.feedbackText = ""
                    }
                }
            }
        }
    }

    Component {
        id: exportView
        
        ColumnLayout {
            spacing: Style.spacingNormal
            
            Text {
                text: "📤 Export"
                color: Style.text
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "Daten exportieren"
                color: Style.textMuted
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }
            
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: previewView
        
        ColumnLayout {
            spacing: Style.spacingNormal
            
            Text {
                text: "👁️ Vorschau"
                color: Style.text
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "Datenvorschau"
                color: Style.textMuted
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }
            
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: statisticsView
        
        ColumnLayout {
            spacing: Style.spacingNormal
            
            Text {
                text: "📊 Statistiken"
                color: Style.text
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "Zusammenfassung & Metriken"
                color: Style.textMuted
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }
            
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: filterView
        
        ColumnLayout {
            spacing: Style.spacingNormal
            
            Text {
                text: "🔍 Filter"
                color: Style.text
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "Zeitraum, Fahrer, Platform"
                color: Style.textMuted
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }
            
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: settingsView
        
        ColumnLayout {
            spacing: Style.spacingNormal
            
            Text {
                text: "⚙️ Einstellungen"
                color: Style.text
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "Anzeige-Einstellungen"
                color: Style.textMuted
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }
            
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: revenueView
        
        ColumnLayout {
            spacing: Style.spacingNormal
            
            Text {
                text: "💰 Umsatz"
                color: Style.text
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "Umsatzentwicklung"
                color: Style.textMuted
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }
            
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: platformView
        
        ColumnLayout {
            spacing: Style.spacingNormal
            
            Text {
                text: "🌐 Plattformen"
                color: Style.text
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "Uber/Bolt/40100 Verteilung"
                color: Style.textMuted
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }
            
            Item { Layout.fillHeight: true }
        }
    }

    Component {
        id: caseManagementView
        
        ColumnLayout {
            spacing: Style.spacingNormal
            
            Text {
                text: "📋 Case Management"
                color: Style.text
                font.pixelSize: 18
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Text {
                text: "Datensätze verwalten"
                color: Style.textMuted
                font.pixelSize: 14
                Layout.alignment: Qt.AlignHCenter
            }
            
            Item { Layout.fillHeight: true }
        }
    }
    
    // Plattform-Auswahl-Dialog
    Local.PlatformSelectionDialog {
        id: platformDialog
        visible: false
        
        onPlatformSelected: function(platform) {
            console.log("Plattform ausgewählt:", platform)
            datenBackend.selectPlatform(platform)
            platformDialog.visible = false
        }
        
        onDialogClosed: function() {
            platformDialog.visible = false
        }
    }
    
    // Monat/Jahr-Auswahl-Dialog
    Local.MonthYearSelectionDialog {
        id: monthYearDialog
        visible: false
        
        onMonthYearSelected: function(month, year) {
            console.log("Monat/Jahr ausgewählt:", month, year)
            datenBackend.selectMonthYear(month, year)
            monthYearDialog.visible = false
        }
        
        onDialogClosed: function() {
            monthYearDialog.visible = false
        }
    }
    
    // Verbindung zum Backend für Plattform-Auswahl
    Connections {
        target: datenBackend
        
        function onPlatformSelectionRequested(filename, platforms) {
            console.log("Plattform-Auswahl angefordert für:", filename, "Plattformen:", platforms)
            platformDialog.filename = filename
            platformDialog.platforms = platforms
            platformDialog.visible = true
        }
        
        function onMonthYearSelectionRequested(filename, suggestedDate) {
            console.log("Monat/Jahr-Auswahl angefordert für:", filename, "Vorschlag:", suggestedDate)
            monthYearDialog.filename = filename
            monthYearDialog.suggestedDate = suggestedDate
            monthYearDialog.visible = true
        }
        
        function onImportFeedbackChanged(type, message) {
            console.log("Import Feedback:", type, message)
            // Hier könnte man Toast-Nachrichten anzeigen
        }
    }
}
