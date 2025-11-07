import CoreData
import SwiftUI

@available(iOS 15.0, *)
struct FetchRequestExample: View {
    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \User.name, ascending: true)],
        predicate: NSPredicate(format: "age >= %d", 18)
    )
    var users: FetchedResults<User>
    
    var body: some View {
        List(users) { user in
            Text(user.name ?? "")
        }
    }
}
