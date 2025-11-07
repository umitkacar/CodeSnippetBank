import SwiftUI

struct NavigationExample: View {
    @State private var path = NavigationPath()
    
    var body: some View {
        NavigationStack(path: $path) {
            List {
                NavigationLink("Go to Details", value: "details")
                NavigationLink("Go to Settings", value: "settings")
            }
            .navigationTitle("Home")
            .navigationDestination(for: String.self) { destination in
                switch destination {
                case "details":
                    DetailsView()
                case "settings":
                    SettingsView()
                default:
                    Text("Unknown")
                }
            }
        }
    }
}

struct DetailsView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack {
            Text("Details Screen")
            Button("Go Back") {
                dismiss()
            }
        }
        .navigationTitle("Details")
    }
}

struct SettingsView: View {
    var body: some View {
        Text("Settings Screen")
            .navigationTitle("Settings")
    }
}
