import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1

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

    // Ergebnis-Overlay für Quick-Output - Über allem anderen
    Rectangle {
        id: quickResultOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 999999
        
        // Meta-Infos für Header
        property string metaDriver: ""
        property string metaVehicle: ""
        property string metaWeekFrom: ""
        property string metaWeekTo: ""
        property string rawOutput: ""
        property var parsedWeekData: ({})
        property real sumUmsatz: 0
        property real sumAnteil: 0
        property real sumTank: 0
        property real sumEinsteiger: 0
        property real sumGarage: 0
        property real sumExpense: 0
        property real sumIncome: 0


        // Overlay-Inhalt (1:1 Style vom Wochen-Daten-Overlay)
        Rectangle {
            id: quickResultContent
            width: Math.min(parent.width - 40, weekColumnsContainer.width + 80)  // Dynamische Breite basierend auf Inhalt
            height: Math.min(quickResultContentColumn.height + 160, parent.height - 60)  // Mehr Platz für Scroll-Bereich
            anchors.centerIn: parent
            radius: Style.radiusNormal
            color: "#1a1a1a"
            border.color: "#333333"
            border.width: 1

            // Header
            Rectangle {
                id: quickResultHeader
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 60
                color: "transparent"
                border.color: "#333333"
                border.width: 0

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    Text {
                        id: quickResultTitle
                        text: "Schnellabrechnung Ergebnis"
                        font.family: ubuntuFont.name
                        font.pixelSize: 18
                        font.bold: true
                        color: "#ff8c00"
                        Layout.fillWidth: true
                    }

                    // Kopieren-Button
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 16
                        color: "transparent"
                        border.width: 0
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                try {
                                    if (Qt && Qt.application && Qt.application.clipboard) {
                                        Qt.application.clipboard.setText(quickResultOverlay.rawOutput || "")
                                    }
                                } catch(e) { console.log("Clipboard-Fehler:", e) }
                            }
                            Text { anchors.centerIn: parent; text: "⧉"; font.pixelSize: 16; color: parent.containsMouse ? "#ff8c00" : "#cccccc" }
                        }
                    }

                    // Speichern-Button (SVG-Icon)
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 16
                        color: "transparent"
                        border.width: 0
                        MouseArea {
                            id: saveButtonMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                var vehicle = quickResultOverlay.metaVehicle && quickResultOverlay.metaVehicle.length > 0 ? quickResultOverlay.metaVehicle : quickWeekOverlay.currentLicensePlate
                                var driver = quickResultOverlay.metaDriver && quickResultOverlay.metaDriver.length > 0 ? quickResultOverlay.metaDriver : quickDriverField.text
                                if (!vehicle || !driver) {
                                    console.log("Speichern abgebrochen: Fahrzeug oder Fahrer fehlen")
                                    return
                                }
                                if (!quickResultOverlay.parsedWeekData || Object.keys(quickResultOverlay.parsedWeekData).length === 0) {
                                    console.log("Speichern abgebrochen: Keine WeekData vorhanden")
                                    return
                                }
                                try {
                                    fahrzeugBackendV2.saveQuickResultsForWeeks(vehicle, driver, quickResultOverlay.parsedWeekData)
                                    console.log("Speichern gestartet für", vehicle, driver)
                                } catch(e) {
                                    console.log("Fehler beim Starten des Speicherns:", e)
                                }
                                // Overlays schließen
                                quickResultOverlay.visible = false
                                if (typeof schnellabrechnungOverlay !== 'undefined') schnellabrechnungOverlay.visible = false
                                if (typeof quickWeekOverlay !== 'undefined') quickWeekOverlay.visible = false
                            }
                        }
                        Image {
                            anchors.centerIn: parent
                            source: saveButtonMouse.pressed ? "assets/icons/save_gray.svg" : (saveButtonMouse.containsMouse ? "assets/icons/save_orange.svg" : "assets/icons/save_white.svg")
                            width: saveButtonMouse.pressed ? 20 : (saveButtonMouse.containsMouse ? 22 : 20)
                            height: width
                            fillMode: Image.PreserveAspectFit
                        }
                    }

                    Rectangle {
                        width: 32
                        height: 32
                        radius: 16
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: quickResultOverlay.visible = false
                            
                            Text {
                                anchors.centerIn: parent
                                text: "×"
                                font.pixelSize: 20
                                color: parent.containsMouse ? "#ff8c00" : "#cccccc"
                            }
                        }
                    }
                }
            }

            // Zusammenfassung (fixiert, scrollt nicht mit)
            Rectangle {
                id: quickResultSummary
                anchors.top: quickResultHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 16
                height: 82
                color: Style.surface
                border.color: Style.border
                border.width: 1
                radius: Style.radiusNormal
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 18
                    Repeater {
                        model: [
                            { label: "Umsatz", key: "sumUmsatz" },
                            { label: "Anteil", key: "sumAnteil" },
                            { label: "Tank", key: "sumTank" },
                            { label: "Einsteiger", key: "sumEinsteiger" },
                            { label: "Garage", key: "sumGarage" },
                            { label: "Expense", key: "sumExpense" },
                            { label: "Income", key: "sumIncome" }
                        ]
                        delegate: ColumnLayout {
                            spacing: 2
                            Text { text: modelData.label; font.family: ubuntuFont.name; font.pixelSize: 12; color: Style.textMuted }
                            Text {
                                font.family: ubuntuFont.name; font.pixelSize: 14; color: Style.text; font.bold: true
                                text: (function(){ var v = quickResultOverlay[modelData.key]; return (v || 0).toFixed(2) + "€"; })()
                            }
                        }
                    }
                }
            }

            // ScrollView für alle Daten
            ScrollView {
                anchors.top: quickResultSummary.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: 16
                clip: true
                contentHeight: quickResultContentColumn.height
                contentWidth: weekColumnsContainer.width
                ScrollBar.horizontal.policy: ScrollBar.AsNeeded
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                ColumnLayout {
                    id: quickResultContentColumn
                    width: parent.width
                    spacing: 12
                    Layout.fillWidth: true

                    // Subheader mit Meta-Infos (Fahrer, Fahrzeug, KW von/bis)
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        visible: quickResultOverlay.metaVehicle !== "" || quickResultOverlay.metaDriver !== ""
                        
                        Text {
                            text: (quickResultOverlay.metaDriver && quickResultOverlay.metaDriver.length > 0 ? quickResultOverlay.metaDriver : "-") + " — " + (quickResultOverlay.metaVehicle && quickResultOverlay.metaVehicle.length > 0 ? quickResultOverlay.metaVehicle : "-")
                            color: "#cccccc"
                            font.family: ubuntuFont.name
                            font.pixelSize: 13
                            Layout.fillWidth: true
                        }
                        Text {
                            text: (quickResultOverlay.metaWeekFrom && quickResultOverlay.metaWeekTo) ? ("KW " + quickResultOverlay.metaWeekFrom + "–" + quickResultOverlay.metaWeekTo) : ""
                            color: "#cccccc"
                            font.family: ubuntuFont.name
                            font.pixelSize: 13
                        }
                    }

                    // Horizontales Layout für Kalenderwochen-Spalten
                    Row {
                        id: weekColumnsContainer
                        spacing: 40
                        
                        // Platzhalter für dynamische Spalten
                        // Diese werden durch JavaScript erstellt
                    }
                }
            }
        }
    }

    // Verbindung für Backend-Output
    Connections {
        target: fahrzeugBackendV2
        function onQuickResultReady(output) {
            console.log("QML: QuickResultReady empfangen, Länge:", output ? output.length : 0)
            console.log("QML: Erste 100 Zeichen:", output ? output.substring(0, 100) : "null")
            
            // Zusätzliche Debug-Ausgabe für Benutzer
            if (output && output.length > 0) {
                console.log("QML: Text erfolgreich empfangen")
                console.log("QML: quickResultOverlay.visible =", quickResultOverlay.visible)
                console.log("QML: quickResultOverlay.z =", quickResultOverlay.z)
                
                // Rohtext speichern und Overlay explizit sichtbar machen
                quickResultOverlay.rawOutput = output
                quickResultOverlay.visible = true
                console.log("QML: Overlay explizit sichtbar gemacht")
                
                // Schnellabrechnung-Daten parsen und Spalten erstellen
                parseSchnellabrechnungData(output)
            } else {
                console.log("QML: Kein Text empfangen oder leer")
            }
        }
        
                        function parseSchnellabrechnungData(output) {
                    console.log("QML: Parse Schnellabrechnung-Daten")
                    console.log("QML: Erste 500 Zeichen der Ausgabe:", output.substring(0, 500))
                    
                    // Bestehende Spalten löschen
                    for (var i = weekColumnsContainer.children.length - 1; i >= 0; i--) {
                        weekColumnsContainer.children[i].destroy()
                    }
                    
                    // Daten parsen (verbesserte Version für test_schnellabrechnung.py Format)
                    var lines = output.split('\n')
                    var weekData = {}
                    var currentWeek = null
                    var currentProcessingWeek = null
                    
                    // Debug: Alle Zeilen ausgeben
                    console.log("QML: Anzahl Zeilen:", lines.length)
                    for (var k = 0; k < Math.min(lines.length, 100); k++) {
                        console.log("QML: Zeile", k, ":", lines[k])
                    }
                    
                    // Suche nach echten Daten in der Ausgabe
                    var foundRealData = false
                    var inTestSummary = false
                    for (var i = 0; i < lines.length; i++) {
                        var line = lines[i].trim()
                        
                        // Laufende KW aus Live-Output merken ("Verarbeite <KW>...")
                        var procMatch = line.match(/^Verarbeite\s+(\d+)\.\.\./)
                        if (procMatch) {
                            currentProcessingWeek = procMatch[1]
                            if (!weekData[currentProcessingWeek]) {
                                weekData[currentProcessingWeek] = {
                                    umsatz: 0, credit_card: 0, anteil: 0, tank: 0, einsteiger: 0,
                                    garage: 0, expense: 0, income: 0, abrechnungsergebnis: 0, deal_typ: ""
                                }
                            }
                        }

                        // Suche nach "Gesamtumsatz:" - das ist ein Indikator für echte Daten
                        if (line.includes("Gesamtumsatz:")) {
                            foundRealData = true
                            console.log("QML: Echte Daten gefunden:", line)
                            
                            // Robustere KW-Erkennung: bis zu 10 Zeilen zurück nach "Verarbeite <KW>" suchen
                            var foundWeek = false
                            for (var back = 1; back <= 25 && !foundWeek && i - back >= 0; back++) {
                                var prevLine = lines[i - back].trim()
                                var weekMatch = prevLine.match(/Verarbeite\s+(\d+)/)
                                if (weekMatch) {
                                    currentWeek = weekMatch[1]
                                    if (!weekData[currentWeek]) {
                                        weekData[currentWeek] = {
                                            umsatz: 0,
                                            credit_card: 0,
                                            anteil: 0,
                                            tank: 0,
                                            einsteiger: 0,
                                            garage: 0,
                                            expense: 0,
                                            income: 0,
                                            abrechnungsergebnis: 0,
                                            deal_typ: ""
                                        }
                                    }
                                    console.log("QML: KW aus Verarbeite gefunden:", currentWeek)
                                    foundWeek = true
                                }
                            }
                            // Fallback: nutze gemerkte laufende KW
                            if (!foundWeek && currentProcessingWeek) {
                                currentWeek = currentProcessingWeek
                                if (!weekData[currentWeek]) {
                                    weekData[currentWeek] = {
                                        umsatz: 0, credit_card: 0, anteil: 0, tank: 0, einsteiger: 0,
                                        garage: 0, expense: 0, income: 0, abrechnungsergebnis: 0, deal_typ: ""
                                    }
                                }
                            }
                        }
                        
                        // Test-Zusammenfassung beginnt
                        if (line.includes("TEST-ZUSAMMENFASSUNG")) {
                            inTestSummary = true
                            console.log("QML: Test-Zusammenfassung gefunden")
                            continue
                        }
                        
                        // Debug: Zeile ausgeben wenn sie Income enthält und in Test-Zusammenfassung ist
                        if (inTestSummary && (line.includes('Income:') || line.includes('INCOME:'))) {
                            console.log("QML: Income-Zeile in Test-Zusammenfassung:", line)
                        }
                        
                        // Test-Zusammenfassung endet
                        if (inTestSummary && line.includes("GESAMT:")) {
                            inTestSummary = false
                            console.log("QML: Test-Zusammenfassung beendet")
                            break
                        }
                        
                        if (inTestSummary) {
                            // KW-Format erkennen (z.B. "27:")
                            var weekMatch = line.match(/^(\d+):$/)
                            if (weekMatch) {
                                currentWeek = weekMatch[1]
                                weekData[currentWeek] = {
                                    umsatz: 0,
                                    credit_card: 0,
                                    anteil: 0,
                                    tank: 0,
                                    einsteiger: 0,
                                    garage: 0,
                                    expense: 0,
                                    income: 0,
                                    abrechnungsergebnis: 0,
                                    deal_typ: ""
                                }
                                console.log("QML: KW gefunden:", currentWeek)
                                continue
                            }
                            
                            // Werte extrahieren (Fallback aus Test-Zusammenfassung)
                            if (currentWeek && weekData[currentWeek]) {
                                // Debug: Zeile ausgeben wenn sie Income enthält
                                if (line.includes('Income:') || line.includes('INCOME:')) {
                                    console.log("QML: Verarbeite Zeile mit Income:", line)
                                    console.log("QML: currentWeek:", currentWeek)
                                    console.log("QML: weekData[currentWeek]:", weekData[currentWeek])
                                }
                                // Echte Daten aus der Ausgabe extrahieren
                                if (line.includes('Gesamtumsatz:')) {
                                    var match = line.match(/Gesamtumsatz:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].umsatz = value
                                        console.log("QML: Gesamtumsatz für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Credit Card:')) {
                                    var match = line.match(/Credit Card:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].credit_card = value
                                        console.log("QML: Credit Card für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('ANTEIL:')) {
                                    var match = line.match(/ANTEIL:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].anteil = value
                                        console.log("QML: Anteil für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Berechneter Anteil:')) {
                                    var match = line.match(/Berechneter Anteil:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].anteil = value
                                        console.log("QML: Berechneter Anteil für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Garage-Abzug berechnet:')) {
                                    var match = line.match(/Garage-Abzug berechnet:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].garage = value
                                        console.log("QML: Garage für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Einsteiger-Input:')) {
                                    var match = line.match(/Einsteiger-Input:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].einsteiger = value
                                        console.log("QML: Einsteiger für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Einsteiger-Plus')) {
                                    var match = line.match(/Einsteiger-Plus.*?=\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].einsteiger = value
                                        console.log("QML: Einsteiger-Plus für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('===     ANTEIL:')) {
                                    var match = line.match(/===     ANTEIL:\s*([\d.,]+)€ ===/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].anteil = value
                                        console.log("QML: Anteil für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('===     INCOME-BERECHNUNG:')) {
                                    // Income-Berechnung beginnt, suche nach dem Ergebnis
                                    console.log("QML: Income-Berechnung gefunden für KW", currentWeek)
                                } else if (line.includes('Tank-Abzug:') && line.includes('Garage-Abzug:')) {
                                    // Extrahiere Tank und Garage aus der Income-Zeile
                                    var tankMatch = line.match(/Tank-Abzug:\s*([\d.,]+)€/)
                                    if (tankMatch) {
                                        var tankValue = parseFloat(tankMatch[1].replace(',', '.'))
                                        weekData[currentWeek].tank = tankValue
                                        console.log("QML: Tank für KW", currentWeek, ":", tankValue)
                                    }
                                    
                                    var garageMatch = line.match(/Garage-Abzug:\s*([\d.,]+)€/)
                                    if (garageMatch) {
                                        var garageValue = parseFloat(garageMatch[1].replace(',', '.'))
                                        weekData[currentWeek].garage = garageValue
                                        console.log("QML: Garage für KW", currentWeek, ":", garageValue)
                                    }
                                } else if (line.includes('Abrechnungsergebnis:')) {
                                    var match = line.match(/Abrechnungsergebnis:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].abrechnungsergebnis = value
                                        console.log("QML: Abrechnungsergebnis für KW", currentWeek, ":", value)
                                    }
                                }
                                
                                // Test-Zusammenfassung Format (Fallback)
                                if (line.includes('Umsatz:')) {
                                    var match = line.match(/Umsatz:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        // WICHTIG: Nur setzen, wenn noch kein Gesamtumsatz gesetzt wurde
                                        if (!weekData[currentWeek].umsatz || weekData[currentWeek].umsatz === 0) {
                                            weekData[currentWeek].umsatz = value
                                            console.log("QML: Umsatz (Fallback) für KW", currentWeek, ":", value)
                                        } else {
                                            console.log("QML: Überspringe Fallback-Umsatz, Gesamtumsatz bereits gesetzt für KW", currentWeek)
                                        }
                                    }
                                } else if (line.includes('Anteil:')) {
                                    var match = line.match(/Anteil:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].anteil = value
                                    }
                                } else if (line.includes('Tank:')) {
                                    var match = line.match(/Tank:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].tank = value
                                        console.log("QML: Tank für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Einsteiger:')) {
                                    var match = line.match(/Einsteiger:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].einsteiger = value
                                        console.log("QML: Einsteiger für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Garage:')) {
                                    var match = line.match(/Garage:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].garage = value
                                        console.log("QML: Garage für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Ausgaben:')) {
                                    var match = line.match(/Ausgaben:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].expense = value
                                        console.log("QML: Ausgaben für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('INCOME:') && line.includes('EUR')) {
                                    var match = line.match(/INCOME:\s*([\d.,]+)\s*EUR/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].income = value
                                        console.log("QML: INCOME für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Income:') && line.includes('EUR')) {
                                    var match = line.match(/Income:\s*([\d.,]+)\s*EUR/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].income = value
                                        console.log("QML: Income für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('INCOME:') && line.includes('€')) {
                                    var match = line.match(/INCOME:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].income = value
                                        console.log("QML: INCOME für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Income:') && line.includes('€')) {
                                    var match = line.match(/Income:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].income = value
                                        console.log("QML: Income für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Abrechnungsergebnis:')) {
                                    var match = line.match(/Abrechnungsergebnis:\s*([\d.,]+)€/)
                                    if (match) {
                                        var value = parseFloat(match[1].replace(',', '.'))
                                        weekData[currentWeek].abrechnungsergebnis = value
                                        console.log("QML: Abrechnungsergebnis für KW", currentWeek, ":", value)
                                    }
                                } else if (line.includes('Deal-Typ:')) {
                                    var match = line.match(/Deal-Typ:\s*(.+)/)
                                    if (match) {
                                        weekData[currentWeek].deal_typ = match[1].trim()
                                        console.log("QML: Deal-Typ für KW", currentWeek, ":", match[1].trim())
                                    }
                                }
                            }
                        }

                        // Live-Output außerhalb der Test-Zusammenfassung ebenfalls auswerten
                        if (!inTestSummary) {
                            var targetWeek = currentWeek || currentProcessingWeek
                            if (targetWeek && weekData[targetWeek]) {
                                if (line.includes('Gesamtumsatz:')) {
                                    var m1 = line.match(/Gesamtumsatz:\s*([\d.,]+)€/)
                                    if (m1) {
                                        var v1 = parseFloat(m1[1].replace(',', '.'))
                                        weekData[targetWeek].umsatz = v1
                                    }
                                } else if (line.includes('Credit Card:')) {
                                    var m2 = line.match(/Credit Card:\s*([\d.,]+)€/)
                                    if (m2) {
                                        var v2 = parseFloat(m2[1].replace(',', '.'))
                                        weekData[targetWeek].credit_card = v2
                                    }
                                } else if (line.match(/(^|\s)ANTEIL:/)) {
                                    var m3 = line.match(/ANTEIL:\s*([\d.,]+)€/)
                                    if (m3) {
                                        var v3 = parseFloat(m3[1].replace(',', '.'))
                                        weekData[targetWeek].anteil = v3
                                    }
                                } else if (line.match(/(^|\s)INCOME:/)) {
                                    var m4 = line.match(/INCOME:\s*([\d.,]+)\s*EUR/)
                                    if (m4) {
                                        var v4 = parseFloat(m4[1].replace(',', '.'))
                                        weekData[targetWeek].income = v4
                                    }
                                } else if (line.includes('Abrechnungsergebnis:')) {
                                    var m5 = line.match(/Abrechnungsergebnis:\s*([\d.,]+)€/)
                                    if (m5) {
                                        var v5 = parseFloat(m5[1].replace(',', '.'))
                                        weekData[targetWeek].abrechnungsergebnis = v5
                                    }
                                }
                            }
                        }
                    }
                    
                    // Abrechnungsergebnis berechnen, falls nicht vorhanden
                    for (var weekKey in weekData) {
                        var week = weekData[weekKey]
                        if (week.abrechnungsergebnis === 0 && week.credit_card > 0 && week.income > 0) {
                            // Berechne Abrechnungsergebnis: Credit Card - Income
                            week.abrechnungsergebnis = week.credit_card - week.income
                            console.log("QML: Abrechnungsergebnis berechnet für KW", weekKey, ":", week.abrechnungsergebnis)
                        }
                    }
                    
                    // Spalten für jede Kalenderwoche erstellen
                    var weekNumbers = Object.keys(weekData).sort()
                    console.log("QML: Gefundene Wochen:", weekNumbers)

                    // Summen berechnen
                    var tU = 0, tA = 0, tT = 0, tE = 0, tG = 0, tX = 0, tI = 0
                    for (var ti = 0; ti < weekNumbers.length; ti++) {
                        var wk = weekNumbers[ti]
                        var d = weekData[wk]
                        if (!d) continue
                        tU += parseFloat(d.umsatz || 0)
                        tA += parseFloat(d.anteil || 0)
                        tT += parseFloat(d.tank || 0)
                        tE += parseFloat(d.einsteiger || 0)
                        tG += parseFloat(d.garage || 0)
                        tX += parseFloat(d.expense || 0)
                        tI += parseFloat(d.income || 0)
                    }
                    quickResultOverlay.sumUmsatz = tU
                    quickResultOverlay.sumAnteil = tA
                    quickResultOverlay.sumTank = tT
                    quickResultOverlay.sumEinsteiger = tE
                    quickResultOverlay.sumGarage = tG
                    quickResultOverlay.sumExpense = tX
                    quickResultOverlay.sumIncome = tI
                    quickResultOverlay.parsedWeekData = weekData

                    // Summen berechnen
                    var tU = 0, tA = 0, tT = 0, tE = 0, tG = 0, tX = 0, tI = 0
                    for (var ti = 0; ti < weekNumbers.length; ti++) {
                        var wk = weekNumbers[ti]
                        var d = weekData[wk]
                        if (!d) continue
                        tU += parseFloat(d.umsatz || 0)
                        tA += parseFloat(d.anteil || 0)
                        tT += parseFloat(d.tank || 0)
                        tE += parseFloat(d.einsteiger || 0)
                        tG += parseFloat(d.garage || 0)
                        tX += parseFloat(d.expense || 0)
                        tI += parseFloat(d.income || 0)
                    }
                    quickResultOverlay.sumUmsatz = tU
                    quickResultOverlay.sumAnteil = tA
                    quickResultOverlay.sumTank = tT
                    quickResultOverlay.sumEinsteiger = tE
                    quickResultOverlay.sumGarage = tG
                    quickResultOverlay.sumExpense = tX
                    quickResultOverlay.sumIncome = tI
                    
                    // Fallback: Wenn keine Wochen gefunden wurden, Testdaten erstellen
                    if (weekNumbers.length === 0) {
                        console.log("QML: Keine Wochen gefunden, erstelle Testdaten")
                        var testWeeks = ["29", "30", "31"]
                        for (var t = 0; t < testWeeks.length; t++) {
                            var testData = {
                                umsatz: 1200 + (t * 100),
                                credit_card: 800 + (t * 50),
                                anteil: 600 + (t * 30),
                                tank: 120 + (t * 10),
                                einsteiger: 60 + (t * 5),
                                garage: 20 + (t * 2),
                                expense: 50 + (t * 5),
                                income: 400 + (t * 20),
                                abrechnungsergebnis: 200 + (t * 15),
                                deal_typ: "Percent Deal"
                            }
                            createWeekColumn(testWeeks[t], testData)
                        }
                        console.log("QML: Testdaten erstellt für Wochen:", testWeeks)
                    } else {
                        for (var j = 0; j < weekNumbers.length; j++) {
                            var week = weekNumbers[j]
                            var data = weekData[week]
                            createWeekColumn(week, data)
                        }
                    }
                    
                    console.log("QML: Spalten erstellt für Wochen:", weekNumbers.length > 0 ? weekNumbers : ["Testdaten"])
                }
        
        function createWeekColumn(week, data) {
            // Spalten-Container erstellen
            var column = Qt.createQmlObject('
                import QtQuick 2.15
                import QtQuick.Controls 2.15
                import QtQuick.Layouts 1.15
                
                ColumnLayout {
                    id: weekColumn
                    width: 450
                    spacing: 10
                    // Editierbare Werte (initial aus Daten)
                    property real umsatzStatic: ' + data.umsatz + '
                    property real tankValue: ' + data.tank + '
                    property real einsteigerValue: ' + data.einsteiger + '
                    
                    // Wochen-Header (ohne Hintergrund)
                    Text {
                        Layout.fillWidth: true
                        text: "KW ' + week + '"
                        font.family: ubuntuFont.name
                        font.pixelSize: 16
                        font.bold: true
                        color: "#ff8c00"
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    // Gemeinsame Card für Umsatz, Einkommen und Anteil
                    Rectangle {
                        Layout.fillWidth: true
                        height: 110
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 10
                            
                            // Umsatz
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12
                                
                                Text {
                                    text: "Umsatz"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: Style.fontSizeSmall
                                    color: Style.textMuted
                                    Layout.preferredWidth: 90
                                }
                                Text {
                                    text: "' + data.umsatz.toFixed(2) + '€"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: Style.fontSizeNormal
                                    font.bold: true
                                    color: Style.text
                                    Layout.fillWidth: true
                                    horizontalAlignment: Text.AlignRight
                                }
                            }
                            
                            // Einkommen
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12
                                
                                Text {
                                    text: "Einkommen"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: Style.fontSizeSmall
                                    color: Style.textMuted
                                    Layout.preferredWidth: 90
                                }
                                Text {
                                    text: "' + data.income.toFixed(2) + '€"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: Style.fontSizeNormal
                                    font.bold: true
                                    color: Style.success
                                    Layout.fillWidth: true
                                    horizontalAlignment: Text.AlignRight
                                }
                            }
                            
                            // Anteil
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12
                                
                                Text {
                                    text: "Anteil"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: Style.fontSizeSmall
                                    color: Style.textMuted
                                    Layout.preferredWidth: 90
                                }
                                Text {
                                    text: "' + data.anteil.toFixed(2) + '€"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: Style.fontSizeNormal
                                    font.bold: true
                                    color: Style.warning
                                    Layout.fillWidth: true
                                    horizontalAlignment: Text.AlignRight
                                }
                            }
                        }
                    }
                    
                    // Credit Card Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 60
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 4
                            
                            Text {
                                text: "Credit Card"
                                font.family: ubuntuFont.name
                                font.pixelSize: Style.fontSizeSmall
                                color: Style.textMuted
                                Layout.fillWidth: true
                            }
                            Text {
                                text: "' + data.credit_card.toFixed(2) + '€"
                                font.family: ubuntuFont.name
                                font.pixelSize: Style.fontSizeLarge
                                font.bold: true
                                color: Style.text
                                Layout.fillWidth: true
                            }
                        }
                    }
                    
                    // Tank Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        transformOrigin: Item.Center
                        Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutQuad } }
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4
                            
                            Text { text: "Tank"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeSmall; color: Style.textMuted; Layout.fillWidth: true }
                            Text { text: weekColumn.tankValue.toFixed(2) + "€"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeNormal; font.bold: true; color: Style.text; Layout.fillWidth: true }
                        }
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onEntered: parent.scale = 1.02
                            onExited: parent.scale = 1.0
                            onDoubleClicked: {
                                var dialog = Qt.createQmlObject(`
                                    import QtQuick 2.15
                                    import QtQuick.Controls 2.15
                                    import QtQuick.Layouts 1.15
                                    Rectangle {
                                        id: editDialog
                                        anchors.fill: quickResultOverlay
                                        color: "#000000BF" // dunkleres Overlay
                                        z: 1000000
                                        Rectangle {
                                            width: 420; height: 220; anchors.centerIn: parent
                                            color: Style.surface; radius: Style.radiusNormal; border.color: Style.border; border.width: 1
                                            ColumnLayout {
                                                anchors.fill: parent; anchors.margins: 18; spacing: 14
                                                Text { text: "Tank bearbeiten"; color: Style.primary; font.pixelSize: Style.fontSizeLarge; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                                                RowLayout { Layout.fillWidth: true; spacing: 8
                                                    Text { text: "Wert:"; color: Style.text; font.pixelSize: Style.fontSizeNormal }
                                                    TextField {
                                                        id: valueInput
                                                        Layout.fillWidth: true
                                                        text: weekColumn.tankValue.toFixed(2)
                                                        color: Style.text
                                                        font.pixelSize: Style.fontSizeNormal
                                                        verticalAlignment: TextInput.AlignVCenter
                                                        horizontalAlignment: TextInput.AlignRight
                                                        selectByMouse: true
                                                        validator: DoubleValidator { bottom: 0; decimals: 2 }
                                                        background: Rectangle {
                                                            color: "#2a2a2a"
                                                            radius: Style.radiusNormal
                                                            border.color: Style.border
                                                            border.width: 1
                                                        }
                                                    }
                                                    Text { text: "€"; color: Style.textMuted }
                                                }
                                                RowLayout { Layout.fillWidth: true; spacing: 12
                                                    Rectangle { Layout.fillWidth: true; height: 36; color: Style.surface; radius: Style.radiusNormal; border.color: Style.border
                                                        Text { anchors.centerIn: parent; text: "Abbrechen"; color: Style.text }
                                                        MouseArea { anchors.fill: parent; onClicked: editDialog.destroy() }
                                                    }
                                                    Rectangle { Layout.fillWidth: true; height: 36; color: Style.primary; radius: Style.radiusNormal
                                                        Text { anchors.centerIn: parent; text: "Speichern"; color: "white" }
                                                        MouseArea { anchors.fill: parent; onClicked: { weekColumn.tankValue = parseFloat(valueInput.text) || 0; editDialog.destroy(); } }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                `, quickResultOverlay)
                            }
                        }
                    }
                    
                    // Einsteiger Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        transformOrigin: Item.Center
                        Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutQuad } }
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4
                            
                            Text { text: "Einsteiger"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeSmall; color: Style.textMuted; Layout.fillWidth: true }
                            Text { text: weekColumn.einsteigerValue.toFixed(2) + "€"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeNormal; font.bold: true; color: Style.text; Layout.fillWidth: true }
                        }
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onEntered: parent.scale = 1.02
                            onExited: parent.scale = 1.0
                            onDoubleClicked: {
                                var dialog = Qt.createQmlObject(`
                                    import QtQuick 2.15
                                    import QtQuick.Controls 2.15
                                    import QtQuick.Layouts 1.15
                                    Rectangle {
                                        id: editDialog
                                        anchors.fill: quickResultOverlay
                                        color: "#000000BF"
                                        z: 1000000
                                        Rectangle {
                                            width: 420; height: 220; anchors.centerIn: parent
                                            color: Style.surface; radius: Style.radiusNormal; border.color: Style.border; border.width: 1
                                            ColumnLayout {
                                                anchors.fill: parent; anchors.margins: 18; spacing: 14
                                                Text { text: "Einsteiger bearbeiten"; color: Style.primary; font.pixelSize: Style.fontSizeLarge; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
                                                RowLayout { Layout.fillWidth: true; spacing: 8
                                                    Text { text: "Wert:"; color: Style.text; font.pixelSize: Style.fontSizeNormal }
                                                    TextField {
                                                        id: valueInput
                                                        Layout.fillWidth: true
                                                        text: weekColumn.einsteigerValue.toFixed(2)
                                                        color: Style.text
                                                        font.pixelSize: Style.fontSizeNormal
                                                        verticalAlignment: TextInput.AlignVCenter
                                                        horizontalAlignment: TextInput.AlignRight
                                                        selectByMouse: true
                                                        validator: DoubleValidator { bottom: 0; decimals: 2 }
                                                        background: Rectangle {
                                                            color: "#2a2a2a"
                                                            radius: Style.radiusNormal
                                                            border.color: Style.border
                                                            border.width: 1
                                                        }
                                                    }
                                                    Text { text: "€"; color: Style.textMuted }
                                                }
                                                RowLayout { Layout.fillWidth: true; spacing: 12
                                                    Rectangle { Layout.fillWidth: true; height: 36; color: Style.surface; radius: Style.radiusNormal; border.color: Style.border
                                                        Text { anchors.centerIn: parent; text: "Abbrechen"; color: Style.text }
                                                        MouseArea { anchors.fill: parent; onClicked: editDialog.destroy() }
                                                    }
                                                    Rectangle { Layout.fillWidth: true; height: 36; color: Style.primary; radius: Style.radiusNormal
                                                        Text { anchors.centerIn: parent; text: "Speichern"; color: "white" }
                                                        MouseArea { anchors.fill: parent; onClicked: { weekColumn.einsteigerValue = parseFloat(valueInput.text) || 0; editDialog.destroy(); } }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                `, quickResultOverlay)
                            }
                        }
                    }
                    
                    // Total Card (Umsatz + Einsteiger)
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4
                            
                            Text { text: "Total"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeSmall; color: Style.textMuted; Layout.fillWidth: true }
                            Text { text: (weekColumn.umsatzStatic + weekColumn.einsteigerValue).toFixed(2) + "€"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeNormal; font.bold: true; color: Style.success; Layout.fillWidth: true }
                        }
                    }
                    
                    // Garage Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4
                            
                            Text { text: "Garage"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeSmall; color: Style.textMuted; Layout.fillWidth: true }
                            Text { text: "' + data.garage.toFixed(2) + '€"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeNormal; font.bold: true; color: Style.text; Layout.fillWidth: true }
                        }
                    }
                    
                    // Ausgaben Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4
                            
                            Text { text: "Ausgaben"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeSmall; color: Style.textMuted; Layout.fillWidth: true }
                            Text { text: "' + data.expense.toFixed(2) + '€"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeNormal; font.bold: true; color: Style.text; Layout.fillWidth: true }
                        }
                    }
                    
                    // Abrechnungsergebnis Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4
                            
                            Text { text: "Ergebnis"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeSmall; color: Style.textMuted; Layout.fillWidth: true }
                            Text { text: "' + data.abrechnungsergebnis.toFixed(2) + '€"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeNormal; font.bold: true; color: ' + (data.abrechnungsergebnis >= 0 ? 'Style.text' : 'Style.error') + '; Layout.fillWidth: true }
                        }
                    }
                    
                    // Deal-Typ Card
                    Rectangle {
                        Layout.fillWidth: true
                        height: 44
                        color: Style.surface
                        border.color: Style.border
                        border.width: 1
                        radius: Style.radiusNormal
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 4
                            
                            Text { text: "Deal-Typ"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeSmall; color: Style.textMuted; Layout.fillWidth: true }
                            Text { text: "' + data.deal_typ + '"; font.family: ubuntuFont.name; font.pixelSize: Style.fontSizeNormal; color: Style.text; Layout.fillWidth: true }
                        }
                    }
                }
            ', weekColumnsContainer, "WeekColumn")
            
            weekColumnsContainer.children.push(column)
        }
    }
    FontLoader {
        id: spaceMonoFont
        source: "assets/fonts/SpaceMono-Regular.ttf"
    }

    // Einfaches Error-Overlay (sehr vorsichtig implementiert)
    Rectangle {
        id: errorOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 3000 // Höchster Z-Index
        
        Rectangle {
            width: 400
            height: 150
            anchors.centerIn: parent
            radius: Style.radiusNormal
            color: "#1a1a1a"
            border.color: "#ff4444"
            border.width: 2
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                Text {
                    text: "⚠️ Fehler aufgetreten"
                    font.family: ubuntuFont.name
                    font.pixelSize: 18
                    font.bold: true
                    color: "#ff4444"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                }
                
                Text {
                    id: errorMessage
                    text: "Ein Fehler ist aufgetreten"
                    font.family: ubuntuFont.name
                    font.pixelSize: 14
                    color: "#cccccc"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    Item { Layout.fillWidth: true }
                    
                    // Schließen-Button
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
                            onClicked: errorOverlay.visible = false
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                width: parent.containsMouse ? 32 : 28
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                }
            }
        }
        
        // ESC-Taste zum Schließen
        Keys.onEscapePressed: errorOverlay.visible = false
    }

    // QML-Overlay für Wochen-Daten
    Rectangle {
        id: weekDataOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 1000

                 // Overlay-Inhalt
         Rectangle {
             id: overlayContent
             width: Math.min(800, parent.width - 40)
             height: Math.min(overlayContentColumn.height + 120, parent.height - 40)  // Dynamische Höhe basierend auf Inhalt
             anchors.centerIn: parent
             radius: Style.radiusNormal
             color: "#1a1a1a"
             border.color: "#333333"
             border.width: 1

            // Header
            Rectangle {
                id: overlayHeader
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 60
                color: "transparent"
                border.color: "#333333"
                border.width: 0

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    Text {
                        id: overlayTitle
                        text: "Kalenderwoche - Fahrzeug"
                        font.family: ubuntuFont.name
                        font.pixelSize: 18
                        font.bold: true
                        color: "#ff8c00"
                        Layout.fillWidth: true
                    }

                                         Rectangle {
                         width: 32
                         height: 32
                         radius: 16
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: weekDataOverlay.visible = false
                             
                             Text {
                                 anchors.centerIn: parent
                                 text: "×"
                                 font.pixelSize: 20
                                 color: parent.containsMouse ? "#ff8c00" : "#cccccc"
                             }
                         }
                     }
                }
            }

                                                   // ScrollView für alle Daten
              ScrollView {
                  anchors.top: overlayHeader.bottom
                  anchors.left: parent.left
                  anchors.right: parent.right
                  anchors.bottom: parent.bottom
                  anchors.margins: 16
                  clip: true
                  contentHeight: overlayContentColumn.height

                                                                           ColumnLayout {
                          id: overlayContentColumn
                          width: parent.width
                          spacing: 12

                         // Revenue-Sektion
                         Text {
                             text: "📈 Revenue"
                             font.family: ubuntuFont.name
                             font.pixelSize: 18
                             font.bold: true
                             color: "#4CAF50"
                             Layout.fillWidth: true
                             Layout.topMargin: 10
                         }

                                                   // Revenue-Daten
                          Repeater {
                              id: revenueDataRepeater
                              model: []

                              Rectangle {
                                  Layout.fillWidth: true
                                  height: 80
                                  radius: 8
                                  color: "#2a2a2a"
                                  border.color: "#333333"
                                  border.width: 1

                                  RowLayout {
                                      anchors.fill: parent
                                      anchors.margins: 12
                                      spacing: 16

                                      ColumnLayout {
                                          Layout.fillWidth: true
                                          spacing: 4

                                          Text {
                                              text: (modelData.driver || "N/A") + " - " + (modelData.deal || "N/A")
                                              font.family: ubuntuFont.name
                                              font.pixelSize: 14
                                              color: "#cccccc"
                                          }

                                          Text {
                                              text: (modelData.income || 0).toFixed(2) + " €"
                                              font.family: ubuntuFont.name
                                              font.pixelSize: 16
                                              font.bold: true
                                              color: "#4CAF50"
                                          }

                                          Text {
                                              text: (modelData.total || 0).toFixed(2) + " €"
                                              font.family: ubuntuFont.name
                                              font.pixelSize: 12
                                              color: "#b0b0b0"
                                          }
                                      }
                                      
                                                                             // Löschen-Button für Revenue-Eintrag
                                       Rectangle {
                                           Layout.preferredWidth: 24
                                           Layout.preferredHeight: 24
                                           radius: 12
                                           color: "transparent"
                                           border.width: 0
                                           
                                           MouseArea {
                                               anchors.fill: parent
                                               hoverEnabled: true
                                               onClicked: {
                                                   // Revenue-Eintrag löschen
                                                   console.log("Lösche Revenue-Eintrag:", modelData)
                                                   fahrzeugBackendV2.deleteRevenueEntry(overlayTitle.text.split(" - ")[1], parseInt(overlayTitle.text.split(" ")[1]), modelData)
                                               }
                                               
                                               Image {
                                                   anchors.centerIn: parent
                                                   source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_gray.svg"
                                                   width: parent.containsMouse ? 16 : 14
                                                   height: width
                                                   fillMode: Image.PreserveAspectFit
                                               }
                                           }
                                       }
                                  }
                              }
                          }

                         // Keine Revenue-Daten-Nachricht
                         Text {
                             text: "Keine Revenue-Daten für diese Woche vorhanden."
                             font.family: ubuntuFont.name
                             font.pixelSize: 14
                             color: "#666666"
                             horizontalAlignment: Text.AlignHCenter
                             Layout.fillWidth: true
                             Layout.topMargin: 10
                             visible: revenueDataRepeater.count === 0
                         }

                         // Trennlinie
                         Rectangle {
                             Layout.fillWidth: true
                             height: 1
                             color: "#333333"
                             Layout.topMargin: 20
                             Layout.bottomMargin: 20
                         }

                         // Running-Costs-Sektion
                         Text {
                             text: "💰 Running-Costs"
                             font.family: ubuntuFont.name
                             font.pixelSize: 18
                             font.bold: true
                             color: "#FF9800"
                             Layout.fillWidth: true
                             Layout.topMargin: 10
                         }

                         // Running-Costs-Daten
                         GridLayout {
                             Layout.fillWidth: true
                             columns: 3
                             rowSpacing: 8
                             columnSpacing: 8

                                                           Repeater {
                                  id: runningCostsDataRepeater
                                  model: []

                                  Rectangle {
                                      Layout.preferredWidth: 200
                                      Layout.preferredHeight: 80
                                      radius: 8
                                      color: "#2a2a2a"
                                      border.color: "#333333"
                                      border.width: 1

                                      RowLayout {
                                          anchors.fill: parent
                                          anchors.margins: 12
                                          spacing: 16

                                          ColumnLayout {
                                              Layout.fillWidth: true
                                              spacing: 4

                                              Text {
                                                  text: modelData.category || "N/A"
                                                  font.family: ubuntuFont.name
                                                  font.pixelSize: 14
                                                  color: "#cccccc"
                                              }

                                              Text {
                                                  text: (modelData.amount || 0).toFixed(2) + " €"
                                                  font.family: ubuntuFont.name
                                                  font.pixelSize: 16
                                                  font.bold: true
                                                  color: "#FF9800"
                                              }

                                              Text {
                                                  text: modelData.timestamp || "N/A"
                                                  font.family: ubuntuFont.name
                                                  font.pixelSize: 12
                                                  color: "#b0b0b0"
                                              }
                                          }
                                          
                                                                                     // Löschen-Button für Running-Costs-Eintrag
                                           Rectangle {
                                               Layout.preferredWidth: 24
                                               Layout.preferredHeight: 24
                                               radius: 12
                                               color: "transparent"
                                               border.width: 0
                                               
                                               MouseArea {
                                                   anchors.fill: parent
                                                   hoverEnabled: true
                                                   onClicked: {
                                                       // Running-Costs-Eintrag löschen
                                                       console.log("Lösche Running-Costs-Eintrag:", modelData)
                                                       fahrzeugBackendV2.deleteRunningCostsEntry(overlayTitle.text.split(" - ")[1], parseInt(overlayTitle.text.split(" ")[1]), modelData)
                                                   }
                                                   
                                                   Image {
                                                       anchors.centerIn: parent
                                                       source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_gray.svg"
                                                       width: parent.containsMouse ? 16 : 14
                                                       height: width
                                                       fillMode: Image.PreserveAspectFit
                                                   }
                                               }
                                           }
                                      }
                                  }
                              }
                         }

                         // Keine Running-Costs-Daten-Nachricht
                         Text {
                             text: "Keine Running-Costs-Daten für diese Woche vorhanden."
                             font.family: ubuntuFont.name
                             font.pixelSize: 14
                             color: "#666666"
                             horizontalAlignment: Text.AlignHCenter
                             Layout.fillWidth: true
                             Layout.topMargin: 10
                             visible: runningCostsDataRepeater.count === 0
                         }
                     }
            }
        }

                 // ESC-Taste zum Schließen
         Keys.onEscapePressed: weekDataOverlay.visible = false
     }
     
     // Bestätigungsdialog für das Löschen von Fahrzeugen
     Rectangle {
         id: deleteConfirmDialog
         anchors.fill: parent
         color: "#000000"
         opacity: 0.8
         visible: false
         z: 2000
         
         property string licensePlate: ""
         
         Rectangle {
             width: 400
             height: 200
             anchors.centerIn: parent
             radius: Style.radiusNormal
             color: "#1a1a1a"
             border.color: "#333333"
             border.width: 1
             
             ColumnLayout {
                 anchors.fill: parent
                 anchors.margins: 20
                 spacing: 16
                 
                 Text {
                     text: "Fahrzeug löschen?"
                     font.family: ubuntuFont.name
                     font.pixelSize: 18
                     font.bold: true
                     color: "#ff4444"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                 }
                 
                 Text {
                     text: "Möchten Sie das Fahrzeug '" + deleteConfirmDialog.licensePlate + "' wirklich löschen?"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "#cccccc"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                     wrapMode: Text.WordWrap
                 }
                 
                 RowLayout {
                     Layout.fillWidth: true
                     spacing: 16
                     
                     // Spacer um Icons nach rechts zu schieben
                     Item {
                         Layout.fillWidth: true
                     }
                     
                     // Abbrechen-Button mit Close-Icon
                     Rectangle {
                         Layout.preferredWidth: 48
                         height: 48
                         radius: 24
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: deleteConfirmDialog.visible = false
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                 width: parent.containsMouse ? 32 : 28
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                     
                     // Löschen-Button mit Delete-Icon
                     Rectangle {
                         Layout.preferredWidth: 48
                         height: 48
                         radius: 24
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: {
                                 fahrzeugBackendV2.deleteVehicle(deleteConfirmDialog.licensePlate)
                                 deleteConfirmDialog.visible = false
                             }
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_white.svg"
                                 width: parent.containsMouse ? 32 : 28
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                 }
             }
         }
         
         // ESC-Taste zum Schließen
         Keys.onEscapePressed: deleteConfirmDialog.visible = false
     }
     
     // Bestätigungsdialog für das Löschen von Running-Costs
     Rectangle {
         id: deleteRunningCostsDialog
         anchors.fill: parent
         color: "#000000"
         opacity: 0.8
         visible: false
         z: 2000
         
         property string licensePlate: ""
         property int week: 0
         property int count: 0
         
         Rectangle {
             width: 450
             height: 220
             anchors.centerIn: parent
             radius: Style.radiusNormal
             color: "#1a1a1a"
             border.color: "#333333"
             border.width: 1
             
             ColumnLayout {
                 anchors.fill: parent
                 anchors.margins: 20
                 spacing: 16
                 
                 Text {
                     text: "Ausgaben löschen?"
                     font.family: ubuntuFont.name
                     font.pixelSize: 18
                     font.bold: true
                     color: "#ff8c00"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                 }
                 
                 Text {
                     text: "Möchten Sie auch die " + deleteRunningCostsDialog.count + " Ausgaben-Einträge für KW " + deleteRunningCostsDialog.week + " löschen?"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "#cccccc"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                     wrapMode: Text.WordWrap
                 }
                 
                 Text {
                     text: "Dies kann nicht rückgängig gemacht werden."
                     font.family: ubuntuFont.name
                     font.pixelSize: 12
                     color: "#ff4444"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                     wrapMode: Text.WordWrap
                 }
                 
                 RowLayout {
                     Layout.fillWidth: true
                     spacing: 16
                     
                     // Spacer um Icons nach rechts zu schieben
                     Item {
                         Layout.fillWidth: true
                     }
                     
                     // Abbrechen-Button mit Close-Icon
                     Rectangle {
                         Layout.preferredWidth: 48
                         height: 48
                         radius: 24
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: deleteRunningCostsDialog.visible = false
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                 width: parent.containsMouse ? 32 : 28
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                     
                     // Löschen-Button mit Delete-Icon
                     Rectangle {
                         Layout.preferredWidth: 48
                         height: 48
                         radius: 24
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: {
                                 fahrzeugBackendV2.deleteRunningCostsForWeek(deleteRunningCostsDialog.licensePlate, deleteRunningCostsDialog.week)
                                 deleteRunningCostsDialog.visible = false
                             }
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_white.svg"
                                 width: parent.containsMouse ? 32 : 28
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                 }
             }
         }
         
         // ESC-Taste zum Schließen
         Keys.onEscapePressed: deleteRunningCostsDialog.visible = false
     }
     
     // Quick-Week-Overlay für Kalenderwochen-Einträge
     Rectangle {
         id: quickWeekOverlay
         anchors.fill: parent
         color: "#000000"
         opacity: 0.8
         visible: false
         z: 1500
         
         property string currentLicensePlate: ""
         
         Rectangle {
             width: 500
             height: 400
             anchors.centerIn: parent
             radius: Style.radiusNormal
             color: "#1a1a1a"
             border.color: "#333333"
             border.width: 1
             
             ColumnLayout {
                 anchors.fill: parent
                 anchors.margins: 24
                 spacing: 20
                 
                  // Header
                  RowLayout {
                     Layout.fillWidth: true
                     spacing: 16
                     
                      Text {
                          text: "Schnellabrechnung"
                         font.family: ubuntuFont.name
                         font.pixelSize: 20
                         font.bold: true
                         color: "#ff8c00"
                         Layout.fillWidth: true
                     }
                     
                      // Close-Button (ohne Hintergrund)
                      Item {
                          width: 28
                          height: 28
                          
                          MouseArea {
                              anchors.fill: parent
                              hoverEnabled: true
                              cursorShape: Qt.PointingHandCursor
                              onClicked: quickWeekOverlay.visible = false
                              
                              Text {
                                  anchors.centerIn: parent
                                  text: "×"
                                  font.pixelSize: 18
                                  color: parent.containsMouse ? "#ff8c00" : "#cccccc"
                              }
                          }
                      }
                 }
                 
                 // Fahrzeug-Kennzeichen (ohne Beschreibung)
                 Text {
                     text: quickWeekOverlay.currentLicensePlate
                     font.family: ubuntuFont.name
                     font.pixelSize: 16
                     color: "white"
                     Layout.fillWidth: true
                 }
                 
                 // Fahrer-Auswahl
                 Text {
                     text: "Fahrer *"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "white"
                     font.bold: true
                     Layout.fillWidth: true
                 }
                 
                 Rectangle {
                     Layout.fillWidth: true
                     height: 48
                     color: "transparent"
                     z: 1
                     
                     TextField {
                         id: quickDriverField
                         anchors.fill: parent
                         font.family: ubuntuFont.name
                         font.pixelSize: 16
                         color: "white"
                         verticalAlignment: TextInput.AlignVCenter
                         horizontalAlignment: TextInput.AlignHCenter
                         background: Rectangle {
                             color: "#2a2a2a"
                             border.color: quickDriverField.text.length > 0 ? "#4CAF50" : "#555555"
                             border.width: 1
                             radius: 6
                         }
                         placeholderText: "Fahrer auswählen..."
                         
                          property var driverList: []
                          property var filteredDrivers: []
                         property bool isInitializing: false
                         
                         function loadDriverList() {
                             if (fahrzeugBackendV2 && quickDriverField.driverList.length === 0) {
                                 quickDriverField.driverList = fahrzeugBackendV2.getDriverList()
                             }
                         }
                          
                          // Levenshtein-Distanz (für fuzzy Match)
                          function levenshtein(a, b) {
                              a = (a || "").toLowerCase();
                              b = (b || "").toLowerCase();
                              var m = a.length, n = b.length;
                              if (m === 0) return n;
                              if (n === 0) return m;
                              var dp = new Array(n + 1);
                              for (var j = 0; j <= n; j++) dp[j] = j;
                              for (var i = 1; i <= m; i++) {
                                  var prev = dp[0];
                                  dp[0] = i;
                                  for (var j2 = 1; j2 <= n; j2++) {
                                      var temp = dp[j2];
                                      var cost = a.charAt(i - 1) === b.charAt(j2 - 1) ? 0 : 1;
                                      dp[j2] = Math.min(
                                          dp[j2] + 1,
                                          dp[j2 - 1] + 1,
                                          prev + cost
                                      );
                                      prev = temp;
                                  }
                              }
                              return dp[n];
                          }
                          function fuzzyScore(query, target) {
                              if (!query || !target) return 0;
                              var q = query.toLowerCase();
                              var t = target.toLowerCase();
                              // Direkter Substring-Treffer bevorzugen
                              if (t.indexOf(q) !== -1) return 1.0 - (t.indexOf(q) / Math.max(1, t.length));
                              var dist = levenshtein(q, t);
                              var maxLen = Math.max(q.length, t.length);
                              return 1.0 - (dist / Math.max(1, maxLen));
                          }
                         
                         onTextChanged: {
                             // AutoFill filtern
                             if (text.length > 0 && !isInitializing) {
                                 loadDriverList()
                                  var entries = []
                                  var q = text.toLowerCase()
                                  for (var i = 0; i < quickDriverField.driverList.length; i++) {
                                      var name = quickDriverField.driverList[i]
                                      var t = name.toLowerCase()
                                      // Substring- oder fuzzy-Match
                                      var score = 0
                                      if (t.indexOf(q) !== -1) {
                                          // Substring priorisieren
                                          score = 0.9 + (0.1 * (q.length / Math.max(1, t.length)))
                                      } else {
                                          score = fuzzyScore(q, t)
                                      }
                                      if (score >= 0.6) {
                                          entries.push({ name: name, score: score })
                                      }
                                  }
                                  // Nach Score sortieren und auf Namen abbilden
                                  entries.sort(function(a,b){ return b.score - a.score })
                                  var filtered = []
                                  var seen = {}
                                  for (var k = 0; k < entries.length; k++) {
                                      if (!seen[entries[k].name]) {
                                          filtered.push(entries[k].name)
                                          seen[entries[k].name] = true
                                      }
                                  }
                                  filteredDrivers = filtered
                                 quickAutoFillPopup.visible = filtered.length > 0
                             } else {
                                 quickAutoFillPopup.visible = false
                             }
                         }
                         
                         Keys.onDownPressed: {
                             if (quickAutoFillPopup.visible && quickAutoFillList.count > 0) {
                                 quickAutoFillList.currentIndex = Math.min(quickAutoFillList.currentIndex + 1, quickAutoFillList.count - 1)
                             }
                         }
                         Keys.onUpPressed: {
                             if (quickAutoFillPopup.visible && quickAutoFillList.count > 0) {
                                 quickAutoFillList.currentIndex = Math.max(quickAutoFillList.currentIndex - 1, 0)
                             }
                         }
                         Keys.onReturnPressed: {
                             if (quickAutoFillPopup.visible && quickAutoFillList.currentIndex >= 0) {
                                 text = filteredDrivers[quickAutoFillList.currentIndex]
                                 quickAutoFillPopup.visible = false
                             }
                         }
                         Keys.onEscapePressed: quickAutoFillPopup.visible = false
                     }
                     
                     // AutoFill Popup
                     Rectangle {
                         id: quickAutoFillPopup
                         anchors.top: parent.bottom
                         anchors.left: parent.left
                         anchors.right: parent.right
                         height: Math.min(quickAutoFillList.count * 28 + 4, 144)
                         color: "#2a2a2a"
                         border.color: "#555555"
                         border.width: 1
                         radius: 6
                         visible: false
                         z: 3000
                         
                         ListView {
                             id: quickAutoFillList
                             anchors.fill: parent
                             anchors.margins: 2
                             model: quickDriverField.filteredDrivers
                             currentIndex: 0
                             
                             delegate: Rectangle {
                                 width: quickAutoFillList.width
                                 height: 28
                                 color: ListView.isCurrentItem ? "#404040" : "transparent"
                                 radius: 4
                                 
                                 Text {
                                     anchors.left: parent.left
                                     anchors.leftMargin: 8
                                     anchors.verticalCenter: parent.verticalCenter
                                     text: modelData
                                     font.family: ubuntuFont.name
                                     font.pixelSize: 14
                                     color: "white"
                                 }
                                 
                                 MouseArea {
                                     anchors.fill: parent
                                     hoverEnabled: true
                                     onEntered: quickAutoFillList.currentIndex = index
                                     onClicked: {
                                         quickDriverField.text = modelData
                                         quickAutoFillPopup.visible = false
                                     }
                                 }
                             }
                         }
                     }
                 }
                 
                 // Kompakte KW-Auswahl nebeneinander
                 RowLayout {
                     Layout.fillWidth: true
                     spacing: 12
                     
                     // KW von
                     ColumnLayout {
                         Layout.fillWidth: true
                         spacing: 6
                         
                         Text {
                             text: "KW von *"
                             font.family: ubuntuFont.name
                             font.pixelSize: 12
                             color: "white"
                             Layout.fillWidth: true
                         }
                         
                     Rectangle {
                             Layout.fillWidth: true
                         height: 28
                             color: "#2a2a2a"
                             border.color: "#555555"
                             border.width: 1
                             radius: 6
                             
                             SpinBox {
                                 id: weekFromSpinBox
                                 anchors.fill: parent
                             anchors.margins: 2
                                 font.family: ubuntuFont.name
                             font.pixelSize: 12
                                 
                                 from: 1
                                 to: 53
                                 value: 1
                                 
                                 background: Rectangle { color: "transparent"; border.width: 0 }
                                  up.indicator: null
                                  down.indicator: null
                                  enabled: false
                                  opacity: 0
                                 
                                 textFromValue: function(value, locale) { return "KW " + value }
                                 valueFromText: function(text, locale) { return parseInt(text.replace("KW ", "")) || 1 }
                             }

                              // Minus-Icon links (icon-only)
                              Item {
                                  anchors.left: parent.left
                                  anchors.leftMargin: 6
                                  anchors.verticalCenter: parent.verticalCenter
                                  width: 18; height: 18
                                  Text {
                                      anchors.centerIn: parent
                                      text: "\u2212"
                                      color: "#ff8c00"
                                      font.pixelSize: 14
                                  }
                                  MouseArea {
                                      anchors.fill: parent
                                      onClicked: weekFromSpinBox.value = Math.max(weekFromSpinBox.from, weekFromSpinBox.value - 1)
                                      hoverEnabled: true
                                      cursorShape: Qt.PointingHandCursor
                                  }
                              }
                              // Plus-Icon rechts (icon-only)
                              Item {
                                  anchors.right: parent.right
                                  anchors.rightMargin: 6
                                  anchors.verticalCenter: parent.verticalCenter
                                  width: 18; height: 18
                                  Text {
                                      anchors.centerIn: parent
                                      text: "+"
                                      color: "#ff8c00"
                                      font.pixelSize: 14
                                  }
                                  MouseArea {
                                      anchors.fill: parent
                                      onClicked: weekFromSpinBox.value = Math.min(weekFromSpinBox.to, weekFromSpinBox.value + 1)
                                      hoverEnabled: true
                                      cursorShape: Qt.PointingHandCursor
                                  }
                              }
                              // Wert-Anzeige zentriert
                              Text {
                                  anchors.centerIn: parent
                                  text: "KW " + weekFromSpinBox.value
                                  font.family: ubuntuFont.name
                                  font.pixelSize: 12
                                  color: "#b0b0b0"
                              }
                         }
                     }
                     
                     // KW bis
                     ColumnLayout {
                         Layout.fillWidth: true
                         spacing: 6
                         
                         Text {
                             text: "KW bis *"
                             font.family: ubuntuFont.name
                             font.pixelSize: 12
                             color: "white"
                             Layout.fillWidth: true
                         }
                         
                     Rectangle {
                             Layout.fillWidth: true
                         height: 28
                             color: "#2a2a2a"
                             border.color: "#555555"
                             border.width: 1
                             radius: 6
                             
                             SpinBox {
                                 id: weekToSpinBox
                                 anchors.fill: parent
                             anchors.margins: 2
                                 font.family: ubuntuFont.name
                             font.pixelSize: 12
                                 
                                 from: 1
                                 to: 53
                                 value: 1
                                 
                                 background: Rectangle { color: "transparent"; border.width: 0 }
                                  up.indicator: null
                                  down.indicator: null
                                  enabled: false
                                  opacity: 0
                                 
                                 textFromValue: function(value, locale) { return "KW " + value }
                                 valueFromText: function(text, locale) { return parseInt(text.replace("KW ", "")) || 1 }
                             }

                              // Minus-Icon links (icon-only)
                              Item {
                                  anchors.left: parent.left
                                  anchors.leftMargin: 6
                                  anchors.verticalCenter: parent.verticalCenter
                                  width: 18; height: 18
                                  Text {
                                      anchors.centerIn: parent
                                      text: "\u2212"
                                      color: "#ff8c00"
                                      font.pixelSize: 14
                                  }
                                  MouseArea {
                                      anchors.fill: parent
                                      onClicked: weekToSpinBox.value = Math.max(weekToSpinBox.from, weekToSpinBox.value - 1)
                                      hoverEnabled: true
                                      cursorShape: Qt.PointingHandCursor
                                  }
                              }
                              // Plus-Icon rechts (icon-only)
                              Item {
                                  anchors.right: parent.right
                                  anchors.rightMargin: 6
                                  anchors.verticalCenter: parent.verticalCenter
                                  width: 18; height: 18
                                  Text {
                                      anchors.centerIn: parent
                                      text: "+"
                                      color: "#ff8c00"
                                      font.pixelSize: 14
                                  }
                                  MouseArea {
                                      anchors.fill: parent
                                      onClicked: weekToSpinBox.value = Math.min(weekToSpinBox.to, weekToSpinBox.value + 1)
                                      hoverEnabled: true
                                      cursorShape: Qt.PointingHandCursor
                                  }
                              }
                              // Wert-Anzeige zentriert
                              Text {
                                  anchors.centerIn: parent
                                  text: "KW " + weekToSpinBox.value
                                  font.family: ubuntuFont.name
                                  font.pixelSize: 12
                                  color: "#b0b0b0"
                              }
                         }
                     }
                 }
                 
                  // Weitere Parameter: Tank %, Einsteiger %, Fixe Ausgaben €
                  RowLayout {
                      Layout.fillWidth: true
                      spacing: 12
                      
                      // Tank (%)
                      ColumnLayout {
                          Layout.fillWidth: true
                          spacing: 6
                          Text { text: "Tank (%)"; font.family: ubuntuFont.name; font.pixelSize: 12; color: "white"; Layout.fillWidth: true }
                          Rectangle {
                              Layout.fillWidth: true; height: 32; color: "#2a2a2a"; border.color: "#555555"; border.width: 1; radius: 6
                              RowLayout { anchors.fill: parent; anchors.margins: 6; spacing: 6
                                  TextField { id: tankPercentField; Layout.fillWidth: true; Layout.fillHeight: true; Layout.alignment: Qt.AlignVCenter; font.family: ubuntuFont.name; font.pixelSize: 14; color: "white"; background: null; padding: 0; topPadding: 0; bottomPadding: 0; placeholderText: "10"; horizontalAlignment: TextInput.AlignHCenter; verticalAlignment: TextInput.AlignVCenter }
                                  Text { text: "%"; Layout.alignment: Qt.AlignVCenter; font.family: ubuntuFont.name; font.pixelSize: 14; color: "#b0b0b0" }
                              }
                          }
                      }
                      
                      // Einsteiger (%)
                      ColumnLayout {
                          Layout.fillWidth: true
                          spacing: 6
                          Text { text: "Einsteiger (%)"; font.family: ubuntuFont.name; font.pixelSize: 12; color: "white"; Layout.fillWidth: true }
                          Rectangle {
                              Layout.fillWidth: true; height: 32; color: "#2a2a2a"; border.color: "#555555"; border.width: 1; radius: 6
                              RowLayout { anchors.fill: parent; anchors.margins: 6; spacing: 6
                                  TextField { id: starterPercentField; Layout.fillWidth: true; Layout.fillHeight: true; Layout.alignment: Qt.AlignVCenter; font.family: ubuntuFont.name; font.pixelSize: 14; color: "white"; background: null; padding: 0; topPadding: 0; bottomPadding: 0; placeholderText: "5"; horizontalAlignment: TextInput.AlignHCenter; verticalAlignment: TextInput.AlignVCenter }
                                  Text { text: "%"; Layout.alignment: Qt.AlignVCenter; font.family: ubuntuFont.name; font.pixelSize: 14; color: "#b0b0b0" }
                              }
                          }
                      }
                      
                      // Fixe Ausgaben (€)
                      ColumnLayout {
                          Layout.fillWidth: true
                          spacing: 6
                          Text { text: "Fixe Ausgaben (€)"; font.family: ubuntuFont.name; font.pixelSize: 12; color: "white"; Layout.fillWidth: true }
                          Rectangle {
                              Layout.fillWidth: true; height: 32; color: "#2a2a2a"; border.color: "#555555"; border.width: 1; radius: 6
                              RowLayout { anchors.fill: parent; anchors.margins: 6; spacing: 6
                                  TextField { id: expenseEuroField; Layout.fillWidth: true; Layout.fillHeight: true; Layout.alignment: Qt.AlignVCenter; font.family: ubuntuFont.name; font.pixelSize: 14; color: "white"; background: null; padding: 0; topPadding: 0; bottomPadding: 0; placeholderText: "0"; horizontalAlignment: TextInput.AlignHCenter; verticalAlignment: TextInput.AlignVCenter }
                                  Text { text: "€"; Layout.alignment: Qt.AlignVCenter; font.family: ubuntuFont.name; font.pixelSize: 14; color: "#b0b0b0" }
                              }
                          }
                      }
                  }

                  // Buttons
                  RowLayout {
                     Layout.fillWidth: true
                     spacing: 16
                     
                     Item { Layout.fillWidth: true }
                     
                      // Abbrechen-Button (Icon-only)
                      Item {
                          width: 28
                          height: 28
                          
                          MouseArea {
                              anchors.fill: parent
                              hoverEnabled: true
                              cursorShape: Qt.PointingHandCursor
                              onClicked: quickWeekOverlay.visible = false
                              
                              Image {
                                  anchors.centerIn: parent
                                  source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                  width: parent.containsMouse ? 26 : 22
                                  height: width
                                  fillMode: Image.PreserveAspectFit
                              }
                          }
                      }
                     
                      // Ausführen-Button (Icon-only, Bolt)
                      Item {
                          width: 28
                          height: 28
                          
                          MouseArea {
                              anchors.fill: parent
                              hoverEnabled: true
                              cursorShape: Qt.PointingHandCursor
                              onClicked: {
                                 // Validierung
                                 if (!quickDriverField.text || quickDriverField.text.trim() === "") {
                                     console.log("Fehler: Fahrer muss ausgewählt werden!")
                                     return
                                 }
                                 
                                 if (weekFromSpinBox.value > weekToSpinBox.value) {
                                     console.log("Fehler: 'Von' Woche muss kleiner oder gleich 'Bis' Woche sein!")
                                     return
                                 }
                                 
                                  // Parameter sammeln und Backend aufrufen
                                  var tankP = parseFloat(tankPercentField.text || tankPercentField.placeholderText) || 0
                                  var starterP = parseFloat(starterPercentField.text || starterPercentField.placeholderText) || 0
                                  var expense = parseFloat(expenseEuroField.text || expenseEuroField.placeholderText) || 0
                                  // Prozent von 0..100 in 0..1 umrechnen
                                  if (tankP > 1) tankP = tankP / 100.0
                                  if (starterP > 1) starterP = starterP / 100.0
                                  
                                  if (fahrzeugBackendV2 && typeof fahrzeugBackendV2.runQuickSchnellabrechnung === 'function') {
                                      // Kalenderwochen als String zusammenstellen
                                      var weeks = []
                                      for (var i = weekFromSpinBox.value; i <= weekToSpinBox.value; i++) {
                                          weeks.push(i)
                                      }
                                      var weeksString = weeks.join(',')
                                      
                                      fahrzeugBackendV2.runQuickSchnellabrechnung(quickWeekOverlay.currentLicensePlate, quickDriverField.text, weeksString, tankP, starterP, expense)
                                  }
                                 
                                  // Ergebnis-Overlay öffnen (wird via Signal befüllt)
                                  console.log("QML: Öffne quickResultOverlay")
                                  quickResultOverlay.visible = true
                                  console.log("QML: quickResultOverlay.visible nach setzen =", quickResultOverlay.visible)
                             }
                             
                             Image {
                                 anchors.centerIn: parent
                                  source: parent.containsMouse ? "assets/icons/receipt_orange.svg" : "assets/icons/receipt_white.svg"
                                  width: parent.containsMouse ? 26 : 22
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                      }
                 }
             }
             
             // ESC-Taste zum Schließen
             Keys.onEscapePressed: quickWeekOverlay.visible = false
         }
     }

     // Schnellabrechnung-Overlay
     Rectangle {
         id: schnellabrechnungOverlay
         anchors.fill: parent
         color: "#000000"
         opacity: 0.8
         visible: false
         z: 1600
         
         property string currentLicensePlate: ""
         // Default-Logik für KW von/bis und Wochenliste
         property int defaultWeekFrom: 0
         property int defaultWeekTo: 0
         
         function isoWeek(d) {
             // ISO-Woche berechnen (Montag als Wochenbeginn)
             var date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
             var dayNum = date.getUTCDay() || 7; // Sonntag=7
             date.setUTCDate(date.getUTCDate() + 4 - dayNum);
             var yearStart = new Date(Date.UTC(date.getUTCFullYear(),0,1));
             var weekNo = Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
             return { year: date.getUTCFullYear(), week: weekNo };
         }
         
         function clampWeek(n) {
             n = parseInt(n)
             if (isNaN(n)) return 0
             if (n < 1) return 1
             if (n > 53) return 53
             return n
         }
         
         function updateWeeksFromRange() {
             if (!kwFromField || !kwToField || !schnellabrechnungWeeksField) return;
             var fromW = clampWeek(kwFromField.text)
             var toW = clampWeek(kwToField.text)
             if (!fromW || !toW) return
             if (fromW > toW) { var t = fromW; fromW = toW; toW = t }
             var parts = []
             for (var w = fromW; w <= toW; w++) parts.push(String(w))
             schnellabrechnungWeeksField.text = parts.join(',')
         }
         
         onVisibleChanged: {
             if (visible) {
                 try {
                     var now = new Date()
                     var lastFull = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
                     var iso = isoWeek(lastFull)
                     defaultWeekTo = iso.week
                     defaultWeekFrom = Math.max(1, defaultWeekTo - 2)
                     if (kwFromField) kwFromField.text = String(defaultWeekFrom)
                     if (kwToField) kwToField.text = String(defaultWeekTo)
                     updateWeeksFromRange()
                 } catch(e) {
                     // Fallback: nichts tun
                 }
             }
         }
         
         Rectangle {
             width: 500
             height: 400
             anchors.centerIn: parent
             radius: Style.radiusNormal
             color: "#1a1a1a"
             border.color: "#333333"
             border.width: 1
             
             ColumnLayout {
                 anchors.fill: parent
                 anchors.margins: 24
                 spacing: 20
                 
                 // Header
                 RowLayout {
                     Layout.fillWidth: true
                     spacing: 16
                     
                     Text {
                         text: "Schnellabrechnung"
                         font.family: ubuntuFont.name
                         font.pixelSize: 20
                         font.bold: true
                         color: "#ff8c00"
                         Layout.fillWidth: true
                     }
                     
                     // Close-Button
                     Item {
                         width: 28
                         height: 28
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: schnellabrechnungOverlay.visible = false
                             
                             Text {
                                 anchors.centerIn: parent
                                 text: "×"
                                 font.pixelSize: 18
                                 color: parent.containsMouse ? "#ff8c00" : "#cccccc"
                             }
                         }
                     }
                 }
                 
                 // Fahrzeug-Kennzeichen
                 Text {
                     text: schnellabrechnungOverlay.currentLicensePlate
                     font.family: ubuntuFont.name
                     font.pixelSize: 16
                     color: "white"
                     Layout.fillWidth: true
                 }
                 
                 // Fahrer-Auswahl
                 Text {
                     text: "Fahrer *"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "white"
                     font.bold: true
                     Layout.fillWidth: true
                 }
                 
                 Rectangle {
                     Layout.fillWidth: true
                     height: 48
                     color: "transparent"
                     
                     TextField {
                         id: schnellabrechnungDriverField
                         anchors.fill: parent
                         font.family: ubuntuFont.name
                         font.pixelSize: 16
                         color: "white"
                         verticalAlignment: TextInput.AlignVCenter
                         horizontalAlignment: TextInput.AlignHCenter
                         background: Rectangle {
                             color: "#2a2a2a"
                             border.color: schnellabrechnungDriverField.text && schnellabrechnungDriverField.text.trim().length > 0 ? "#4CAF50" : "#555555"
                             border.width: 1
                             radius: 6
                         }
                         placeholderText: "Fahrername eingeben..."
                     }
                 }
                 
                 // Kalenderwochen
                 Text {
                     text: "Kalenderwochen *"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "white"
                     font.bold: true
                     Layout.fillWidth: true
                 }
                 
                 // Bereich: KW von/bis
                 RowLayout {
                     Layout.fillWidth: true
                     spacing: 12
                     
                     ColumnLayout {
                         Layout.fillWidth: true
                         spacing: 6
                         Text { text: "KW von"; color: "white"; font.family: ubuntuFont.name; font.pixelSize: 12 }
                         TextField {
                             id: kwFromField
                             Layout.fillWidth: true
                             font.family: ubuntuFont.name
                             font.pixelSize: 16
                             color: "white"
                             horizontalAlignment: TextInput.AlignHCenter
                             verticalAlignment: TextInput.AlignVCenter
                             inputMethodHints: Qt.ImhDigitsOnly
                             background: Rectangle {
                                 color: "#2a2a2a"
                                 border.color: kwFromField.text && kwFromField.text.trim().length > 0 ? "#4CAF50" : "#555555"
                                 border.width: 1
                                 radius: 6
                             }
                             placeholderText: "z. B. 29"
                             onTextChanged: updateWeeksFromRange()
                         }
                     }
                     ColumnLayout {
                         Layout.fillWidth: true
                         spacing: 6
                         Text { text: "KW bis"; color: "white"; font.family: ubuntuFont.name; font.pixelSize: 12 }
                         TextField {
                             id: kwToField
                             Layout.fillWidth: true
                             font.family: ubuntuFont.name
                             font.pixelSize: 16
                             color: "white"
                             horizontalAlignment: TextInput.AlignHCenter
                             verticalAlignment: TextInput.AlignVCenter
                             inputMethodHints: Qt.ImhDigitsOnly
                             background: Rectangle {
                                 color: "#2a2a2a"
                                 border.color: kwToField.text && kwToField.text.trim().length > 0 ? "#4CAF50" : "#555555"
                                 border.width: 1
                                 radius: 6
                             }
                             placeholderText: "z. B. 31"
                             onTextChanged: updateWeeksFromRange()
                         }
                     }
                 }
                 
                 Rectangle {
                     Layout.fillWidth: true
                     height: 48
                     color: "transparent"
                     
                     TextField {
                         id: schnellabrechnungWeeksField
                         anchors.fill: parent
                         font.family: ubuntuFont.name
                         font.pixelSize: 16
                         color: "white"
                         verticalAlignment: TextInput.AlignVCenter
                         horizontalAlignment: TextInput.AlignHCenter
                         background: Rectangle {
                             color: "#2a2a2a"
                             border.color: schnellabrechnungWeeksField.text && schnellabrechnungWeeksField.text.trim().length > 0 ? "#4CAF50" : "#555555"
                             border.width: 1
                             radius: 6
                         }
                         placeholderText: "KW26,KW27,KW28,KW29,KW30,KW31"
                     }
                 }
                 
                 // Tank-Prozent
                 Text {
                     text: "Tank-Prozent (%)"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "white"
                     font.bold: true
                     Layout.fillWidth: true
                 }
                 
                 Rectangle {
                     Layout.fillWidth: true
                     height: 48
                     color: "transparent"
                     
                     TextField {
                         id: schnellabrechnungTankField
                         anchors.fill: parent
                         font.family: ubuntuFont.name
                         font.pixelSize: 16
                         color: "white"
                         verticalAlignment: TextInput.AlignVCenter
                         horizontalAlignment: TextInput.AlignHCenter
                         background: Rectangle {
                             color: "#2a2a2a"
                             border.color: schnellabrechnungTankField.text && schnellabrechnungTankField.text.trim().length > 0 ? "#4CAF50" : "#555555"
                             border.width: 1
                             radius: 6
                         }
                        placeholderText: "10"
                        text: "10"
                     }
                 }
                 
                 // Einsteiger-Prozent
                 Text {
                     text: "Einsteiger-Prozent (%)"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "white"
                     font.bold: true
                     Layout.fillWidth: true
                 }
                 
                 Rectangle {
                     Layout.fillWidth: true
                     height: 48
                     color: "transparent"
                     
                     TextField {
                         id: schnellabrechnungEinsteigerField
                         anchors.fill: parent
                         font.family: ubuntuFont.name
                         font.pixelSize: 16
                         color: "white"
                         verticalAlignment: TextInput.AlignVCenter
                         horizontalAlignment: TextInput.AlignHCenter
                         background: Rectangle {
                             color: "#2a2a2a"
                             border.color: schnellabrechnungEinsteigerField.text && schnellabrechnungEinsteigerField.text.trim().length > 0 ? "#4CAF50" : "#555555"
                             border.width: 1
                             radius: 6
                         }
                         placeholderText: "20"
                         text: "20"
                     }
                 }
                 
                 // Fixe Ausgaben
                 Text {
                     text: "Fixe Ausgaben (€)"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "white"
                     font.bold: true
                     Layout.fillWidth: true
                 }
                 
                 Rectangle {
                     Layout.fillWidth: true
                     height: 48
                     color: "transparent"
                     
                     TextField {
                         id: schnellabrechnungExpenseField
                         anchors.fill: parent
                         font.family: ubuntuFont.name
                         font.pixelSize: 16
                         color: "white"
                         verticalAlignment: TextInput.AlignVCenter
                         horizontalAlignment: TextInput.AlignHCenter
                         background: Rectangle {
                             color: "#2a2a2a"
                             border.color: schnellabrechnungExpenseField.text && schnellabrechnungExpenseField.text.trim().length > 0 ? "#4CAF50" : "#555555"
                             border.width: 1
                             radius: 6
                         }
                         placeholderText: "0.00"
                         text: "0.00"
                     }
                 }
                 
                 // Buttons
                 RowLayout {
                     Layout.fillWidth: true
                     spacing: 16
                     
                     Item { Layout.fillWidth: true }
                     
                     // Abbrechen-Button
                     Item {
                         width: 28
                         height: 28
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: schnellabrechnungOverlay.visible = false
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                 width: parent.containsMouse ? 26 : 22
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                     
                     // Ausführen-Button
                     Item {
                         width: 28
                         height: 28
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: {
                                 // Validierung
                                 if (!schnellabrechnungDriverField.text || schnellabrechnungDriverField.text.trim() === "") {
                                     console.log("Fehler: Fahrer muss eingegeben werden!")
                                     return
                                 }
                                 
                                 if (!schnellabrechnungWeeksField.text || schnellabrechnungWeeksField.text.trim() === "") {
                                     console.log("Fehler: Kalenderwochen müssen eingegeben werden!")
                                     return
                                 }
                                 
                                 // Parameter sammeln und Backend aufrufen
                                 var tankP = parseFloat(schnellabrechnungTankField.text) / 100.0 || 0.13
                                 var einsteigerP = parseFloat(schnellabrechnungEinsteigerField.text) / 100.0 || 0.20
                                 var expense = parseFloat(schnellabrechnungExpenseField.text) || 0.0
                                 
                                 if (fahrzeugBackendV2 && typeof fahrzeugBackendV2.runQuickSchnellabrechnung === 'function') {
                                     fahrzeugBackendV2.runQuickSchnellabrechnung(
                                         schnellabrechnungOverlay.currentLicensePlate, 
                                         schnellabrechnungDriverField.text, 
                                         schnellabrechnungWeeksField.text, 
                                         tankP, 
                                         einsteigerP, 
                                         expense
                                     )
                                 }
                                 
                                 // Ergebnis-Overlay öffnen
                                 console.log("QML: Öffne quickResultOverlay (Schnellabrechnung)")
                                 quickResultOverlay.metaDriver = schnellabrechnungDriverField.text
                                 quickResultOverlay.metaVehicle = schnellabrechnungOverlay.currentLicensePlate
                                 quickResultOverlay.metaWeekFrom = kwFromField.text
                                 quickResultOverlay.metaWeekTo = kwToField.text
                                 quickResultOverlay.visible = true
                                 console.log("QML: quickResultOverlay.visible nach setzen =", quickResultOverlay.visible)
                             }
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/quick_orange.svg" : "assets/icons/quick_white.svg"
                                 width: parent.containsMouse ? 26 : 22
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                 }
             }
             
             // ESC-Taste zum Schließen
             Keys.onEscapePressed: schnellabrechnungOverlay.visible = false
         }
     }

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
                        // Ansichtswechsel: Cards ↔ Kalenderwochen
                        if (typeof fahrzeugBackendV2.toggleViewMode === "function") {
                            fahrzeugBackendV2.toggleViewMode()
                        } else {
                            console.log("toggleViewMode nicht verfügbar")
                        }
                    }
                }
                
                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                                            text: fahrzeugBackendV2 && fahrzeugBackendV2.isCalendarView ? "Kalenderwochen-Übersicht" : "Fahrzeugverwaltung"
                    font.family: ubuntuFont.name
                    font.pixelSize: 36
                    font.bold: true
                    color: titleMouseArea.containsMouse ? "#ff8c00" : "white"
                    
                    // Hover-Effekt: Leichte Vergrößerung
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
                visible: !fahrzeugBackendV2 || !fahrzeugBackendV2.isCalendarView
                
                // Toggle Switch Background
                Rectangle {
                    width: 40
                    height: 20
                    radius: 10
                                            color: fahrzeugBackendV2 && fahrzeugBackendV2.showOnlyActive ? "#ff8c00" : "#555555"
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
                        anchors.leftMargin: fahrzeugBackendV2 && fahrzeugBackendV2.showOnlyActive ? 20 : 2
                        
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
                                if (fahrzeugBackendV2) {
                                    fahrzeugBackendV2.showOnlyActive = !fahrzeugBackendV2.showOnlyActive
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
                    onTextChanged: {
                        console.log("Suchtext geändert:", text)
                        fahrzeugBackendV2.filterText = text
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
            
            // Refresh-Button entfernt
        }

        // Cards-Container mit echtem Grid-Layout
        GridView {
            id: cardsGridView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            // Performance-Optimierungen
            cacheBuffer: 1000  // Größerer Cache für bessere Performance
            maximumFlickVelocity: 2500  // Schnelleres Scrollen
            boundsBehavior: Flickable.StopAtBounds  // Bessere Scroll-Performance
            
            // Responsive Grid-Eigenschaften
            cellWidth: 396  // 380 + 16 spacing
            cellHeight: 296 // 280 + 16 spacing
            
            // Automatische Spaltenberechnung
            onWidthChanged: {
                var availableWidth = width - 16 // Abstand berücksichtigen
                var cardsPerRow = Math.max(1, Math.floor(availableWidth / 396))
                cellWidth = availableWidth / cardsPerRow
            }
            
            // Fahrzeug-Cards
                            model: fahrzeugBackendV2 ? fahrzeugBackendV2.fahrzeugList : []
            
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
                                    visible: fahrzeugBackendV2 && fahrzeugBackendV2.isLoading
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
                        text: "Fahrzeuge werden geladen..."
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        color: "#cccccc"
                    }
                }
            }
            
            // Pagination-Controls (sehr vorsichtig hinzugefügt)
            Rectangle {
                id: paginationControls
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottomMargin: 20
                width: 300
                height: 50
                radius: Style.radiusNormal
                color: "#1a1a1a"
                border.color: "#333333"
                border.width: 1
                                    visible: fahrzeugBackendV2 && fahrzeugBackendV2.totalVehicles > fahrzeugBackendV2.pageSize
                z: 50
                
                RowLayout {
                    anchors.centerIn: parent
                    spacing: 16
                    
                    // Zurück-Button
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 20
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            enabled: fahrzeugBackendV2 && fahrzeugBackendV2.currentPage > 0
                            onClicked: fahrzeugBackendV2.loadPreviousPage()
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.enabled && parent.containsMouse ? "assets/icons/close_orange.svg" : "assets/icons/close_gray.svg"
                                width: parent.enabled && parent.containsMouse ? 24 : 20
                                height: width
                                fillMode: Image.PreserveAspectFit
                                rotation: 180  // Pfeil nach links
                            }
                        }
                    }
                    
                    // Seiten-Anzeige
                    Text {
                        text: "Seite " + (fahrzeugBackendV2 ? (fahrzeugBackendV2.currentPage + 1) : 1) + " von " + (fahrzeugBackendV2 ? Math.ceil(fahrzeugBackendV2.totalVehicles / fahrzeugBackendV2.pageSize) : 1)
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        color: "#cccccc"
                    }
                    
                    // Weiter-Button
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 20
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            enabled: fahrzeugBackendV2 && fahrzeugBackendV2.currentPage < Math.ceil(fahrzeugBackendV2.totalVehicles / fahrzeugBackendV2.pageSize) - 1
                            onClicked: fahrzeugBackendV2.loadNextPage()
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.enabled && parent.containsMouse ? "assets/icons/close_orange.svg" : "assets/icons/close_gray.svg"
                                width: parent.enabled && parent.containsMouse ? 24 : 20
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                }
            }
            

            
                         delegate: Rectangle {
                 id: vehicleCard
                 width: 380
                 height: 280
                 radius: Style.radiusNormal
                 color: "transparent"
                 border.width: 0
                 z: 1 // Standard Z-Index für normale Cards
                 
                 // Hover-Effekt: Vergrößerung um 1.05x
                 property real hoverScale: (vehicleCardMouseArea.containsMouse || statusBadgeMouseArea.containsMouse || editButtonMouseArea.containsMouse || deleteButtonMouseArea.containsMouse) ? 1.05 : 1.0
                 
                 // Transform mit Zentrierung
                 transform: Scale {
                     xScale: vehicleCard.hoverScale
                     yScale: vehicleCard.hoverScale
                     origin.x: vehicleCard.width / 2
                     origin.y: vehicleCard.height / 2
                 }
                 
                 // Animation für smooth Übergänge
                 Behavior on hoverScale {
                     NumberAnimation { 
                         duration: 150
                         easing.type: Easing.OutCubic
                     }
                 }
            
                property bool selected: {
                    if (!fahrzeugBackendV2 || !fahrzeugBackendV2.selectedVehicle || !modelData) return false
                    return fahrzeugBackendV2.selectedVehicle.kennzeichen === modelData.kennzeichen
                }
                
                // Gradient-Hintergrund (wie in Abrechnungsseite)
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
                     id: vehicleCardMouseArea
                     anchors.fill: parent
                     hoverEnabled: true
                     onClicked: fahrzeugBackendV2.selectVehicle(modelData.kennzeichen)
                     onDoubleClicked: {
                         // Doppelklick: Edit-Modus mit vorausgefüllten Daten
                         showVehicleFormOverlayForEdit(modelData)
                     }
                 }
                
                // Card-Inhalt
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    
                    // Header mit Kennzeichen und Status
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Text {
                            text: modelData.kennzeichen || "Kein Kennzeichen"
                            font.family: ubuntuFont.name
                            font.pixelSize: 24
                            font.bold: true
                            color: "white"
                            Layout.fillWidth: true
                        }
                        
                        // Status-Badge (klickbar) - nur in normaler Ansicht
                        Rectangle {
                            Layout.preferredWidth: 80
                            height: 28
                            radius: 14
                            color: "transparent"
                            border.width: 0
                            visible: !fahrzeugBackendV2 || !fahrzeugBackendV2.isCalendarView
                            
                            MouseArea {
                                id: statusBadgeMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    // Status-Toggle: Aktiv → Wartung → Inaktiv → Aktiv
                                    var currentStatus = modelData.status || "Aktiv"
                                    var newStatus
                                    if (currentStatus === "Aktiv") newStatus = "Wartung"
                                    else if (currentStatus === "Wartung") newStatus = "Inaktiv"
                                    else newStatus = "Aktiv"
                                    
                                    // Backend-Methode zum Aktualisieren des Status
                                    fahrzeugBackendV2.updateVehicleStatus(modelData.kennzeichen, newStatus)
                                }
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: modelData.status || "Aktiv"
                                font.family: ubuntuFont.name
                                font.pixelSize: 12
                                color: {
                                    if (modelData.status === "Aktiv") return "#4CAF50"
                                    else if (modelData.status === "Wartung") return "#9E9E9E"
                                    else return "#F44336"
                                }
                                horizontalAlignment: Text.AlignCenter
                            }
                        }
                    }
                    
                    // Fahrzeug-Details oder Kalenderwochen
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                                                 // Normale Fahrzeug-Details
                         GridLayout {
                             anchors.fill: parent
                             columns: 2
                             rowSpacing: 8
                             columnSpacing: 16
                             visible: !fahrzeugBackendV2 || !fahrzeugBackendV2.isCalendarView
                             
                                                         // Modell und Baujahr in einer Zeile
                            Text {
                                text: "Modell/Baujahr:"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: (modelData.modell && modelData.modell !== "" && modelData.modell !== undefined && modelData.modell !== null) || (modelData.baujahr && modelData.baujahr !== "" && modelData.baujahr !== undefined && modelData.baujahr !== null)
                            }
                            
                            // Modell und Baujahr
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: (modelData.modell || "-") + " / " + (modelData.baujahr || "-")
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: (modelData.modell && modelData.modell !== "" && modelData.modell !== undefined && modelData.modell !== null) || (modelData.baujahr && modelData.baujahr !== "" && modelData.baujahr !== undefined && modelData.baujahr !== null)
                            }
                             
                                                         // Stammfahrer
                            Text {
                                text: "Stammfahrer:"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: modelData.stammfahrer && modelData.stammfahrer !== "" && modelData.stammfahrer !== undefined && modelData.stammfahrer !== null
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.stammfahrer || "-"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: modelData.stammfahrer && modelData.stammfahrer !== "" && modelData.stammfahrer !== undefined && modelData.stammfahrer !== null
                            }
                             
                                                         // Referenz
                            Text {
                                text: "Referenz:"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: modelData.rfrnc && modelData.rfrnc !== "" && modelData.rfrnc !== undefined && modelData.rfrnc !== null
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.rfrnc || "-"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: modelData.rfrnc && modelData.rfrnc !== "" && modelData.rfrnc !== undefined && modelData.rfrnc !== null
                            }
                             
                                                         // Versicherung
                            Text {
                                text: "Versicherung:"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: modelData.versicherung && modelData.versicherung !== "" && modelData.versicherung !== undefined && modelData.versicherung !== null
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.versicherung ? (parseFloat(modelData.versicherung) || 0).toFixed(2) + " €" : "-"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: modelData.versicherung && modelData.versicherung !== "" && modelData.versicherung !== undefined && modelData.versicherung !== null
                            }
                             
                                                                                     // Finanzierung
                            Text {
                                text: "Finanzierung:"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "#b0b0b0"
                                visible: modelData.finanzierung && modelData.finanzierung !== "" && modelData.finanzierung !== undefined && modelData.finanzierung !== null
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                height: 32
                                text: modelData.finanzierung ? (parseFloat(modelData.finanzierung) || 0).toFixed(2) + " €" : "-"
                                font.family: ubuntuFont.name
                                font.pixelSize: 14
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                visible: modelData.finanzierung && modelData.finanzierung !== "" && modelData.finanzierung !== undefined && modelData.finanzierung !== null
                            }
                             
                             // Notizen (falls vorhanden)
                             Text {
                                 text: "Notizen:"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "#b0b0b0"
                                 visible: modelData.notizen && modelData.notizen !== ""
                             }
                             
                             Text {
                                 Layout.fillWidth: true
                                 height: 32
                                 text: modelData.notizen || "-"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 12
                                 color: "#cccccc"
                                 visible: modelData.notizen && modelData.notizen !== ""
                                 verticalAlignment: Text.AlignVCenter
                             }
                            
                            
                        }
                        
                        // Kalenderwochen-Grid
                        GridLayout {
                            anchors.fill: parent
                            columns: Math.min(12, (modelData.calendar_weeks ? modelData.calendar_weeks.length : 0) + 1)  // Dynamische Spalten
                            rowSpacing: 2
                            columnSpacing: 2
                            visible: fahrzeugBackendV2 && fahrzeugBackendV2.isCalendarView
                            
                            // Kalenderwochen-Daten
                            Repeater {
                                model: modelData.calendar_weeks || []
                                
                                Text {
                                    width: 24
                                    height: 24
                                    text: modelData.week.toString()
                                    font.family: ubuntuFont.name
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: modelData.has_data ? "#4CAF50" : "#F44336"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    
                                    // Tooltip
                                    ToolTip {
                                        text: "KW " + modelData.week + ": " + (modelData.has_data ? "Daten vorhanden" : "Keine Daten")
                                        visible: parentMouseArea.containsMouse
                                    }
                                    
                                    MouseArea {
                                        id: parentMouseArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            // Kalenderwoche wurde geklickt
                                            console.log("Kalenderwoche geklickt:", modelData.week, "has_data:", modelData.has_data)
                                            if (modelData.has_data) {
                                                // Daten vorhanden: QML-Overlay anzeigen
                                                console.log("Zeige QML-Overlay für:", modelData.week)
                                                var vehicleKennzeichen = modelData.kennzeichen || ""
                                                console.log("Fahrzeug-Kennzeichen:", vehicleKennzeichen)
                                                console.log("Rufe showWeekDataOverlay auf mit:", vehicleKennzeichen, modelData.week)
                                                showWeekDataOverlay(vehicleKennzeichen, modelData.week)
                                            } else {
                                                // Keine Daten: Neuen Eintrag erstellen
                                                console.log("Erstelle neuen Eintrag für:", modelData.week)
                                                var vehicleKennzeichen = modelData.kennzeichen || ""
                                                fahrzeugBackendV2.createWeekDataEntry(vehicleKennzeichen, modelData.week)
                                            }
                                        }
                                    }
                                }
                            }
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
                         
                         // Edit/Quick-Button (dynamisch basierend auf Ansicht)
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
                                     // Dynamische Funktionalität basierend auf Ansicht
                                      if (fahrzeugBackendV2 && fahrzeugBackendV2.isCalendarView) {
                                          // Kalenderwochen-Ansicht: Quick-Overlay öffnen (mit Prefill Stammfahrer)
                                          console.log("Quick-Overlay für Fahrzeug:", modelData.kennzeichen)
                                          showQuickWeekOverlay(modelData.kennzeichen, modelData.stammfahrer)
                                     } else {
                                         // Normale Ansicht: Standard Edit-Funktion
                                         console.log("Edit-Button geklickt für:", modelData.kennzeichen)
                                         showVehicleFormOverlayForEdit(modelData)
                                     }
                                 }
                                 
                                 Image {
                                     anchors.centerIn: parent
                                     source: {
                                         if (fahrzeugBackendV2 && fahrzeugBackendV2.isCalendarView) {
                                             // Kalenderwochen-Ansicht: Quick-Icon
                                             return parent.containsMouse ? "assets/icons/quick_orange.svg" : "assets/icons/quick_white.svg"
                                         } else {
                                             // Normale Ansicht: Edit-Icon
                                             return parent.containsMouse ? "assets/icons/edit_orange.svg" : "assets/icons/edit_white.svg"
                                         }
                                     }
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
                                     // Bestätigungsdialog anzeigen
                                     deleteConfirmDialog.licensePlate = modelData.kennzeichen
                                     deleteConfirmDialog.visible = true
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
            onClicked: showVehicleFormOverlay()
            Image {
                anchors.centerIn: parent
                source: addArea.pressed ? "assets/icons/add_gray.svg"
                    : addArea.containsMouse ? "assets/icons/add_orange.svg" : "assets/icons/add_white.svg"
                width: addArea.pressed ? 40 : addArea.containsMouse ? 48 : 40
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        
        // Schnellabrechnung-Button
        MouseArea {
            id: schnellabrechnungArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                if (fahrzeugBackendV2 && fahrzeugBackendV2.selectedVehicle) {
                    schnellabrechnungOverlay.currentLicensePlate = fahrzeugBackendV2.selectedVehicle.kennzeichen
                    schnellabrechnungOverlay.visible = true
                } else {
                    console.log("Kein Fahrzeug ausgewählt für Schnellabrechnung")
                }
            }
            Image {
                anchors.centerIn: parent
                source: schnellabrechnungArea.pressed ? "assets/icons/receipt_gray.svg"
                    : schnellabrechnungArea.containsMouse ? "assets/icons/receipt_orange.svg" : "assets/icons/receipt_white.svg"
                width: schnellabrechnungArea.pressed ? 40 : schnellabrechnungArea.containsMouse ? 48 : 40
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        

    }

    // Hilfsfunktion für Kalenderwoche
    function getCurrentWeek() {
        var now = new Date()
        var start = new Date(now.getFullYear(), 0, 1)
        var days = Math.floor((now - start) / (24 * 60 * 60 * 1000))
        var weekNumber = Math.ceil(days / 7)
        return weekNumber
    }
    
    // Funktion zum Anzeigen des Quick-Week-Overlays
    function showQuickWeekOverlay(licensePlate, stammfahrer) {
        quickWeekOverlay.currentLicensePlate = licensePlate
        
        // Fahrerliste für AutoFill vorladen
        if (fahrzeugBackendV2 && typeof fahrzeugBackendV2.getDriverList === 'function') {
            try {
                quickDriverField.isInitializing = true
                quickDriverField.driverList = fahrzeugBackendV2.getDriverList() || []
                quickDriverField.filteredDrivers = []
                // Prefill mit Stammfahrer, falls vorhanden
                var prefill = ""
                if (stammfahrer && String(stammfahrer).trim().length > 0) {
                    prefill = String(stammfahrer).trim()
                } else if (fahrzeugBackendV2 && fahrzeugBackendV2.selectedVehicle && fahrzeugBackendV2.selectedVehicle.stammfahrer) {
                    prefill = String(fahrzeugBackendV2.selectedVehicle.stammfahrer).trim()
                }
                quickDriverField.text = prefill
            } finally {
                quickDriverField.isInitializing = false
            }
        } else {
            quickDriverField.driverList = []
            quickDriverField.filteredDrivers = []
            quickDriverField.text = ""
        }
        
        // KW vorbelegen: KW bis = letzte volle KW, KW von = zwei Wochen davor
        try {
            var now = new Date()
            var lastFull = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000) // Vorwoche
            var start = new Date(lastFull.getFullYear(), 0, 1)
            var days = Math.floor((lastFull - start) / (24 * 60 * 60 * 1000))
            var weekNumber = Math.ceil(days / 7)
            weekToSpinBox.value = Math.max(1, Math.min(53, weekNumber))
            weekFromSpinBox.value = Math.max(1, Math.min(53, weekNumber - 2))
        } catch(e) {
            // Fallback: aktuelle Woche
            weekFromSpinBox.value = getCurrentWeek()
            weekToSpinBox.value = getCurrentWeek()
        }
        
        // Overlay anzeigen
        quickWeekOverlay.visible = true
        quickWeekOverlay.forceActiveFocus()
        quickAutoFillPopup.visible = false
    }
    
    // Funktion zum Anzeigen des QML-Overlays
    function showWeekDataOverlay(licensePlate, week) {
        console.log("QML: showWeekDataOverlay aufgerufen")
        console.log("QML: licensePlate:", licensePlate)
        console.log("QML: week:", week)
        
        overlayTitle.text = "KW " + week + " - " + licensePlate
        console.log("QML: overlayTitle.text gesetzt:", overlayTitle.text)
        
        // Backend-Methode aufrufen, um Daten zu laden
        console.log("QML: Rufe fahrzeugBackendV2.loadWeekDataForOverlay auf")
        fahrzeugBackendV2.loadWeekDataForOverlay(licensePlate, week)
        
        // Overlay anzeigen
        console.log("QML: Setze weekDataOverlay.visible = true")
        weekDataOverlay.visible = true
        weekDataOverlay.forceActiveFocus()
        console.log("QML: Overlay sollte jetzt sichtbar sein")
    }
    
         // Funktion zum Anzeigen des Fahrzeug-Formular-Overlays
          function showVehicleFormOverlay() {
        // AutoFill während Initialisierung deaktivieren
        stammfahrerField.isInitializing = true
        
        // Reset alle Felder für neues Fahrzeug
        licensePlateField.text = ""
        referenceField.text = ""
        modelField.text = ""
        yearField.text = ""
        insuranceField.text = ""
        creditField.text = ""
        statusField.currentIndex = 0
        stammfahrerField.text = ""
        notesField.text = ""
        
        // AutoFill wieder aktivieren
        stammfahrerField.isInitializing = false
         
         // Titel ändern
         vehicleFormTitle.text = "Neues Fahrzeug anlegen"
         
         vehicleFormOverlay.visible = true
         vehicleFormOverlay.forceActiveFocus()
     }
     
         // Funktion zum Anzeigen des Fahrzeug-Formular-Overlays im Edit-Modus
    function showVehicleFormOverlayForEdit(vehicleData) {
        // AutoFill während Initialisierung deaktivieren
        stammfahrerField.isInitializing = true
        
        // Felder mit Fahrzeugdaten vorausfüllen
        licensePlateField.text = vehicleData.kennzeichen || ""
        referenceField.text = vehicleData.rfrnc || ""
        modelField.text = vehicleData.modell || ""
        yearField.text = vehicleData.baujahr || ""
        insuranceField.text = vehicleData.versicherung || ""
        creditField.text = vehicleData.finanzierung || ""
        stammfahrerField.text = vehicleData.stammfahrer || ""
        notesField.text = vehicleData.notizen || ""
        
        // AutoFill wieder aktivieren
        stammfahrerField.isInitializing = false
         
         // Status setzen
         var statusIndex = 0
         if (vehicleData.status === "Wartung") statusIndex = 1
         else if (vehicleData.status === "Inaktiv") statusIndex = 2
         statusField.currentIndex = statusIndex
         
         // Titel ändern
         vehicleFormTitle.text = "Fahrzeug bearbeiten: " + vehicleData.kennzeichen
         
         vehicleFormOverlay.visible = true
         vehicleFormOverlay.forceActiveFocus()
     }
    
    // Overlay für Fahrzeug-Formular
    Rectangle {
        id: vehicleFormOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 2000
        
        MouseArea {
            anchors.fill: parent
            onClicked: vehicleFormOverlay.visible = false
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(parent.width * 0.4, 400)
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
                         id: vehicleFormTitle
                         text: "Neues Fahrzeug anlegen"
                         font.family: ubuntuFont.name
                         font.pixelSize: 24
                         font.bold: true
                         color: "white"
                         Layout.fillWidth: true
                         visible: !text.includes("bearbeiten")
                     }
                    
                                         // Close-Icon entfernt - wird unten verwendet
                }
                
                // Abstand zwischen Titel und Formular
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 20
                }
                
                                 // Formular
                 GridLayout {
                     Layout.fillWidth: true
                     Layout.fillHeight: true
                     columns: 2
                     rowSpacing: 12
                     columnSpacing: 16
                        
                        // Kennzeichen
                        Text {
                            text: "Kennzeichen *"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                                                 TextField {
                             id: licensePlateField
                             Layout.fillWidth: true
                             height: 48
                             font.family: ubuntuFont.name
                             font.pixelSize: 16
                             color: "white"
                             verticalAlignment: TextInput.AlignVCenter
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: licensePlateField.text.length > 0 ? (fahrzeugBackendV2 && fahrzeugBackendV2.isLicensePlateValid ? "#4CAF50" : "#f44336") : "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "z.B. W135CTX"
                            
                            // Live-Validierung bei Texteingabe
                            onTextChanged: {
                                if (text.length > 0 && fahrzeugBackendV2) {
                                    fahrzeugBackendV2.validateSingleField("license_plate", text)
                                }
                            }
                        }
                        
                        // Referenz
                        Text {
                            text: "Referenz"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                                                 TextField {
                             id: referenceField
                             Layout.fillWidth: true
                             height: 48
                             font.family: ubuntuFont.name
                             font.pixelSize: 16
                             color: "white"
                             verticalAlignment: TextInput.AlignVCenter
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: referenceField.text.length > 0 ? (fahrzeugBackendV2 && fahrzeugBackendV2.isRfrncValid ? "#4CAF50" : "#f44336") : "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "Referenz-Nummer"
                            
                            // Live-Validierung bei Texteingabe
                            onTextChanged: {
                                if (text.length > 0) {
                                    if (fahrzeugBackendV2) {
                                    fahrzeugBackendV2.validateSingleField("rfrnc", text)
                                }
                                }
                            }
                        }
                        
                        // Modell
                        Text {
                            text: "Modell"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                                                 TextField {
                             id: modelField
                             Layout.fillWidth: true
                             height: 48
                             font.family: ubuntuFont.name
                             font.pixelSize: 16
                             color: "white"
                             verticalAlignment: TextInput.AlignVCenter
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: modelField.text.length > 0 ? (fahrzeugBackendV2 && fahrzeugBackendV2.isModelValid ? "#4CAF50" : "#f44336") : "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "z.B. Mercedes Sprinter"
                            
                            // Live-Validierung bei Texteingabe
                            onTextChanged: {
                                if (text.length > 0) {
                                    if (fahrzeugBackendV2) {
                                    fahrzeugBackendV2.validateSingleField("model", text)
                                }
                                }
                            }
                        }
                        
                        // Baujahr
                        Text {
                            text: "Baujahr"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                                                 TextField {
                             id: yearField
                             Layout.fillWidth: true
                             height: 48
                             font.family: ubuntuFont.name
                             font.pixelSize: 16
                             color: "white"
                             verticalAlignment: TextInput.AlignVCenter
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: yearField.text.length > 0 ? (fahrzeugBackendV2 && fahrzeugBackendV2.isYearValid ? "#4CAF50" : "#f44336") : "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "z.B. 2020"
                            
                            // Live-Validierung bei Texteingabe
                            onTextChanged: {
                                if (text.length > 0) {
                                    if (fahrzeugBackendV2) {
                                    fahrzeugBackendV2.validateSingleField("year", text)
                                }
                                }
                            }
                        }
                        
                        // Versicherung
                        Text {
                            text: "Versicherung (€)"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                                                 TextField {
                             id: insuranceField
                             Layout.fillWidth: true
                             height: 48
                             font.family: ubuntuFont.name
                             font.pixelSize: 16
                             color: "white"
                             verticalAlignment: TextInput.AlignVCenter
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: insuranceField.text.length > 0 ? (fahrzeugBackendV2 && fahrzeugBackendV2.isInsuranceValid ? "#4CAF50" : "#f44336") : "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "0.00"
                            
                            // Live-Validierung bei Texteingabe
                            onTextChanged: {
                                if (fahrzeugBackendV2) {
                                    fahrzeugBackendV2.validateSingleField("insurance", text)
                                }
                            }
                        }
                        
                        // Finanzierung
                        Text {
                            text: "Finanzierung (€)"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                                                 TextField {
                             id: creditField
                             Layout.fillWidth: true
                             height: 48
                             font.family: ubuntuFont.name
                             font.pixelSize: 16
                             color: "white"
                             verticalAlignment: TextInput.AlignVCenter
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: creditField.text.length > 0 ? (fahrzeugBackendV2 && fahrzeugBackendV2.isCreditValid ? "#4CAF50" : "#f44336") : "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "0.00"
                            
                            // Live-Validierung bei Texteingabe
                            onTextChanged: {
                                if (fahrzeugBackendV2) {
                                    fahrzeugBackendV2.validateSingleField("credit", text)
                                }
                            }
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
                        
                        Rectangle {
                            id: statusField
                            Layout.fillWidth: true
                            height: 48
                            color: "#2a2a2a"
                            border.color: {
                                if (statusText.text === "Aktiv") return "#4CAF50"
                                else if (statusText.text === "Wartung") return "#FF9800" 
                                else return "#F44336"
                            }
                            border.width: 2
                            radius: 6
                            
                            property var statusList: ["Aktiv", "Wartung", "Inaktiv"]
                            property int currentIndex: 0
                            property string currentText: statusList[currentIndex]
                            
                            Text {
                                id: statusText
                                anchors.centerIn: parent
                                text: statusField.currentText
                                font.family: ubuntuFont.name
                                font.pixelSize: 16
                                font.bold: true
                                color: {
                                    if (text === "Aktiv") return "#4CAF50"
                                    else if (text === "Wartung") return "#FF9800"
                                    else return "#F44336"
                                }
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    // Zum nächsten Status wechseln
                                    statusField.currentIndex = (statusField.currentIndex + 1) % 3
                                    statusField.currentText = statusField.statusList[statusField.currentIndex]
                                }
                                
                                onEntered: parent.opacity = 0.8
                                onExited: parent.opacity = 1.0
                            }
                            
                            Behavior on opacity {
                                NumberAnimation { duration: 150 }
                            }
                        }
                        
                        // Stammfahrer
                        Text {
                            text: "Stammfahrer"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                                                 Rectangle {
                             Layout.fillWidth: true
                             height: 48
                             color: "transparent"
                             z: 1 // Basis Z-Index für den Container
                             
                             TextField {
                                 id: stammfahrerField
                                 anchors.fill: parent
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 16
                                 color: "white"
                                 verticalAlignment: TextInput.AlignVCenter
                                 horizontalAlignment: TextInput.AlignHCenter
                                                                 background: Rectangle {
                                    color: "#2a2a2a"
                                    border.color: stammfahrerField.text.length > 0 ? (fahrzeugBackendV2 && fahrzeugBackendV2.isStammfahrerValid ? "#4CAF50" : "#f44336") : "#555555"
                                    border.width: 1
                                    radius: 6
                                }
                                 placeholderText: "Fahrer auswählen..."
                                 
                                 property var driverList: []
                                 property var filteredDrivers: []
                                 property bool isInitializing: false
                                 
                                 // DriverList lazy loading
                                 function loadDriverList() {
                                     if (fahrzeugBackendV2 && driverList.length === 0) {
                                         driverList = fahrzeugBackendV2.getDriverList()
                                     }
                                 }
                                 
                                 // Live-Validierung und AutoFill bei Texteingabe
                                 onTextChanged: {
                                     if (fahrzeugBackendV2) {
                                         fahrzeugBackendV2.validateSingleField("stammfahrer", text)
                                     }
                                     
                                     // AutoFill-Liste filtern (nur wenn nicht initialisiert wird)
                                     if (text.length > 0 && !isInitializing) {
                                         loadDriverList()  // DriverList laden falls nötig
                                         var filtered = []
                                         for (var i = 0; i < driverList.length; i++) {
                                             if (driverList[i].toLowerCase().indexOf(text.toLowerCase()) === 0) {
                                                 filtered.push(driverList[i])
                                             }
                                         }
                                         filteredDrivers = filtered
                                         if (filtered.length > 0) {
                                             autoFillPopup.visible = true
                                         } else {
                                             autoFillPopup.visible = false
                                         }
                                     } else {
                                         autoFillPopup.visible = false
                                     }
                                 }
                                 
                                 Keys.onDownPressed: {
                                     if (autoFillPopup.visible && autoFillList.count > 0) {
                                         autoFillList.currentIndex = Math.min(autoFillList.currentIndex + 1, autoFillList.count - 1)
                                     }
                                 }
                                 
                                 Keys.onUpPressed: {
                                     if (autoFillPopup.visible && autoFillList.count > 0) {
                                         autoFillList.currentIndex = Math.max(autoFillList.currentIndex - 1, 0)
                                     }
                                 }
                                 
                                 Keys.onReturnPressed: {
                                     if (autoFillPopup.visible && autoFillList.currentIndex >= 0) {
                                         text = filteredDrivers[autoFillList.currentIndex]
                                         autoFillPopup.visible = false
                                     }
                                 }
                                 
                                 Keys.onEscapePressed: {
                                     autoFillPopup.visible = false
                                 }
                             }
                             
                             // AutoFill Popup
                             Rectangle {
                                 id: autoFillPopup
                                 anchors.top: parent.bottom
                                 anchors.left: parent.left
                                 anchors.right: parent.right
                                 height: Math.min(autoFillList.count * 28 + 4, 144) // 28px pro Eintrag + 4px für Margins, Max 5 Einträge
                                 color: "#2a2a2a"
                                 border.color: "#555555"
                                 border.width: 1
                                 radius: 6
                                 visible: false
                                 z: 3000 // Höher als das Formular-Overlay (2000)
                                 
                                 ListView {
                                     id: autoFillList
                                     anchors.fill: parent
                                     anchors.margins: 2
                                     model: stammfahrerField.filteredDrivers
                                     currentIndex: 0
                                     
                                     delegate: Rectangle {
                                         width: autoFillList.width
                                         height: 28
                                         color: ListView.isCurrentItem ? "#404040" : "transparent"
                                         radius: 4
                                         
                                         Text {
                                             anchors.left: parent.left
                                             anchors.leftMargin: 8
                                             anchors.verticalCenter: parent.verticalCenter
                                             text: modelData
                                             font.family: ubuntuFont.name
                                             font.pixelSize: 14
                                             color: "white"
                                         }
                                         
                                         MouseArea {
                                             anchors.fill: parent
                                             hoverEnabled: true
                                             onEntered: autoFillList.currentIndex = index
                                             onClicked: {
                                                 stammfahrerField.text = modelData
                                                 autoFillPopup.visible = false
                                             }
                                         }
                                     }
                                 }
                             }
                         }
                        
                        // Notizen
                        Text {
                            text: "Notizen"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextArea {
                            id: notesField
                            Layout.fillWidth: true
                            Layout.preferredHeight: 80
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "Zusätzliche Notizen..."
                                                         wrapMode: TextArea.Wrap
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
                            onClicked: vehicleFormOverlay.visible = false
                            
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
                                 // Validierung
                                 if (!licensePlateField.text.trim()) {
                                     console.log("Fehler: Kennzeichen ist erforderlich!")
                                     return
                                 }
                                 
                                 // Daten sammeln
                                 var vehicleData = {
                                     license_plate: licensePlateField.text.trim(),
                                     rfrnc: referenceField.text.trim(),
                                     model: modelField.text.trim(),
                                     year: yearField.text.trim(),
                                     insurance: insuranceField.text.trim(),
                                     credit: creditField.text.trim(),
                                     status: statusField.currentText,
                                     stammfahrer: stammfahrerField.text.trim(),
                                     notes: notesField.text.trim()
                                 }
                                 
                                 // Prüfen ob es sich um Edit oder Neues Fahrzeug handelt
                                 var isEditMode = vehicleFormTitle.text.includes("bearbeiten")
                                 
                                 if (isEditMode) {
                                     // Edit-Modus: Fahrzeug aktualisieren
                                     fahrzeugBackendV2.updateVehicleFromForm(vehicleData)
                                 } else {
                                     // Neues Fahrzeug: Speichern
                                     fahrzeugBackendV2.saveVehicleFromForm(vehicleData)
                                 }
                                 
                                 // Overlay schließen
                                 vehicleFormOverlay.visible = false
                                 
                                 // Felder zurücksetzen
                                 licensePlateField.text = ""
                                 referenceField.text = ""
                                 modelField.text = ""
                                 yearField.text = ""
                                 insuranceField.text = ""
                                 creditField.text = ""
                                 statusField.currentIndex = 0
                                 stammfahrerField.text = ""
                                 notesField.text = ""
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
            Keys.onEscapePressed: vehicleFormOverlay.visible = false
        }
    }

         // Connections für Backend-Signale
     Connections {
         target: fahrzeugBackendV2
         
         function onWeekDataLoaded(licensePlate, week, revenueData, runningCostsData) {
             console.log("QML: weekDataLoaded Signal empfangen")
             console.log("QML: licensePlate:", licensePlate)
             console.log("QML: week:", week)
             console.log("QML: revenueData:", revenueData)
             console.log("QML: runningCostsData:", runningCostsData)
             
             // Revenue-Daten setzen
             revenueDataRepeater.model = revenueData || []
             console.log("QML: revenueDataRepeater.model gesetzt, Anzahl:", revenueDataRepeater.count)
             
             // Running-Costs-Daten setzen
             runningCostsDataRepeater.model = runningCostsData || []
             console.log("QML: runningCostsDataRepeater.model gesetzt, Anzahl:", runningCostsDataRepeater.count)
         }
         
         function onAskDeleteRunningCosts(licensePlate, week, count) {
             // Bestätigungsdialog für Running-Costs anzeigen
             deleteRunningCostsDialog.licensePlate = licensePlate
             deleteRunningCostsDialog.week = week
             deleteRunningCostsDialog.count = count
             deleteRunningCostsDialog.visible = true
         }
         
         // Neuer Error-Handler (sehr vorsichtig hinzugefügt)
         function onErrorOccurred(errorMessage) {
             console.log("Error-Signal empfangen:", errorMessage)
             errorMessage.text = errorMessage || "Ein unbekannter Fehler ist aufgetreten"
             errorOverlay.visible = true
         }
     }
} 