import QtQuick
import QtQuick.Controls

Button {
    id: root

    property color colorAcento: Theme.primary
    property string colorFondoPersonalizado: ""
    property string colorTextoPersonalizado: ""

    hoverEnabled: true
    padding: 14

    readonly property bool usarPersonalizados: root.colorFondoPersonalizado !== "" && root.colorTextoPersonalizado !== ""
    readonly property real opacidadBotón: !root.enabled ? 0.5 : 1.0
    readonly property color colorBorde: root.usarPersonalizados
        ? (root.enabled && (root.hovered || root.down) ? "#C2353F" : root.colorFondoPersonalizado)
        : (!root.enabled
            ? "#d7dbe8"
            : (root.hovered || root.down) ? root.colorAcento : "#c3c9de")
    readonly property color colorFondo: root.usarPersonalizados
        ? (root.enabled && (root.hovered || root.down) ? "#C2353F" : root.colorFondoPersonalizado)
        : (!root.enabled
            ? "#f1f2f7"
            : root.down
                ? "#e4e9fb"
                : root.hovered
                    ? "#eef1fb"
                    : "white")
    readonly property color colorTexto: root.usarPersonalizados
        ? root.colorTextoPersonalizado
        : (!root.enabled ? "#a3a8bd" : root.colorAcento)

    background: Rectangle {
        implicitHeight: 44
        radius: 10
        color: root.colorFondo
        opacity: root.opacidadBotón
        border.width: 1
        border.color: root.colorBorde
        scale: root.down && root.enabled ? 0.97 : 1.0

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on border.color { ColorAnimation { duration: 120 } }
        Behavior on opacity { NumberAnimation { duration: 120 } }
    }

    contentItem: Text {
        text: root.text
        color: root.colorTexto
        opacity: root.usarPersonalizados ? 1.0 : root.opacidadBotón
        font.pixelSize: 14
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    HoverHandler {
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ForbiddenCursor
    }
}
