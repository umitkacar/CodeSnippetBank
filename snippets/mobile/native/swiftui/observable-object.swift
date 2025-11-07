import SwiftUI
import Combine

// Observable Object for State Management
class UserViewModel: ObservableObject {
    @Published var name: String = ""
    @Published var email: String = ""
    @Published var isLoggedIn: Bool = false
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    func login(email: String, password: String) {
        isLoading = true
        errorMessage = nil

        // Simulate API call
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            if email.isEmpty || password.isEmpty {
                self.errorMessage = "Email and password are required"
                self.isLoading = false
            } else {
                self.email = email
                self.isLoggedIn = true
                self.isLoading = false
            }
        }
    }

    func logout() {
        name = ""
        email = ""
        isLoggedIn = false
    }
}

// Using Observable Object in View
struct LoginView: View {
    @StateObject private var viewModel = UserViewModel()
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 20) {
            if viewModel.isLoading {
                ProgressView()
            } else if viewModel.isLoggedIn {
                Text("Welcome, \(viewModel.email)")
                    .font(.title)

                Button("Logout") {
                    viewModel.logout()
                }
                .buttonStyle(.borderedProminent)
            } else {
                TextField("Email", text: $email)
                    .textFieldStyle(.roundedBorder)
                    .autocapitalization(.none)

                SecureField("Password", text: $password)
                    .textFieldStyle(.roundedBorder)

                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                Button("Login") {
                    viewModel.login(email: email, password: password)
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
    }
}

// Cart View Model
class CartViewModel: ObservableObject {
    @Published var items: [CartItem] = []

    var totalPrice: Double {
        items.reduce(0) { $0 + ($1.price * Double($1.quantity)) }
    }

    var itemCount: Int {
        items.reduce(0) { $0 + $1.quantity }
    }

    func addItem(_ item: CartItem) {
        if let index = items.firstIndex(where: { $0.id == item.id }) {
            items[index].quantity += 1
        } else {
            items.append(item)
        }
    }

    func removeItem(_ item: CartItem) {
        items.removeAll { $0.id == item.id }
    }

    func updateQuantity(_ item: CartItem, quantity: Int) {
        if let index = items.firstIndex(where: { $0.id == item.id }) {
            items[index].quantity = quantity
        }
    }

    func clearCart() {
        items.removeAll()
    }
}

struct CartItem: Identifiable {
    let id: String
    let name: String
    let price: Double
    var quantity: Int
}

// Environment Object Example
struct ShoppingApp: View {
    @StateObject private var cart = CartViewModel()

    var body: some View {
        TabView {
            ProductListView()
                .tabItem {
                    Label("Products", systemImage: "bag")
                }

            CartView()
                .tabItem {
                    Label("Cart", systemImage: "cart")
                }
        }
        .environmentObject(cart)
    }
}

struct ProductListView: View {
    @EnvironmentObject var cart: CartViewModel

    let products = [
        CartItem(id: "1", name: "Product 1", price: 19.99, quantity: 1),
        CartItem(id: "2", name: "Product 2", price: 29.99, quantity: 1),
        CartItem(id: "3", name: "Product 3", price: 39.99, quantity: 1),
    ]

    var body: some View {
        List(products) { product in
            HStack {
                VStack(alignment: .leading) {
                    Text(product.name)
                        .font(.headline)
                    Text("$\(product.price, specifier: "%.2f")")
                        .font(.subheadline)
                }

                Spacer()

                Button("Add to Cart") {
                    cart.addItem(product)
                }
                .buttonStyle(.borderedProminent)
            }
        }
    }
}

struct CartView: View {
    @EnvironmentObject var cart: CartViewModel

    var body: some View {
        VStack {
            List {
                ForEach(cart.items) { item in
                    HStack {
                        Text(item.name)
                        Spacer()
                        Text("$\(item.price * Double(item.quantity), specifier: "%.2f")")
                    }
                }
            }

            Text("Total: $\(cart.totalPrice, specifier: "%.2f")")
                .font(.title)
                .padding()

            Button("Clear Cart") {
                cart.clearCart()
            }
            .buttonStyle(.bordered)
        }
    }
}
