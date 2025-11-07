import androidx.compose.runtime.*
import kotlinx.coroutines.delay

@Composable
fun LaunchedEffectExample() {
    var count by remember { mutableStateOf(0) }
    
    LaunchedEffect(Unit) {
        while (true) {
            delay(1000)
            count++
        }
    }
    
    Text("Count: $count")
}

@Composable
fun DisposableEffectExample() {
    DisposableEffect(Unit) {
        println("Effect started")
        
        onDispose {
            println("Effect disposed")
        }
    }
}

@Composable
fun SideEffectExample(value: Int) {
    SideEffect {
        println("Value changed: $value")
    }
}
