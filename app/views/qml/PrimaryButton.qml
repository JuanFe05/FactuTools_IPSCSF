import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: root

    property color colorAcento: Theme.primary
    property string iconoTexto: ""
    property bool cargando: false
    property string textoCargando: "Procesando..."

    hoverEnabled: true
    padding: 14

    readonly property color colorActual: !root.enabled
        ? "#a9b2d6"
        : root.down
            ? Qt.darker(root.colorAcento, 1.18)
            : root.hovered
                ? Qt.lighter(root.colorAcento, 1.1)
                : root.colorAcento

    background: Rectangle {
        implicitHeight: 44
        radius: 10
        color: root.colorActual
        scale: root.down ? 0.97 : 1.0

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on scale { NumberAnimation { duration: 90 } }
    }

    contentItem: Item {
        implicitWidth: fila.implicitWidth
        implicitHeight: fila.implicitHeight

        RowLayout {
            id: fila
            anchors.centerIn: parent
            spacing: 8

            BusyIndicator {
                visible: root.cargando
                running: root.cargando
                implicitWidth: 18
                implicitHeight: 18
            }

            Text {
                visible: root.iconoTexto !== "" && !root.cargando
                text: root.iconoTexto
                color: "white"
                font.pixelSize: 16
                font.bold: true
            }

            Text {
                text: root.cargando ? root.textoCargando : root.text
                color: "white"
                font.pixelSize: 14
                font.bold: true
            }
        }
    }

    // Basic style no aplica cursor de mano por defecto; se fuerza explícitamente.
    HoverHandler {
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ForbiddenCursor
    }
}
