//
//  ninetysBullsApp.swift
//  ninetysBulls
//
//  Created by 차차 on 6/22/24.
//

import SwiftUI

@main
struct ninetysBullsApp: App {
    let persistenceController = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}
