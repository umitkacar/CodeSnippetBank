import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Details : Screen("details/{id}") {
        fun createRoute(id: String) = "details/$id"
    }
    object Profile : Screen("profile")
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    
    NavHost(navController = navController, startDestination = Screen.Home.route) {
        composable(Screen.Home.route) {
            HomeScreen(navController)
        }
        
        composable(Screen.Details.route) { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id")
            DetailsScreen(id, navController)
        }
        
        composable(Screen.Profile.route) {
            ProfileScreen(navController)
        }
    }
}
