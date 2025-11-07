import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class ListItem(
    val id: Int,
    val title: String,
    val subtitle: String
)

@Composable
fun ItemListCompose() {
    val items = remember {
        List(20) { index ->
            ListItem(
                id = index,
                title = "Item $index",
                subtitle = "Subtitle for item $index"
            )
        }
    }
    
    LazyColumn {
        items(items) { item ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(item.title, style = MaterialTheme.typography.titleMedium)
                    Text(item.subtitle, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
}
