pragma Singleton
import QtQuick 2.15

QtObject {
    // Farben
    readonly property color background: "#000000"
    readonly property color surface: "#1a1a1a"
    readonly property color primary: "#f79009"
    readonly property color primaryHover: "#ffa733"
    readonly property color text: "#ffffff"
    readonly property color textMuted: "#aaaaaa"
    readonly property color border: "#2a2a2a"
    readonly property color accent: "#00c2ff"
    readonly property color success: "#22c55e"
    readonly property color error: "#ef4444"
    readonly property color warning: "#f59e0b"

    // Button-Farben
    readonly property color buttonTransparent: "transparent"
    readonly property color buttonHover: "#1AF79009"    // 10% Alpha
    readonly property color buttonPressed: "#33F79009"  // 20% Alpha
    readonly property color buttonBorder: "#444444"
    readonly property color buttonBorderHover: "#f79009"

    // Schriftgrößen
    readonly property int fontSizeSmall: 12
    readonly property int fontSizeNormal: 14
    readonly property int fontSizeLarge: 18
    readonly property int fontSizeTitle: 20
    readonly property int fontSizeHeader: 24
    readonly property int fontSizeHuge: 48

    // Abstände
    readonly property int spacingSmall: 5
    readonly property int spacingNormal: 10
    readonly property int spacingLarge: 15
    readonly property int spacingHuge: 30
    readonly property int spacingExtra: 30

    // Radien
    readonly property int radiusSmall: 4
    readonly property int radiusNormal: 8
    readonly property int radiusLarge: 12
    readonly property int radiusHuge: 16

    // Button-Höhen
    readonly property int buttonHeightSmall: 32
    readonly property int buttonHeightNormal: 40
    readonly property int buttonHeightLarge: 60
    readonly property int buttonHeightHuge: 80

    // Animationen
    readonly property int animationFast: 200
    readonly property int animationNormal: 300
    readonly property int animationSlow: 400

    // Sidebar
    readonly property int sidebarWidth: 80
    readonly property int sidebarHeight: 300

    // Funktionen für Hover-Effekte
    function getHoverColor(baseColor) {
        // Für transparente Buttons
        if (baseColor === buttonTransparent) {
            return buttonHover
        }
        // Für andere Farben
        return Qt.lighter(baseColor, 1.1)
    }
    
    function getPressedColor(baseColor) {
        // Für transparente Buttons
        if (baseColor === buttonTransparent) {
            return buttonPressed
        }
        // Für andere Farben
        return Qt.darker(baseColor, 1.1)
    }
    
    // Standard-Button-Styling (transparent)
    function getButtonStyle(baseColor = buttonTransparent) {
        return `
            background: Rectangle {
                color: parent.pressed ? Style.getPressedColor('${baseColor}') : 
                       parent.hovered ? Style.getHoverColor('${baseColor}') : '${baseColor}'
                radius: ${radiusNormal}
                border.color: parent.hovered ? '${buttonBorderHover}' : '${buttonBorder}'
                border.width: 1
            }
        `
    }
    
    // Standard-Text-Styling
    function getTextStyle(color = text, size = fontSizeNormal, bold = false) {
        return `
            color: '${color}'
            font.pixelSize: ${size}
            font.bold: ${bold}
        `
    }
    
    // Transparenter Button-Style
    function getTransparentButtonStyle() {
        return getButtonStyle(buttonTransparent)
    }
} 