import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: window
    width: 1024
    height: 640
    minimumWidth: 900
    minimumHeight: 560
    visible: true
    visibility: Window.Maximized
    title: (typeof AppCtl !== "undefined" && AppCtl) ? AppCtl.appName : "Rename APP"
    color: Theme.background

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: splashComponent
    }

    Component {
        id: splashComponent
        SplashView {
            onFinalizado: stackView.replace(mainComponent)
        }
    }

    Component {
        id: mainComponent
        AppShell {}
    }
}
