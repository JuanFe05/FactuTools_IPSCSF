import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: Theme.background

    readonly property var renombrarCtl: (typeof RenombrarCtl !== "undefined") ? RenombrarCtl : null

    NuevoProcesoDialog {
        id: nuevoProcesoDialog
    }

    ConfirmacionDialog {
        id: confirmacionDialog
        empresa: root.renombrarCtl ? root.renombrarCtl.empresaSeleccionada : ""
        onConfirmado: if (root.renombrarCtl) root.renombrarCtl.ejecutarRenombrado()
    }

    ConfirmarBorradoDialog {
        id: confirmarBorradoDialog
        onConfirmado: {
            if (root.renombrarCtl) root.renombrarCtl.borrarTodo()
            nuevoProcesoDialog.limpiarFormulario()
        }
    }

    ProcesandoOverlay {
        id: overlayProcesando
        titulo: root.renombrarCtl && root.renombrarCtl.accionActual === "renombrar"
            ? "Renombrando soportes y carpetas..."
            : "Analizando información..."
        visible: root.renombrarCtl ? root.renombrarCtl.procesando : false
        actual: root.renombrarCtl ? root.renombrarCtl.progresoActual : 0
        total: root.renombrarCtl ? root.renombrarCtl.progresoTotal : 0
        mensaje: root.renombrarCtl ? root.renombrarCtl.mensajeProgreso : ""
    }

    ResultadoDialog {
        id: resultadoDialog
    }

    Connections {
        target: root.renombrarCtl
        function onProcesoTerminado(resumen) {
            resultadoDialog.resumen = resumen
            resultadoDialog.exito = resumen.accion === "renombrar"
                ? (resumen.subcarpetasConError || 0) === 0
                : (resumen.registrosNoEncontrados || 0) === 0
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
                    text: "Renombramiento de soportes"
                    font.pixelSize: 24
                    font.bold: true
                    color: Theme.primary
                }
                Text {
                    text: "Selecciona una carpeta principal para analizar, validar y renombrar automáticamente sus subcarpetas y archivos PDF."
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
                text: "Renombrar"
                enabled: root.renombrarCtl ? root.renombrarCtl.renombrarHabilitado : false
                onClicked: confirmacionDialog.open()
            }
            SecondaryButton {
                text: "Borrar todo"
                colorFondoPersonalizado: "#e63946"
                colorTextoPersonalizado: "#f6f9f7"
                enabled: root.renombrarCtl ? (root.renombrarCtl.resultados.length > 0) : false
                onClicked: confirmarBorradoDialog.open()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 18

            IndicatorCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                valor: root.renombrarCtl ? String(root.renombrarCtl.totalSubcarpetas) : "0"
                etiqueta: "Subcarpetas detectadas"
                colorAcento: Theme.primary
            }
            IndicatorCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                valor: root.renombrarCtl ? String(root.renombrarCtl.totalRegistrosEncontrados) : "0"
                etiqueta: "Registros encontrados"
                colorAcento: Theme.success
            }
            IndicatorCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                valor: root.renombrarCtl ? String(root.renombrarCtl.totalRegistrosNoEncontrados) : "0"
                etiqueta: "Registros sin coincidencia"
                colorAcento: Theme.danger
            }
            IndicatorCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                valor: root.renombrarCtl ? root.renombrarCtl.totalGeneral.toLocaleString(Qt.locale(), "f", 0) : "0"
                etiqueta: "Total General"
                colorAcento: Theme.primary
            }
            IndicatorCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 100
                valor: root.renombrarCtl ? String(root.renombrarCtl.carpetasConErrores) : "0"
                etiqueta: "Carpetas con errores"
                colorAcento: Theme.danger
            }
        }

        ResultsTable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            filas: root.renombrarCtl ? root.renombrarCtl.resultados : []
        }
    }
}
