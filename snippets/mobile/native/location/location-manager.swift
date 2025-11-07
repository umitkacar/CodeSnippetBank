import CoreLocation
import SwiftUI

class LocationManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    @Published var location: CLLocation?
    @Published var authorizationStatus: CLAuthorizationStatus?
    @Published var error: String?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
    }

    func requestPermission() {
        manager.requestWhenInUseAuthorization()
    }

    func startUpdating() {
        manager.startUpdatingLocation()
    }

    func stopUpdating() {
        manager.stopUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        location = locations.last
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        self.error = error.localizedDescription
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorizationStatus = manager.authorizationStatus
    }
}

struct LocationView: View {
    @StateObject private var locationManager = LocationManager()

    var body: some View {
        VStack(spacing: 20) {
            if let location = locationManager.location {
                Text("Latitude: \(location.coordinate.latitude)")
                Text("Longitude: \(location.coordinate.longitude)")
            } else {
                Text("Location not available")
            }

            Button("Request Permission") {
                locationManager.requestPermission()
            }

            Button("Start Tracking") {
                locationManager.startUpdating()
            }

            Button("Stop Tracking") {
                locationManager.stopUpdating()
            }

            if let error = locationManager.error {
                Text("Error: \(error)")
                    .foregroundColor(.red)
            }
        }
        .padding()
    }
}

// Geocoding Service
class GeocodingService {
    static func reverseGeocode(
        location: CLLocation,
        completion: @escaping (Result<CLPlacemark, Error>) -> Void
    ) {
        let geocoder = CLGeocoder()

        geocoder.reverseGeocodeLocation(location) { placemarks, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            if let placemark = placemarks?.first {
                completion(.success(placemark))
            }
        }
    }

    static func geocode(
        address: String,
        completion: @escaping (Result<CLLocation, Error>) -> Void
    ) {
        let geocoder = CLGeocoder()

        geocoder.geocodeAddressString(address) { placemarks, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            if let location = placemarks?.first?.location {
                completion(.success(location))
            }
        }
    }
}

// Distance Calculator
extension CLLocation {
    func distance(to location: CLLocation) -> String {
        let distanceInMeters = distance(from: location)
        let distanceInKilometers = distanceInMeters / 1000

        if distanceInKilometers < 1 {
            return String(format: "%.0f meters", distanceInMeters)
        } else {
            return String(format: "%.2f km", distanceInKilometers)
        }
    }
}
