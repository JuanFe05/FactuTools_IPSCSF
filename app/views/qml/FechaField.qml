import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    implicitWidth: 180
    implicitHeight: 42
    radius: 8
    color: "white"
    border.width: input.activeFocus ? 2 : 1
    border.color: input.activeFocus ? Theme.primary : "#d7dbe8"

    readonly property date fechaHoy: new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate())
    readonly property string fechaIso: root._aIso(input.text)

    Behavior on border.color { ColorAnimation { duration: 120 } }

    function limpiar() {
        input.text = ""
    }

    function _esValida(d, m, a) {
        if (isNaN(d) || isNaN(m) || isNaN(a) || m < 1 || m > 12 || d < 1 || d > 31) return false
        var fecha = new Date(a, m - 1, d)
        return fecha <= root.fechaHoy
    }

    function _aIso(texto) {
        if (texto.indexOf("_") !== -1) return ""
        var partes = texto.split("/")
        if (partes.length !== 3) return ""
        var d = parseInt(partes[0], 10)
        var m = parseInt(partes[1], 10)
        var a = parseInt(partes[2], 10)
        if (!root._esValida(d, m, a)) return ""
        var dd = d < 10 ? "0" + d : "" + d
        var mm = m < 10 ? "0" + m : "" + m
        return a + "-" + mm + "-" + dd
    }

    function _fijarFecha(fecha) {
        var dd = fecha.getDate() < 10 ? "0" + fecha.getDate() : "" + fecha.getDate()
        var mm = (fecha.getMonth() + 1) < 10 ? "0" + (fecha.getMonth() + 1) : "" + (fecha.getMonth() + 1)
        input.text = dd + "/" + mm + "/" + fecha.getFullYear()
        calendarioPopup.close()
    }

    // Genera las 42 celdas (6 semanas x 7 días, empezando en lunes) de un mes/año dados.
    function _generarCeldas(anio, mes) {
        var primerDia = new Date(anio, mes, 1)
        var offset = (primerDia.getDay() + 6) % 7 // lunes=0 ... domingo=6
        var inicio = new Date(anio, mes, 1 - offset)
        var celdas = []
        for (var i = 0; i < 42; i++) {
            var fecha = new Date(inicio.getFullYear(), inicio.getMonth(), inicio.getDate() + i)
            celdas.push({ dia: fecha.getDate(), delMes: fecha.getMonth() === mes, fecha: fecha })
        }
        return celdas
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 8

        Rectangle {
            width: 16
            height: 16
            radius: 2
            color: "transparent"
            border.width: 1.5
            border.color: Theme.primary

            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 4
                color: Theme.primary
            }

            TapHandler {
                onTapped: calendarioPopup.open()
            }
            HoverHandler { cursorShape: Qt.PointingHandCursor }
        }

        TextInput {
            id: input
            Layout.fillWidth: true
            font.pixelSize: 13
            color: Theme.text
            selectionColor: Theme.primary
            inputMask: "99/99/9999;_"
            verticalAlignment: TextInput.AlignVCenter
            clip: true
        }
    }

    Popup {
        id: calendarioPopup
        y: root.height + 4
        width: 260
        padding: 12
        modal: true
        focus: true

        property date mesMostrado: new Date()
        readonly property var celdas: root._generarCeldas(mesMostrado.getFullYear(), mesMostrado.getMonth())

        background: Rectangle {
            color: "white"
            radius: 10
            border.width: 1
            border.color: "#e5e8f0"
        }

        ColumnLayout {
            anchors.fill: parent
            spacing: 8

            RowLayout {
                Layout.fillWidth: true

                Text {
                    text: "‹"
                    font.pixelSize: 18
                    font.bold: true
                    color: Theme.primary
                    TapHandler {
                        onTapped: calendarioPopup.mesMostrado = new Date(
                            calendarioPopup.mesMostrado.getFullYear(),
                            calendarioPopup.mesMostrado.getMonth() - 1, 1)
                    }
                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                }

                Text {
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    font.bold: true
                    font.pixelSize: 13
                    color: Theme.text
                    text: Qt.formatDate(calendarioPopup.mesMostrado, "MMMM yyyy")
                }

                Text {
                    text: "›"
                    font.pixelSize: 18
                    font.bold: true
                    color: Theme.primary
                    TapHandler {
                        onTapped: calendarioPopup.mesMostrado = new Date(
                            calendarioPopup.mesMostrado.getFullYear(),
                            calendarioPopup.mesMostrado.getMonth() + 1, 1)
                    }
                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                }
            }

            Grid {
                columns: 7
                columnSpacing: 2
                rowSpacing: 2
                Layout.alignment: Qt.AlignHCenter

                Repeater {
                    model: ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
                    delegate: Text {
                        width: 30
                        horizontalAlignment: Text.AlignHCenter
                        text: modelData
                        font.pixelSize: 11
                        font.bold: true
                        color: Theme.text
                    }
                }
            }

            Grid {
                columns: 7
                columnSpacing: 2
                rowSpacing: 2
                Layout.alignment: Qt.AlignHCenter

                Repeater {
                    model: calendarioPopup.celdas

                    delegate: Rectangle {
                        required property var modelData
                        readonly property bool esHoy: modelData.delMes && root.fechaHoy.getTime() === modelData.fecha.getTime()
                        readonly property bool esFutura: modelData.delMes && modelData.fecha > root.fechaHoy
                        readonly property bool esSeleccionable: modelData.delMes && !esFutura

                        width: 30
                        height: 30
                        radius: 15
                        color: esHoy ? Theme.primary : "transparent"

                        Text {
                            anchors.centerIn: parent
                            text: parent.modelData.dia
                            font.pixelSize: 12
                            color: !parent.modelData.delMes
                                   ? "#c3c9de"
                                   : parent.esHoy
                                     ? "white"
                                     : parent.esFutura
                                       ? "#d3d8e8"
                                       : Theme.text
                        }

                        TapHandler { onTapped: if (parent.esSeleccionable) root._fijarFecha(parent.modelData.fecha) }
                        HoverHandler { cursorShape: parent.esSeleccionable ? Qt.PointingHandCursor : Qt.ForbiddenCursor }
                    }
                }
            }
        }
    }
}
