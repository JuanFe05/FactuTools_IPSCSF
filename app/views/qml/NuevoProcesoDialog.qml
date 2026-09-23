import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

Dialog {
    id: root
    title: "Nuevo proceso"
    modal: true
    standardButtons: Dialog.NoButton
    width: 540
    anchors.centerIn: Overlay.overlay

    property var renombrarCtl: (typeof RenombrarCtl !== "undefined") ? RenombrarCtl : null

    readonly property bool modoCsv: root.renombrarCtl ? root.renombrarCtl.modoProceso === "csv" : false

    readonly property bool listoParaAnalizar: comboEmpresa.currentIndex !== -1
        && (root.modoCsv || radioExterna.checked || radioUrgencias.checked)
        && (root.modoCsv ? root.renombrarCtl.rutaCsv !== "" : fechaField.fechaIso !== "")
        && root.renombrarCtl
        && root.renombrarCtl.carpetaSeleccionada !== ""
        && !root.renombrarCtl.procesando

    function limpiarFormulario() {
        comboEmpresa.currentIndex = -1
        grupoTipoAtencion.checkedButton = null
        grupoModoProceso.checkedButton = radioModoBd
        fechaField.limpiar()
    }

    background: Rectangle {
        color: Theme.background
        radius: 16
        border.width: 1
        border.color: "#e5e8f0"
    }

    header: Label {
        text: root.title
        color: Theme.primaryDark
        font.pixelSize: 17
        font.bold: true
        padding: 20
        background: Rectangle { color: Theme.background; radius: 16 }
    }

    FolderDialog {
        id: dialogoCarpeta
        title: "Seleccionar carpeta principal"
        onAccepted: if (root.renombrarCtl) root.renombrarCtl.seleccionarCarpeta(selectedFolder)
    }

    FileDialog {
        id: dialogoCsv
        title: "Seleccionar archivo CSV"
        nameFilters: ["Archivos CSV (*.csv)"]
        onAccepted: if (root.renombrarCtl) root.renombrarCtl.seleccionarArchivoCsv(selectedFile)
    }

    ButtonGroup { id: grupoTipoAtencion }
    ButtonGroup { id: grupoModoProceso }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Sección 1 — Modalidad de procesamiento
        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 16
            Layout.bottomMargin: 16
            spacing: 10

            Text {
                text: "Modalidad de procesamiento"
                font.bold: true
                font.pixelSize: 12
                color: Theme.primaryDark
            }

            RowLayout {
                spacing: 28

                RadioButton {
                    id: radioModoBd
                    text: "Base de datos"
                    checked: true
                    ButtonGroup.group: grupoModoProceso
                    onCheckedChanged: if (checked && root.renombrarCtl) root.renombrarCtl.seleccionarModoProceso("bd")

                    indicator: Rectangle {
                        implicitWidth: 18
                        implicitHeight: 18
                        radius: 9
                        x: radioModoBd.leftPadding
                        y: parent.height / 2 - height / 2
                        border.width: 1.5
                        border.color: Theme.primary
                        color: "transparent"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 10
                            height: 10
                            radius: 5
                            color: Theme.primary
                            visible: radioModoBd.checked
                        }
                    }
                    contentItem: Text {
                        text: radioModoBd.text
                        color: Theme.text
                        leftPadding: radioModoBd.indicator.width + 8
                        verticalAlignment: Text.AlignVCenter
                    }
                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                }

                RadioButton {
                    id: radioModoCsv
                    text: "Archivo CSV"
                    ButtonGroup.group: grupoModoProceso
                    onCheckedChanged: if (checked && root.renombrarCtl) root.renombrarCtl.seleccionarModoProceso("csv")

                    indicator: Rectangle {
                        implicitWidth: 18
                        implicitHeight: 18
                        radius: 9
                        x: radioModoCsv.leftPadding
                        y: parent.height / 2 - height / 2
                        border.width: 1.5
                        border.color: Theme.primary
                        color: "transparent"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 10
                            height: 10
                            radius: 5
                            color: Theme.primary
                            visible: radioModoCsv.checked
                        }
                    }
                    contentItem: Text {
                        text: radioModoCsv.text
                        color: Theme.text
                        leftPadding: radioModoCsv.indicator.width + 8
                        verticalAlignment: Text.AlignVCenter
                    }
                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                }
            }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

        // Sección 2 — Empresa
        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 16
            Layout.bottomMargin: 16
            spacing: 10

            Text { text: "Empresa"; color: Theme.primaryDark; font.bold: true; font.pixelSize: 12 }

            ComboBox {
                id: comboEmpresa
                Layout.fillWidth: true
                model: root.renombrarCtl ? root.renombrarCtl.empresasDisponibles : []
                displayText: currentIndex === -1 ? "Seleccionar empresa" : currentText
                currentIndex: -1
                hoverEnabled: true
                onActivated: if (root.renombrarCtl) root.renombrarCtl.seleccionarEmpresa(currentText)

                background: Rectangle {
                    implicitHeight: 42
                    radius: 8
                    color: "white"
                    border.width: comboEmpresa.activeFocus ? 2 : 1
                    border.color: comboEmpresa.activeFocus ? Theme.primary : "#d7dbe8"
                    Behavior on border.color { ColorAnimation { duration: 120 } }
                }

                contentItem: Text {
                    text: comboEmpresa.displayText
                    color: Theme.text
                    leftPadding: 12
                    rightPadding: 12
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                indicator: Text {
                    text: "▾"
                    color: Theme.primary
                    anchors.right: parent.right
                    anchors.rightMargin: 14
                    anchors.verticalCenter: parent.verticalCenter
                }

                delegate: ItemDelegate {
                    width: comboEmpresa.width
                    highlighted: comboEmpresa.highlightedIndex === index
                    contentItem: Text {
                        text: modelData
                        color: Theme.text
                        leftPadding: 8
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                    background: Rectangle {
                        color: highlighted ? "#eef1fb" : "white"
                    }
                }

                HoverHandler { cursorShape: Qt.PointingHandCursor }
            }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

        // Sección 3 — Tipo de atención (solo si BD)
        ColumnLayout {
            visible: !root.modoCsv
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 16
            Layout.bottomMargin: 16
            spacing: 10

            Text { text: "Tipo de atención"; color: Theme.primaryDark; font.bold: true; font.pixelSize: 12 }

            RowLayout {
                spacing: 28

                RadioButton {
                    id: radioExterna
                    text: "Consulta Externa"
                    ButtonGroup.group: grupoTipoAtencion
                    onCheckedChanged: if (checked && root.renombrarCtl) root.renombrarCtl.seleccionarTipoAtencion("Consulta Externa")

                    indicator: Rectangle {
                        implicitWidth: 18
                        implicitHeight: 18
                        radius: 9
                        x: radioExterna.leftPadding
                        y: parent.height / 2 - height / 2
                        border.width: 1.5
                        border.color: Theme.primary
                        color: "transparent"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 10
                            height: 10
                            radius: 5
                            color: Theme.primary
                            visible: radioExterna.checked
                        }
                    }
                    contentItem: Text {
                        text: radioExterna.text
                        color: Theme.text
                        leftPadding: radioExterna.indicator.width + 8
                        verticalAlignment: Text.AlignVCenter
                    }
                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                }

                RadioButton {
                    id: radioUrgencias
                    text: "Urgencias"
                    ButtonGroup.group: grupoTipoAtencion
                    onCheckedChanged: if (checked && root.renombrarCtl) root.renombrarCtl.seleccionarTipoAtencion("Urgencias")

                    indicator: Rectangle {
                        implicitWidth: 18
                        implicitHeight: 18
                        radius: 9
                        x: radioUrgencias.leftPadding
                        y: parent.height / 2 - height / 2
                        border.width: 1.5
                        border.color: Theme.primary
                        color: "transparent"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 10
                            height: 10
                            radius: 5
                            color: Theme.primary
                            visible: radioUrgencias.checked
                        }
                    }
                    contentItem: Text {
                        text: radioUrgencias.text
                        color: Theme.text
                        leftPadding: radioUrgencias.indicator.width + 8
                        verticalAlignment: Text.AlignVCenter
                    }
                    HoverHandler { cursorShape: Qt.PointingHandCursor }
                }
            }
        }

        Rectangle { visible: !root.modoCsv; Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

        // Sección 4 — Tipo de atención (fijo en modo CSV)
        ColumnLayout {
            visible: root.modoCsv
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 16
            Layout.bottomMargin: 16
            spacing: 10

            Text { text: "Tipo de atención"; color: Theme.primaryDark; font.bold: true; font.pixelSize: 12 }
            Text { text: "Urgencias"; color: Theme.text; font.pixelSize: 13 }
        }

        Rectangle { visible: root.modoCsv; Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

        // Sección 5 — Fecha desde (solo si BD)
        ColumnLayout {
            visible: !root.modoCsv
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 16
            Layout.bottomMargin: 16
            spacing: 10

            Text { text: "Fecha desde"; color: Theme.primaryDark; font.bold: true; font.pixelSize: 12 }

            FechaField {
                id: fechaField
                onFechaIsoChanged: if (root.renombrarCtl) root.renombrarCtl.establecerFechaDesde(fechaIso)
            }
        }

        Rectangle { visible: !root.modoCsv; Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

        // Sección 6 — Archivo CSV (solo si CSV)
        ColumnLayout {
            visible: root.modoCsv
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 16
            Layout.bottomMargin: 16
            spacing: 10

            Text { text: "Archivo CSV"; color: Theme.primaryDark; font.bold: true; font.pixelSize: 12 }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                SecondaryButton {
                    text: "Seleccionar CSV"
                    onClicked: dialogoCsv.open()
                }

                Text {
                    Layout.fillWidth: true
                    elide: Text.ElideMiddle
                    color: Theme.text
                    font.pixelSize: 12
                    text: (root.renombrarCtl && root.renombrarCtl.rutaCsv)
                          ? root.renombrarCtl.rutaCsv.split('/').pop()
                          : "Ningún archivo seleccionado"
                }
            }
        }

        Rectangle { visible: root.modoCsv; Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

        // Sección 7 — Carpeta
        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 16
            Layout.bottomMargin: 16
            spacing: 10

            Text { text: "Carpeta"; color: Theme.primaryDark; font.bold: true; font.pixelSize: 12 }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                SecondaryButton {
                    text: "Seleccionar carpeta"
                    onClicked: dialogoCarpeta.open()
                }

                Text {
                    Layout.fillWidth: true
                    elide: Text.ElideMiddle
                    color: Theme.text
                    font.pixelSize: 12
                    text: (root.renombrarCtl && root.renombrarCtl.carpetaSeleccionada)
                          ? root.renombrarCtl.carpetaSeleccionada.split('/').pop()
                          : "Ninguna carpeta seleccionada"
                }
            }

            ColumnLayout {
                visible: root.renombrarCtl && root.renombrarCtl.carpetaSeleccionada !== ""
                spacing: 8
                Layout.fillWidth: true
                Layout.topMargin: 8

                Rectangle { Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

                Text {
                    text: root.renombrarCtl ? ("📁 Subcarpetas encontradas: " + root.renombrarCtl.totalSubcarpetas) : ""
                    font.pixelSize: 11
                    color: Theme.text
                }
                Text {
                    text: root.renombrarCtl ? ("📄 Archivos PDF encontrados: " + root.renombrarCtl.totalPdfs) : ""
                    font.pixelSize: 11
                    color: Theme.text
                }
                Text {
                    text: root.renombrarCtl && root.renombrarCtl.erroresPrevios.length === 0
                          ? "✓ Carpeta lista para analizar"
                          : "⚠ Carpeta con advertencias"
                    font.pixelSize: 11
                    font.bold: true
                    color: root.renombrarCtl && root.renombrarCtl.erroresPrevios.length === 0
                           ? Theme.success
                           : Theme.danger
                }
                Text {
                    visible: root.renombrarCtl && root.renombrarCtl.erroresPrevios.length > 0
                    text: root.renombrarCtl ? root.renombrarCtl.erroresPrevios.join(" • ") : ""
                    font.pixelSize: 10
                    color: Theme.danger
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }

        Item { Layout.fillHeight: true }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

        // Sección 8 — Acciones
        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 12
            Layout.bottomMargin: 12
            spacing: 12

            Item { Layout.fillWidth: true }

            SecondaryButton {
                text: "Cancelar"
                onClicked: root.close()
            }
            PrimaryButton {
                text: "Analizar"
                cargando: root.renombrarCtl ? root.renombrarCtl.procesando : false
                textoCargando: "Analizando..."
                enabled: root.listoParaAnalizar
                onClicked: {
                    if (root.renombrarCtl) root.renombrarCtl.analizar()
                    root.close()
                }
            }
        }
    }
}
