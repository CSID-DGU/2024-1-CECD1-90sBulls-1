//
//  SwiftUI_MQTTApp.swift
//  SwiftUI_MQTT
//
//

import SwiftUI

@main
struct SwiftUI_MQTTApp: App {
    @StateObject var mqttManager = MQTTManager.shared()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(mqttManager)
        }
    }
}
