import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/home_screen.dart';
import 'screens/upload_screen.dart';
import 'screens/verify_screen.dart';

void main() {
  runApp(TrueImageApp());
}

class TrueImageApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false, // Removes debug banner
      title: 'True Image App',
      theme: ThemeData(
        primarySwatch: Colors.blue, // App color theme
      ),
      initialRoute: '/login', // Start at login screen
      routes: {
        '/login': (context) => LoginScreen(),
        '/register': (context) => RegisterScreen(),
        '/home': (context) => HomeScreen(),
        '/upload': (context) => UploadScreen(),
        '/verify': (context) => VerifyScreen(),
      },
    );
  }
}
