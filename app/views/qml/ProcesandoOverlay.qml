import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: root
    modal: true
    closePolicy: Popup.NoAutoClose
    anchors.centerIn: Overlay.overlay
    width: 380
    padding: 24

    property int actual: 0
    property int total: 0
    property string mensaje: ""
    property string titulo: "Analizando información..."

    background: Rectangle {
        color: Theme.background
        radius: 14
        border.color: "#e5e8f0"
        border.width: 1
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        BusyIndicator {
            running: root.visible
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: root.titulo
            font.pixelSize: 17
            font.bold: true
            color: Theme.primary
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: root.total > 0 ? ("Carpeta " + root.actual + " de " + root.total) : ""
            color: Theme.text
            Layout.alignment: Qt.AlignHCenter
        }

        ProgressBar {
            Layout.fillWidth: true
            from: 0
            to: Math.max(root.total, 1)
            value: root.actual
        }

        Text {
            text: root.mensaje
            color: Theme.text
            font.pixelSize: 12
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
        }
    }
}
