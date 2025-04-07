import 'package:flutter/material.dart';
import 'camera_screen.dart'; // Import Camera screen
import 'gallery_screen.dart'; // Import Gallery screen

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  // List of screens for navigation
  final List<Widget> _screens = [
    HomeContent(),
    CameraScreen(), // Add Camera screen
    GalleryScreen(), // Add Gallery screen
  ];

  // Function to handle bottom navigation item selection
  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false, // Prevents UI shift due to keyboard
      appBar: AppBar(
        title: Text(
          "True Image App",
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.deepPurpleAccent,
        elevation: 4,
        actions: [
          IconButton(
            icon: Icon(Icons.logout, color: Colors.white),
            onPressed: () => Navigator.pushNamed(context, '/login'),
          ),
        ],
      ),
      body: _screens[_selectedIndex],
      bottomNavigationBar: SafeArea(
        child: BottomNavigationBar(
          type: BottomNavigationBarType.fixed, // Prevents shifting
          currentIndex: _selectedIndex,
          onTap: _onItemTapped,
          selectedItemColor: Colors.deepPurpleAccent,
          unselectedItemColor: Colors.grey,
          items: const <BottomNavigationBarItem>[
            BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
            BottomNavigationBarItem(
              icon: Icon(Icons.camera_alt),
              label: 'Camera',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.photo_library),
              label: 'Gallery',
            ),
          ],
        ),
      ),
    );
  }
}

// Home content screen (default screen)
class HomeContent extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            child: Container(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Image.asset(
                    'assets/images/logo.png',
                    width: 120,
                    height: 120,
                  ),
                  SizedBox(height: 20),
                  Text(
                    "Welcome to True Image App!",
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 10),
                  Text(
                    "Capture, upload, and verify images with ease. Join the True Image community today!",
                    style: TextStyle(fontSize: 16, color: Colors.black54),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 40),
                  _buildSimpleButton(
                    context,
                    label: "Upload & Sign Image",
                    icon: Icons.upload_file,
                    route: '/upload',
                  ),
                  _buildSimpleButton(
                    context,
                    label: "Verify Image",
                    icon: Icons.check_circle,
                    route: '/verify',
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSimpleButton(
    BuildContext context, {
    required String label,
    required IconData icon,
    required String route,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10.0),
      child: ElevatedButton.icon(
        style: ButtonStyle(
          backgroundColor: MaterialStateProperty.all(Colors.blueAccent),
          padding: MaterialStateProperty.all(
            EdgeInsets.symmetric(vertical: 14, horizontal: 20),
          ),
          shape: MaterialStateProperty.all(
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
        icon: Icon(icon, size: 24, color: Colors.white),
        label: Text(
          label,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        onPressed: () => Navigator.pushNamed(context, route),
      ),
    );
  }
}
