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
    property var card40100: {"label": "40100", "value": "-"}
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

        // Headercard mit Gesamtsummen
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: "black"
            radius: Style.radiusLarge
            border.width: 0
            anchors.bottomMargin: 4
            RowLayout {
                anchors.fill: parent
                anchors.margins: Style.spacingLarge
                spacing: Style.spacingLarge
                Text {
                    text: (wizardSelection.fahrzeug ? wizardSelection.fahrzeug.split(" ")[0] : "-") + " / " + (wizardSelection.fahrer || "-")
                    font.pixelSize: 38
                    font.bold: true
                    color: "#b0b0b0"
                    font.family: ubuntuFont.name
                }
                Item { Layout.fillWidth: true }
            }
        }

        // Summenzeile als eigene Zeile direkt unter der Headcard
        RowLayout {
            id: summenZeile
            spacing: 40
            anchors.top: parent.children[0].bottom
            anchors.topMargin: 0
            anchors.horizontalCenter: parent.horizontalCenter
            z: 10
            Item { width: 15 }
            RowLayout {
                spacing: 4
                Image {
                    source: "assets/icons/receipt_gray.svg"
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
            RowLayout {
                spacing: 4
                Image {
                    source: "assets/icons/tips_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { text: abrechnungsBackend.headcard_trinkgeld.toFixed(2); font.pixelSize: Style.fontSizeHeader; font.bold: true; color: Style.text; font.family: ubuntuFont.name }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
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
            Item { Layout.fillWidth: true }
        }

        // Cards für Plattformen
        RowLayout {
            spacing: Style.spacingLarge
            anchors.centerIn: parent
            anchors.horizontalCenterOffset: -104
            ColumnLayout {
                spacing: 20
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 180
                Text { text: card40100.label; font.pixelSize: Style.fontSizeTitle; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
            Rectangle {
                    Layout.preferredWidth: 180
                    Layout.preferredHeight: 180
                    color: "black"
                radius: Style.radiusLarge
                    border.width: 0
                ColumnLayout {
                    anchors.fill: parent
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge
                        spacing: Style.spacingLarge
                        Text { text: card40100.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: card40100.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: card40100.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                }
            }
            }
            ColumnLayout {
                spacing: 20
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 180
                Text { text: cardUber.label === "Uber" ? "UBER" : cardUber.label; font.pixelSize: Style.fontSizeTitle; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: 180
                    Layout.preferredHeight: 180
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge
                        spacing: Style.spacingLarge
                        Text { text: cardUber.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardUber.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardUber.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                    }
                }
            }
            ColumnLayout {
                spacing: 20
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 180
                Text { text: cardBolt.label === "Bolt" ? "BOLT" : cardBolt.label; font.pixelSize: Style.fontSizeTitle; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: 180
                    Layout.preferredHeight: 180
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge
                        spacing: Style.spacingLarge
                        Text { text: cardBolt.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardBolt.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardBolt.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                    }
                }
            }
            // Platzhalter-Item zwischen Bolt und Input-Card
            Item { width: 40 }
            // Input-Card mit Feldern
            Item {
                // Wrapper für vertikale Zentrierung
                height: 220 // oder passend zur Card
                RowLayout {
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 8
                    // Input-Card mit Feldern
                    ColumnLayout {
                        spacing: 20
                        Layout.alignment: Qt.AlignTop
                        Layout.preferredWidth: 180
                        Text {
                            text: "INPUT"
                            font.pixelSize: Style.fontSizeTitle
                            font.bold: true
                            color: "#b0b0b0"
                            horizontalAlignment: Text.AlignHCenter
                            Layout.alignment: Qt.AlignHCenter
                            font.family: ubuntuFont.name
                        }
                                    Rectangle {
                            Layout.preferredWidth: 180
                            Layout.preferredHeight: 180
                            color: "black"
                            radius: Style.radiusLarge
                            border.width: 0
                            ColumnLayout {
                                        anchors.fill: parent
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.margins: Style.spacingLarge
                                spacing: 9
                                // Zusätzlicher Abstand unten, damit nichts abgeschnitten wird
                                Item { Layout.fillHeight: true }
                                // Erstes Eingabefeld + Icon
                                RowLayout {
                                    spacing: 12
                                    Layout.alignment: Qt.AlignHCenter
                                    TextField {
                                        id: inputField1
                                        width: 120
                                        Layout.preferredWidth: 120
                                        Layout.alignment: Qt.AlignVCenter
                                        placeholderText: ""
                                        font.pixelSize: 24
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
                                // Zweites Eingabefeld + Icon
                                RowLayout {
                                    spacing: 12
                                    Layout.alignment: Qt.AlignHCenter
                                    TextField {
                                        id: inputField2
                                        width: 120
                                        Layout.preferredWidth: 120
                                        Layout.alignment: Qt.AlignVCenter
                                        placeholderText: ""
                                        font.pixelSize: 24
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
                                // Drittes Eingabefeld + Icon
                                RowLayout {
                                    spacing: 10
                                    Layout.alignment: Qt.AlignHCenter
                                    TextField {
                                        id: inputField3
                                        width: 120
                                        Layout.preferredWidth: 120
                                        Layout.alignment: Qt.AlignVCenter
                                        placeholderText: ""
                                        font.pixelSize: 24
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
                    }
                }
            }
        }
    }

    // Ergebnis zentriert am unteren Rand
    Item {
        id: ergebnisElement
        width: 200; height: 80
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 110
        visible: werteGeladen
        Text {
            anchors.fill: parent
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: abrechnungsBackend.ergebnis.toFixed(2) + ' €'
            font.pixelSize: 54
            font.bold: true
            color: Style.primary
            visible: werteGeladen
            font.family: ubuntuFont.name
        }
    }

    function parseUberCard(results) {
        // Suche Uber-Summary
            for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && results[i].label === "Uber" && results[i].details) {
                var details = results[i].details;
                var gross_total = 0;
                var cash_collected = 0;
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Echter Umsatz" || details[j].label === "Total") gross_total = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Restbetrag" || details[j].label === "Rest" || details[j].label === "Bargeld") cash_collected = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                }
                var zeile1 = gross_total;
                var zeile2 = gross_total / 2;
                var zeile3 = cash_collected;
                console.log("UberCard Debug:", "gross_total:", gross_total, "cash_collected:", cash_collected, "zeile1:", zeile1, "zeile2:", zeile2, "zeile3:", zeile3);
                return {
                    label: "Uber",
                    zeile1: zeile1.toFixed(2),
                    zeile2: zeile2.toFixed(2),
                    zeile3: zeile3.toFixed(2)
                };
            }
        }
        return {label: "Uber", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    function parseBoltCard(results) {
            for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && results[i].label === "Bolt" && results[i].details) {
                var details = results[i].details;
                var net_earnings = 0;
                var rider_tips = 0;
                var cash_collected = 0;
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Echter Umsatz") net_earnings = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Anteil") rider_tips = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Rest" || details[j].label === "Bargeld") cash_collected = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
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
        return {label: "Bolt", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    function parse40100Card(results) {
            for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && results[i].label === "40100" && results[i].details) {
                var details = results[i].details;
                var real = 0;
                var anteil = 0;
                var rest = 0;
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Real") real = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Anteil") anteil = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Rest") rest = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                }
                return {
                    label: "40100",
                    zeile1: real.toFixed(2),
                    zeile2: anteil.toFixed(2),
                    zeile3: rest.toFixed(2)
                };
            }
        }
        return {label: "40100", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    Connections {
        target: abrechnungsBackend
        function onErgebnisseChanged() {
            var results = abrechnungsBackend.get_ergebnisse();
            card40100 = parse40100Card(results);
            cardUber = parseUberCard(results);
            cardBolt = parseBoltCard(results);
            werteGeladen = true;
            wizardSelection = abrechnungsBackend.get_current_selection();
        }
    }

    Component.onCompleted: {
        var results = abrechnungsBackend.get_ergebnisse();
        if (results && results.length > 0) {
            card40100 = parse40100Card(results);
            cardUber = parseUberCard(results);
            cardBolt = parseBoltCard(results);
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
