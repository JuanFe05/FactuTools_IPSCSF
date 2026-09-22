import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    property var filas: []

    radius: 12
    color: "white"
    border.color: "#e5e8f0"
    border.width: 1
    clip: true

    // Pesos relativos de cada columna; cabecera y filas los comparten para quedar alineadas.
    readonly property var columnas: [
        { titulo: "No. Factura", peso: 1.4 },
        { titulo: "FURIPS 1", peso: 1.6 },
        { titulo: "FURIPS 2", peso: 1.6 },
        { titulo: "Separación", peso: 1.0 }
    ]
    readonly property real pesoTotal: {
        var suma = 0
        for (var i = 0; i < columnas.length; i++) suma += columnas[i].peso
        return suma
    }
    readonly property int espaciado: 10
    readonly property real anchoDisponible: width - 32 - espaciado * (columnas.length - 1)

    function anchoColumna(indice) {
        return Math.max(60, anchoDisponible * (columnas[indice].peso / pesoTotal))
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            color: Theme.primary

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: root.espaciado

                Repeater {
                    model: root.columnas
                    delegate: Text {
                        Layout.preferredWidth: root.anchoColumna(index)
                        text: modelData.titulo
                        color: Theme.background
                        font.bold: true
                        font.pixelSize: 12
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }
                }
            }
        }

        Item {
            visible: root.filas.length === 0
            Layout.fillWidth: true
            Layout.fillHeight: true

            Text {
                anchors.centerIn: parent
                text: "Aún no hay procesos ejecutados."
                color: Theme.text
                font.pixelSize: 13
            }
        }

        ListView {
            visible: root.filas.length > 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root.filas
            ScrollBar.vertical: ScrollBar {}

            delegate: Rectangle {
                width: ListView.view.width
                height: 46
                color: index % 2 === 0 ? "white" : "#fafbfe"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16
                    spacing: root.espaciado

                    Text {
                        Layout.preferredWidth: root.anchoColumna(0)
                        text: modelData.numeroFactura || "-"
                        font.pixelSize: 12
                        color: Theme.text
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.preferredWidth: root.anchoColumna(1)
                        text: modelData.furips1 || "—"
                        font.pixelSize: 12
                        color: modelData.furips1 && modelData.furips1 !== "—" ? Theme.text : Theme.danger
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }

                    Text {
                        Layout.preferredWidth: root.anchoColumna(2)
                        text: modelData.furips2 || "—"
                        font.pixelSize: 12
                        color: modelData.furips2 && modelData.furips2 !== "—" ? Theme.text : Theme.danger
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }

                    Item {
                        Layout.preferredWidth: root.anchoColumna(3)
                        Layout.fillHeight: true

                        StatusBadge {
                            anchors.centerIn: parent
                            texto: modelData.separado ? "Completado" : (modelData.error ? "No" : "Pendiente")
                            colorTexto: modelData.separado ? "#0AA06E" : (modelData.error ? "#e63946" : Theme.text)
                            colorFondo: modelData.separado ? "#e4f7ef" : (modelData.error ? "#fdecee" : "#f1f1f1")
                        }
                        HoverHandler { id: hoverError }
                        ToolTip.visible: hoverError.hovered && modelData.error !== ""
                        ToolTip.text: modelData.error || ""
                    }
                }
            }
        }
    }
}
