import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

Rectangle {
    id: root
    property var goHome: function() {
        // Fallback: Blende die Abrechnungsseite aus und zeige das MainMenu
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

    property bool werteGeladen: false
    property var summary: {"umsatz": "-", "trinkgeld": "-", "bargeld": "-"}
    property var card40100: {"label": "Taxi", "value": "-"}
    property var cardUber: {"label": "Uber", "value": "-", "zeile1": "-", "zeile2": "-", "zeile3": "-"}
    property var cardBolt: {"label": "Bolt", "value": "-"}
    property string tank: ""
    property string einsteiger: ""
    property bool wizardGestartet: false
    property var wizardSelection: ({})

    // Seite bleibt leer, solange das Wizard offen ist
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        spacing: 8
        visible: werteGeladen

        // Titel dynamisch setzen
        Component.onCompleted: {
            if (typeof mainWindow !== 'undefined') {
                mainWindow.title = (wizardSelection.fahrzeug ? wizardSelection.fahrzeug.split(" ")[0] : "-") + " - " + (wizardSelection.fahrer || "-");
            }
        }
        Connections {
            target: abrechnungsBackend
            function onErgebnisseChanged() {
                if (typeof mainWindow !== 'undefined') {
                    mainWindow.title = (wizardSelection.fahrzeug ? wizardSelection.fahrzeug.split(" ")[0] : "-") + " - " + (wizardSelection.fahrer || "-");
                }
            }
        }
        Rectangle {
            color: "transparent"
            border.color: "white"
            border.width: 1
            radius: 4
            Layout.leftMargin: 950 // noch weiter nach rechts (Summenzeile)
            Layout.topMargin: 0 // kein Abstand zum Namen
            // Summenzeile entfernt, da sie jetzt weiter unten im Layout steht
        }

        // Cards für Plattformen und Input-Card nebeneinander
        RowLayout {
            spacing: Style.spacingLarge * 1.6
            anchors.centerIn: parent
            anchors.horizontalCenterOffset: -84
            Layout.topMargin: 150
            // Cards für Plattformen
            ColumnLayout {
                spacing: 32 // vorher 20
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 288 // vorher 180
                visible: card40100.zeile1 !== "-" && parseFloat(card40100.zeile1) > 0
                Text { text: card40100.label; font.pixelSize: Style.fontSizeTitle * 1.6; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: 288
                    Layout.preferredHeight: 288
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge * 1.6
                        spacing: Style.spacingLarge * 1.6
                        Text { text: card40100.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: card40100.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: card40100.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                    }
                }
            }
            ColumnLayout {
                spacing: 32
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 288
                visible: cardUber.zeile1 !== "-" && parseFloat(cardUber.zeile1) > 0
                Text { text: cardUber.label === "Uber" ? "UBER" : cardUber.label; font.pixelSize: Style.fontSizeTitle * 1.6; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: 288
                    Layout.preferredHeight: 288
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge * 1.6
                        spacing: Style.spacingLarge * 1.6
                        Text { text: cardUber.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardUber.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardUber.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                    }
                }
            }
            ColumnLayout {
                spacing: 32
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 288
                visible: cardBolt.zeile1 !== "-" && parseFloat(cardBolt.zeile1) > 0
                Text { text: cardBolt.label === "Bolt" ? "BOLT" : cardBolt.label; font.pixelSize: Style.fontSizeTitle * 1.6; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: 288
                    Layout.preferredHeight: 288
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge * 1.6
                        spacing: Style.spacingLarge * 1.6
                        Text { text: cardBolt.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardBolt.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardBolt.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                    }
                }
            }
            Item { width: 64 } // Platzhalter größer
            // Input-Card und Ergebnis-Element untereinander
            ColumnLayout {
                spacing: 16
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 288
                Layout.topMargin: 70
                // Input-Card
                Rectangle {
                    Layout.preferredWidth: 288
                    Layout.preferredHeight: 288
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge * 1.6
                        spacing: 14
                        RowLayout {
                            spacing: 12
                            Layout.alignment: Qt.AlignHCenter
                            TextField {
                                id: inputField1
                                width: 150
                                Layout.preferredWidth: 150
                                Layout.alignment: Qt.AlignVCenter
                                placeholderText: ""
                                font.pixelSize: 28
                                font.family: ubuntuFont.name
                                color: Style.text
                                background: Rectangle { color: "#222"; radius: 8 }
                                padding: 10
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                text: abrechnungsBackend.inputGas
                                onTextChanged: abrechnungsBackend.inputGas = text
                            }
                                Text {
                                text: "€"
                                font.pixelSize: 24
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                verticalAlignment: Text.AlignVCenter
                            }
                            Image {
                                source: "assets/icons/gas_gray.svg"
                                width: 20; height: 20
                                fillMode: Image.PreserveAspectFit
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }
                        RowLayout {
                            spacing: 12
                            Layout.alignment: Qt.AlignHCenter
                            TextField {
                                id: inputField2
                                width: 150
                                Layout.preferredWidth: 150
                                Layout.alignment: Qt.AlignVCenter
                                placeholderText: ""
                                font.pixelSize: 28
                                font.family: ubuntuFont.name
                                    color: Style.text
                                background: Rectangle { color: "#222"; radius: 8 }
                                padding: 10
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                text: abrechnungsBackend.inputEinsteiger
                                onTextChanged: abrechnungsBackend.inputEinsteiger = text
                            }
                            Text {
                                text: "€"
                                font.pixelSize: 24
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                    verticalAlignment: Text.AlignVCenter
                                }
                            Image {
                                source: "assets/icons/hail_gray.svg"
                                width: 20; height: 20
                                fillMode: Image.PreserveAspectFit
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }
                        RowLayout {
                            spacing: 10
                            Layout.alignment: Qt.AlignHCenter
                            TextField {
                                id: inputField3
                                width: 150
                                Layout.preferredWidth: 150
                                Layout.alignment: Qt.AlignVCenter
                                placeholderText: ""
                                font.pixelSize: 28
                                font.family: ubuntuFont.name
                            color: Style.text
                                background: Rectangle { color: "#222"; radius: 8 }
                                padding: 10
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                                text: abrechnungsBackend.inputExpense
                                onTextChanged: {
                                    if (abrechnungsBackend.inputExpense !== text)
                                        abrechnungsBackend.inputExpense = text
                                }
                            }
                            Text {
                                text: "€"
                                font.pixelSize: 24
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                verticalAlignment: Text.AlignVCenter
                            }
                        Item {
                                width: 49
                                height: 49
                                MouseArea {
                                    id: addHoverArea
                                anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: abrechnungsBackend.show_wizard_add_cost()
                                }
                                Image {
                                    anchors.centerIn: parent
                                    source: addHoverArea.containsMouse ? "assets/icons/add_orange.svg" : "assets/icons/add_white.svg"
                                    width: 49
                                    height: 49
                                    fillMode: Image.PreserveAspectFit
                                    z: 1
                                }
                            }
                        }
                    }
                }
                // Ergebnis-Element direkt unter der Input Card
                Item {
                    id: ergebnisElement
                    width: 288
                    height: 90
                    Layout.alignment: Qt.AlignTop
                    visible: werteGeladen
                    z: 10
                    Text {
                        anchors.fill: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        text: abrechnungsBackend.ergebnis.toFixed(2) + ' €'
                        font.pixelSize: 64
                        font.bold: true
                        color: Style.primary
                        visible: werteGeladen
                        font.family: ubuntuFont.name
                    }
                }
            }
        }
    }

    // Nach den Cards für Plattformen:
    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: -100
        anchors.top: parent.top
        anchors.topMargin: 250
        spacing: 64
        // Summenzeile (links)
        RowLayout {
            id: summenZeile
            spacing: 170
            // Umsatz
            RowLayout {
                spacing: 4
                Image {
                    source: "assets/icons/sales_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { 
                    text: abrechnungsBackend.headcard_umsatz.toFixed(2); 
                    font.pixelSize: Style.fontSizeHeader; 
                    font.bold: true; 
                    color: Style.text; 
                    font.family: ubuntuFont.name 
                }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
            // Trinkgeld nur anzeigen, wenn > 0
            RowLayout {
                spacing: 4
                visible: abrechnungsBackend.headcard_trinkgeld > 0
                Image {
                    source: "assets/icons/tips_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { text: abrechnungsBackend.headcard_trinkgeld.toFixed(2); font.pixelSize: Style.fontSizeHeader; font.bold: true; color: Style.text; font.family: ubuntuFont.name }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
            // Deal
            RowLayout {
                spacing: 4
                Image {
                    source: abrechnungsBackend.headcard_deal_icon || "assets/icons/cash_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { 
                    text: abrechnungsBackend.headcard_deal_value.toFixed(2); 
                    font.pixelSize: Style.fontSizeHeader; 
                    font.bold: true; 
                    color: Style.text; 
                    font.family: ubuntuFont.name 
                }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
            // Garage nur anzeigen, wenn > 0
            RowLayout {
                spacing: 4
                visible: abrechnungsBackend.headcard_garage > 0
                Image {
                    source: "assets/icons/parking_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { 
                    text: abrechnungsBackend.headcard_garage.toFixed(2); 
                    font.pixelSize: Style.fontSizeHeader; 
                    font.bold: true; 
                    color: Style.text; 
                    font.family: ubuntuFont.name 
                }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
        }
        // Ergebnis (rechts)
        // Item {
        //     id: ergebnisElement
        //     width: 240
        //     height: 90
        //     Layout.alignment: Qt.AlignHCenter
        //     visible: werteGeladen
        //     z: 10
        //     Text {
        //         anchors.fill: parent
        //         horizontalAlignment: Text.AlignHCenter
        //         verticalAlignment: Text.AlignVCenter
        //         text: abrechnungsBackend.ergebnis.toFixed(2) + ' €'
        //         font.pixelSize: 64
        //         font.bold: true
        //         color: Style.primary
        //         visible: werteGeladen
        //         font.family: ubuntuFont.name
        //     }
        // }
    }

    function parseUberCard(results, deal) {
        for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && results[i].label === "Uber" && results[i].details) {
                var details = results[i].details;
                var gross_total = 0;
                var cash_collected = 0;
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Echter Umsatz" || details[j].label === "Total")
                        gross_total = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Restbetrag" || details[j].label === "Rest" || details[j].label === "Bargeld")
                        cash_collected = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                }
                if (deal === "P") {
                    var bankomat = gross_total - cash_collected;
                    return {
                        label: "Uber",
                        zeile1: gross_total.toFixed(2),
                        zeile2: cash_collected.toFixed(2),
                        zeile3: bankomat.toFixed(2)
                    };
                } else {
                    var zeile1 = gross_total;
                    var zeile2 = gross_total / 2;
                    var zeile3 = cash_collected;
                    return {
                        label: "Uber",
                        zeile1: zeile1.toFixed(2),
                        zeile2: zeile2.toFixed(2),
                        zeile3: zeile3.toFixed(2)
                    };
                }
            }
        }
        return {label: "Uber", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    function parseBoltCard(results, deal) {
        for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && results[i].label === "Bolt" && results[i].details) {
                var details = results[i].details;
                var echter_umsatz = 0;
                var cash_collected = 0;
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Echter Umsatz")
                        echter_umsatz = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Bargeld")
                        cash_collected = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                }
                if (deal === "P") {
                    var bankomat = echter_umsatz - cash_collected;
                    return {
                        label: "Bolt",
                        zeile1: echter_umsatz.toFixed(2),
                        zeile2: cash_collected.toFixed(2),
                        zeile3: bankomat.toFixed(2)
                    };
                } else {
                    var net_earnings = 0;
                    for (var j = 0; j < details.length; j++) {
                        if (details[j].label === "Echter Umsatz") net_earnings = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    }
                    var zeile1 = net_earnings;
                    var zeile2 = zeile1 / 2;
                    var zeile3 = cash_collected;
                    return {
                        label: "Bolt",
                        zeile1: zeile1.toFixed(2),
                        zeile2: zeile2.toFixed(2),
                        zeile3: zeile3.toFixed(2)
                    };
                }
            }
        }
        return {label: "Bolt", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    function parse40100Card(results, deal) {
        for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && results[i].label === "40100" && results[i].details) {
                var details = results[i].details;
                var real = 0;
                var bargeld = 0;
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Real") real = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Bargeld") bargeld = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                }
                if (deal === "P") {
                    var bankomat = real - bargeld;
                    return {
                        label: "Taxi",
                        zeile1: real.toFixed(2),
                        zeile2: bargeld.toFixed(2),
                        zeile3: bankomat.toFixed(2)
                    };
                } else {
                    var anteil = real / 2;
                    var rest = anteil - bargeld;
                    return {
                        label: "Taxi",
                        zeile1: real.toFixed(2),
                        zeile2: anteil.toFixed(2),
                        zeile3: rest.toFixed(2)
                    };
                }
            }
        }
        return {label: "Taxi", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    Connections {
        target: abrechnungsBackend
        function onErgebnisseChanged() {
            var results = abrechnungsBackend.get_ergebnisse();
            var deal = abrechnungsBackend.deal;
            card40100 = parse40100Card(results, deal);
            cardUber = parseUberCard(results, deal);
            cardBolt = parseBoltCard(results, deal);
            werteGeladen = true;
            wizardSelection = abrechnungsBackend.get_current_selection();
        }
    }

    Component.onCompleted: {
        var results = abrechnungsBackend.get_ergebnisse();
        var deal = abrechnungsBackend.deal;
        if (results && results.length > 0) {
            card40100 = parse40100Card(results, deal);
            cardUber = parseUberCard(results, deal);
            cardBolt = parseBoltCard(results, deal);
            werteGeladen = true;
        }
        wizardSelection = abrechnungsBackend.get_current_selection();
    }

    // Neue BottomBar:
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
        // Check-Button
        MouseArea {
            id: checkArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: abrechnungsBackend.speichereUmsatz()
            Image {
                anchors.centerIn: parent
                source: checkArea.containsMouse ? "assets/icons/check_orange.svg" : "assets/icons/check_white.svg"
                width: checkArea.pressed ? 32 : checkArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        // Redo-Button
        MouseArea {
            id: redoArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: abrechnungsBackend.show_wizard_and_load_page()
            Image {
                anchors.centerIn: parent
                source: redoArea.pressed ? "assets/icons/redo_gray.svg"
                    : redoArea.containsMouse ? "assets/icons/redo_orange.svg" : "assets/icons/redo_white.svg"
                width: redoArea.pressed ? 32 : redoArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
        }
    }
    }
}
