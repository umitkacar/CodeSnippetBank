import Foundation

// Network Manager
class NetworkManager {
    static let shared = NetworkManager()

    private init() {}

    func request<T: Decodable>(
        url: URL,
        method: HTTPMethod = .get,
        headers: [String: String]? = nil,
        body: Data? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.httpBody = body

        // Set headers
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        headers?.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let data = data else {
                completion(.failure(NetworkError.noData))
                return
            }

            do {
                let decoded = try JSONDecoder().decode(T.self, from: data)
                completion(.success(decoded))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }

    func get<T: Decodable>(
        url: URL,
        headers: [String: String]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        request(url: url, method: .get, headers: headers, completion: completion)
    }

    func post<T: Decodable>(
        url: URL,
        body: Encodable,
        headers: [String: String]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        let bodyData = try? JSONEncoder().encode(body)
        request(url: url, method: .post, headers: headers, body: bodyData, completion: completion)
    }

    func put<T: Decodable>(
        url: URL,
        body: Encodable,
        headers: [String: String]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        let bodyData = try? JSONEncoder().encode(body)
        request(url: url, method: .put, headers: headers, body: bodyData, completion: completion)
    }

    func delete<T: Decodable>(
        url: URL,
        headers: [String: String]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        request(url: url, method: .delete, headers: headers, completion: completion)
    }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
    case patch = "PATCH"
}

enum NetworkError: Error {
    case noData
    case invalidResponse
    case decodingError
}

// Async/Await version
extension NetworkManager {
    func request<T: Decodable>(
        url: URL,
        method: HTTPMethod = .get,
        headers: [String: String]? = nil,
        body: Data? = nil
    ) async throws -> T {
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.httpBody = body

        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        headers?.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(T.self, from: data)
    }

    func get<T: Decodable>(
        url: URL,
        headers: [String: String]? = nil
    ) async throws -> T {
        try await request(url: url, method: .get, headers: headers)
    }

    func post<T: Decodable>(
        url: URL,
        body: Encodable,
        headers: [String: String]? = nil
    ) async throws -> T {
        let bodyData = try JSONEncoder().encode(body)
        return try await request(url: url, method: .post, headers: headers, body: bodyData)
    }
}

// Usage Example
struct User: Codable {
    let id: Int
    let name: String
    let email: String
}

class UserService {
    func fetchUsers(completion: @escaping (Result<[User], Error>) -> Void) {
        guard let url = URL(string: "https://api.example.com/users") else { return }

        NetworkManager.shared.get(url: url) { (result: Result<[User], Error>) in
            completion(result)
        }
    }

    func createUser(user: User, completion: @escaping (Result<User, Error>) -> Void) {
        guard let url = URL(string: "https://api.example.com/users") else { return }

        NetworkManager.shared.post(url: url, body: user) { (result: Result<User, Error>) in
            completion(result)
        }
    }

    // Async version
    func fetchUsers() async throws -> [User] {
        guard let url = URL(string: "https://api.example.com/users") else {
            throw NetworkError.invalidResponse
        }
        return try await NetworkManager.shared.get(url: url)
    }

    func createUser(user: User) async throws -> User {
        guard let url = URL(string: "https://api.example.com/users") else {
            throw NetworkError.invalidResponse
        }
        return try await NetworkManager.shared.post(url: url, body: user)
    }
}
