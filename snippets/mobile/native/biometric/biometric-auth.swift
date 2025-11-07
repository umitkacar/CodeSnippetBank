import LocalAuthentication
import SwiftUI

class BiometricAuthManager {
    static let shared = BiometricAuthManager()
    
    private init() {}
    
    func canAuthenticate() -> Bool {
        let context = LAContext()
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }
    
    func authenticate(reason: String, completion: @escaping (Result<Void, Error>) -> Void) {
        let context = LAContext()
        
        context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, error in
            DispatchQueue.main.async {
                if success {
                    completion(.success(()))
                } else if let error = error {
                    completion(.failure(error))
                }
            }
        }
    }
    
    func getBiometricType() -> BiometricType {
        let context = LAContext()
        _ = context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: nil)
        
        switch context.biometryType {
        case .faceID:
            return .faceID
        case .touchID:
            return .touchID
        default:
            return .none
        }
    }
}

enum BiometricType {
    case faceID
    case touchID
    case none
}

struct BiometricAuthView: View {
    @State private var isAuthenticated = false
    @State private var errorMessage: String?
    
    var body: some View {
        VStack(spacing: 20) {
            if isAuthenticated {
                Text("Authenticated Successfully!")
                    .font(.title)
                    .foregroundColor(.green)
            } else {
                Text("Biometric Authentication Required")
                    .font(.title2)
                
                Button("Authenticate") {
                    authenticate()
                }
                .buttonStyle(.borderedProminent)
                
                if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                }
            }
        }
        .padding()
    }
    
    private func authenticate() {
        BiometricAuthManager.shared.authenticate(reason: "Authenticate to access the app") { result in
            switch result {
            case .success:
                isAuthenticated = true
                errorMessage = nil
            case .failure(let error):
                errorMessage = error.localizedDescription
            }
        }
    }
}
