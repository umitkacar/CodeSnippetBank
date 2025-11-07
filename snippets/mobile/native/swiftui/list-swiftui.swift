import SwiftUI

struct Item: Identifiable {
    let id = UUID()
    let title: String
    let subtitle: String
}

struct ListView: View {
    let items = [
        Item(title: "Item 1", subtitle: "Subtitle 1"),
        Item(title: "Item 2", subtitle: "Subtitle 2"),
        Item(title: "Item 3", subtitle: "Subtitle 3")
    ]
    
    var body: some View {
        List(items) { item in
            VStack(alignment: .leading) {
                Text(item.title)
                    .font(.headline)
                Text(item.subtitle)
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
        }
    }
}

struct SearchableListView: View {
    @State private var searchText = ""
    
    let items = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
    
    var filteredItems: [String] {
        if searchText.isEmpty {
            return items
        }
        return items.filter { $0.localizedCaseInsensitiveContains(searchText) }
    }
    
    var body: some View {
        NavigationView {
            List(filteredItems, id: \.self) { item in
                Text(item)
            }
            .searchable(text: $searchText)
            .navigationTitle("Fruits")
        }
    }
}
