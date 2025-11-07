import UIKit

class CustomTableViewController: UITableViewController {
    
    var items: [String] = []
    
    override func viewDidLoad() {
        super.viewDidLoad()
        items = Array(1...20).map { "Item \($0)" }
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "cell")
    }
    
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return items.count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "cell", for: indexPath)
        cell.textLabel?.text = items[indexPath.row]
        return cell
    }
    
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        print("Selected: \(items[indexPath.row])")
        tableView.deselectRow(at: indexPath, animated: true)
    }
}
