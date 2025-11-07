import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver

class MainActivity : ComponentActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyAppContent()
        }
    }
    
    override fun onStart() {
        super.onStart()
        println("Activity started")
    }
    
    override fun onResume() {
        super.onResume()
        println("Activity resumed")
    }
    
    override fun onPause() {
        super.onPause()
        println("Activity paused")
    }
    
    override fun onStop() {
        super.onStop()
        println("Activity stopped")
    }
    
    override fun onDestroy() {
        super.onDestroy()
        println("Activity destroyed")
    }
}

@Composable
fun LifecycleAwareComposable() {
    val lifecycleOwner = androidx.lifecycle.compose.LocalLifecycleOwner.current
    
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_CREATE -> println("Composable created")
                Lifecycle.Event.ON_START -> println("Composable started")
                Lifecycle.Event.ON_RESUME -> println("Composable resumed")
                Lifecycle.Event.ON_PAUSE -> println("Composable paused")
                Lifecycle.Event.ON_STOP -> println("Composable stopped")
                Lifecycle.Event.ON_DESTROY -> println("Composable destroyed")
                else -> {}
            }
        }
        
        lifecycleOwner.lifecycle.addObserver(observer)
        
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }
}
