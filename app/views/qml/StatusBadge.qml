import QtQuick

Rectangle {
    id: root
    property string texto: ""
    property color colorTexto: Theme.text
    property color colorFondo: "#eef1fb"

    radius: height / 2
    color: root.colorFondo
    implicitWidth: label.implicitWidth + 24
    implicitHeight: 26

    Text {
        id: label
        anchors.centerIn: parent
        text: root.texto
        color: root.colorTexto
        font.pixelSize: 12
        font.bold: true
    }
}
