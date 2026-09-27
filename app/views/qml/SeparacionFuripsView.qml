import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: Theme.background

    readonly property var separacionCtl: (typeof SeparacionFuripsCtl !== "undefined") ? SeparacionFuripsCtl : null

    NuevoProcesoFuripsDialog {
        id: nuevoProcesoDialog
    }

    ConfirmacionSeparacionDialog {
        id: confirmacionDialog
        onConfirmado: if (root.separacionCtl) root.separacionCtl.ejecutarSeparacion()
    }

    ConfirmarBorradoDialog {
        id: confirmarBorradoDialog
        mensaje: "Se perderá la carpeta y los resultados del proceso actual."
        onConfirmado: if (root.separacionCtl) root.separacionCtl.borrarTodo()
    }

    ProcesandoOverlay {
        id: overlayProcesando
        titulo: root.separacionCtl && root.separacionCtl.accionActual === "separar"
            ? "Separando archivos FURIPS..."
            : "Analizando información..."
        visible: root.separacionCtl ? root.separacionCtl.procesando : false
        actual: root.separacionCtl ? root.separacionCtl.progresoActual : 0
        total: root.separacionCtl ? root.separacionCtl.progresoTotal : 0
        mensaje: root.separacionCtl ? root.separacionCtl.mensajeProgreso : ""
    }

    ResultadoSeparacionDialog {
        id: resultadoDialog
    }

    Connections {
        target: root.separacionCtl
        function onProcesoTerminado(resumen) {
            resultadoDialog.resumen = resumen
            resultadoDialog.exito = (resumen.facturasConError || 0) === 0
            resultadoDialog.open()
        }
        function onProcesoError(mensaje) {
            resultadoDialog.exito = false
            resultadoDialog.resumen = {}
            resultadoDialog.open()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 18

        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            ColumnLayout {
                spacing: 4
                Layout.fillWidth: true

                Text {
                    text: "Separación de FURIPS"
                    font.pixelSize: 24
                    font.bold: true
                    color: Theme.primary
                }
                Text {
                    text: "Selecciona una carpeta con archivos FURIPS1/FURIPS2 para separarlos en subcarpetas por número de factura."
                    font.pixelSize: 13
                    color: Theme.text
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            PrimaryButton {
                text: "Nuevo proceso"
                iconoTexto: "+"
                onClicked: nuevoProcesoDialog.open()
            }
            PrimaryButton {
                text: "Separar"
                enabled: root.separacionCtl ? root.separacionCtl.separarHabilitado : false
                onClicked: confirmacionDialog.open()
            }
            SecondaryButton {
                text: "Borrar todo"
                colorFondoPersonalizado: "#e63946"
                colorTextoPersonalizado: "#f6f9f7"
                enabled: root.separacionCtl ? root.separacionCtl.hayDatosCargados : false
                onClicked: confirmarBorradoDialog.open()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 18

            IndicatorCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                valor: root.separacionCtl ? String(root.separacionCtl.totalTxtEncontrados) : "0"
                etiqueta: "Archivos TXT encontrados"
                colorAcento: Theme.primary
            }
            IndicatorCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                valor: root.separacionCtl ? String(root.separacionCtl.carpetasACrear) : "0"
                etiqueta: "Carpetas que se crearán"
                colorAcento: Theme.success
            }
            IndicatorCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                valor: root.separacionCtl ? String(root.separacionCtl.carpetasCreadas) : "0"
                etiqueta: "Carpetas creadas"
                colorAcento: Theme.primary
            }
        }

        FuripsResultsTable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            filas: root.separacionCtl ? root.separacionCtl.resultados : []
        }
    }
}
