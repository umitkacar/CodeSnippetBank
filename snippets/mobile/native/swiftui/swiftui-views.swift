import SwiftUI

// Basic SwiftUI View
struct ContentView: View {
    @State private var counter = 0

    var body: some View {
        VStack(spacing: 20) {
            Text("Counter: \(counter)")
                .font(.largeTitle)
                .fontWeight(.bold)

            HStack(spacing: 16) {
                Button(action: { counter -= 1 }) {
                    Image(systemName: "minus.circle.fill")
                        .font(.title)
                }

                Button(action: { counter += 1 }) {
                    Image(systemName: "plus.circle.fill")
                        .font(.title)
                }
            }

            Button("Reset") {
                counter = 0
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

// Custom Button Style
struct CustomButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding()
            .background(configuration.isPressed ? Color.blue.opacity(0.5) : Color.blue)
            .foregroundColor(.white)
            .cornerRadius(10)
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
    }
}

// Card View
struct CardView<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding()
            .background(Color.white)
            .cornerRadius(12)
            .shadow(color: .gray.opacity(0.3), radius: 5, x: 0, y: 2)
    }
}

// List View with Navigation
struct ItemListView: View {
    let items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]

    var body: some View {
        NavigationView {
            List(items, id: \.self) { item in
                NavigationLink(destination: DetailView(item: item)) {
                    HStack {
                        Image(systemName: "folder")
                        Text(item)
                    }
                }
            }
            .navigationTitle("Items")
        }
    }
}

struct DetailView: View {
    let item: String

    var body: some View {
        VStack {
            Text(item)
                .font(.title)
                .padding()
            Spacer()
        }
        .navigationTitle("Details")
    }
}

// Form View
struct FormView: View {
    @State private var name = ""
    @State private var email = ""
    @State private var isSubscribed = false
    @State private var selectedOption = 0

    let options = ["Option 1", "Option 2", "Option 3"]

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Personal Information")) {
                    TextField("Name", text: $name)
                    TextField("Email", text: $email)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                }

                Section(header: Text("Preferences")) {
                    Toggle("Subscribe to newsletter", isOn: $isSubscribed)

                    Picker("Select option", selection: $selectedOption) {
                        ForEach(0..<options.count, id: \.self) { index in
                            Text(options[index])
                        }
                    }
                }

                Section {
                    Button("Submit") {
                        print("Form submitted")
                    }
                    .frame(maxWidth: .infinity)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(10)
                }
            }
            .navigationTitle("Form")
        }
    }
}

// Grid View
struct GridView: View {
    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible()),
        GridItem(.flexible())
    ]

    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 16) {
                ForEach(1...12, id: \.self) { index in
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.blue)
                        .frame(height: 100)
                        .overlay(
                            Text("\(index)")
                                .foregroundColor(.white)
                                .font(.title)
                        )
                }
            }
            .padding()
        }
    }
}
