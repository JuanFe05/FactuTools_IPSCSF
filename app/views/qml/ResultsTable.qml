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
        { titulo: "Carpeta", peso: 1.8 },
        { titulo: "No. Factura", peso: 1.1 },
        { titulo: "Correcto", peso: 0.9 },
        { titulo: "Observaciones", peso: 2.5 },
        { titulo: "Empresa", peso: 2.0 },
        { titulo: "F. Facturación", peso: 1.1 },
        { titulo: "Estado", peso: 1.0 },
        { titulo: "Usuario", peso: 1.3 },
        { titulo: "Total", peso: 1.0 },
        { titulo: "Renombrado", peso: 1.2 }
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

    function colorEstado(estado) {
        if (estado === "Completado") return "#0AA06E"
        if (estado === "Error") return "#e63946"
        if (estado === "Procesando") return "#1938bc"
        return Theme.text
    }

    function fondoEstado(estado) {
        if (estado === "Completado") return "#e4f7ef"
        if (estado === "Error") return "#fdecee"
        if (estado === "Procesando") return "#eef1fb"
        return "#f1f1f1"
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

                    Item {
                        Layout.preferredWidth: root.anchoColumna(0)
                        Layout.fillHeight: true

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width
                            text: modelData.nombreCarpeta || "-"
                            font.pixelSize: 12
                            color: Theme.text
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                        }
                        HoverHandler { id: hoverCarpeta }
                        ToolTip.visible: hoverCarpeta.hovered
                        ToolTip.text: modelData.nombreCarpeta || ""
                    }

                    Text {
                        Layout.preferredWidth: root.anchoColumna(1)
                        text: modelData.numeroFactura || "-"
                        font.pixelSize: 12
                        color: modelData.registroEncontrado ? Theme.text : Theme.danger
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }

                    Item {
                        Layout.preferredWidth: root.anchoColumna(2)
                        Layout.fillHeight: true

                        StatusBadge {
                            anchors.centerIn: parent
                            texto: modelData.archivosCorrectos === true
                                   ? "Sí"
                                   : (modelData.archivosCorrectos === false ? "No" : "Pendiente")
                            colorTexto: modelData.archivosCorrectos === true
                                        ? "#0AA06E"
                                        : (modelData.archivosCorrectos === false ? "#e63946" : Theme.text)
                            colorFondo: modelData.archivosCorrectos === true
                                        ? "#e4f7ef"
                                        : (modelData.archivosCorrectos === false ? "#fdecee" : "#f1f1f1")
                        }
                    }

                    Item {
                        Layout.preferredWidth: root.anchoColumna(3)
                        Layout.fillHeight: true

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width
                            text: (modelData.detallesValidacion && modelData.detallesValidacion.length > 0)
                                  ? modelData.detallesValidacion[0]
                                  : "—"
                            font.pixelSize: 11
                            color: modelData.archivosCorrectos === false ? Theme.danger : Theme.text
                            wrapMode: Text.WordWrap
                            elide: Text.ElideRight
                        }
                        HoverHandler { id: hoverObservaciones }
                        ToolTip.visible: hoverObservaciones.hovered
                        ToolTip.text: (modelData.detallesValidacion && modelData.detallesValidacion.length > 0)
                                      ? modelData.detallesValidacion.join("\n")
                                      : ""
                    }

                    Item {
                        Layout.preferredWidth: root.anchoColumna(4)
                        Layout.fillHeight: true

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width
                            text: modelData.empresa || "-"
                            font.pixelSize: 12
                            color: Theme.text
                            horizontalAlignment: Text.AlignHCenter
                            elide: Text.ElideRight
                        }
                        HoverHandler { id: hoverEmpresa }
                        ToolTip.visible: hoverEmpresa.hovered
                        ToolTip.text: modelData.empresa || ""
                    }

                    Text {
                        Layout.preferredWidth: root.anchoColumna(5)
                        text: modelData.fechaFacturacion || "-"
                        font.pixelSize: 12
                        color: Theme.text
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }
                    Text {
                        Layout.preferredWidth: root.anchoColumna(6)
                        text: modelData.estado || "-"
                        font.pixelSize: 12
                        color: Theme.text
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }

                    Item {
                        Layout.preferredWidth: root.anchoColumna(7)
                        Layout.fillHeight: true

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width
                            text: modelData.usuarioFactura || "-"
                            font.pixelSize: 12
                            color: Theme.text
                            elide: Text.ElideRight
                            horizontalAlignment: Text.AlignHCenter
                        }
                        HoverHandler { id: hoverUsuario }
                        ToolTip.visible: hoverUsuario.hovered
                        ToolTip.text: modelData.usuarioFactura || ""
                    }

                    Text {
                        Layout.preferredWidth: root.anchoColumna(8)
                        text: modelData.total ? modelData.total.toLocaleString(Qt.locale(), "f", 0) : "-"
                        font.pixelSize: 12
                        color: Theme.text
                        horizontalAlignment: Text.AlignHCenter
                        elide: Text.ElideRight
                    }

                    Item {
                        Layout.preferredWidth: root.anchoColumna(9)
                        Layout.fillHeight: true

                        StatusBadge {
                            anchors.centerIn: parent
                            texto: modelData.estadoRenombramiento || "Pendiente"
                            colorTexto: root.colorEstado(modelData.estadoRenombramiento)
                            colorFondo: root.fondoEstado(modelData.estadoRenombramiento)
                        }
                    }
                }
            }
        }
    }
}
