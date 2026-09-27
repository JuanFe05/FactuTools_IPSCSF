import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    property string valor: "0"
    property string etiqueta: ""
    property color colorAcento: Theme.primary

    radius: 12
    color: "white"
    border.color: "#e5e8f0"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 6

        Text {
            text: root.valor
            font.pixelSize: 34
            font.bold: true
            color: root.colorAcento
        }

        Text {
            text: root.etiqueta
            font.pixelSize: 13
            color: Theme.text
        }
    }
}
