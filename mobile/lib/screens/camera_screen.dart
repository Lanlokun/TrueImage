import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart'; // Assuming you have this for your upload logic
import 'package:shared_preferences/shared_preferences.dart';

class CameraScreen extends StatefulWidget {
  @override
  _CameraScreenState createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  File? _image; // Variable to store the selected image
  bool _isUploading = false;

  // Method to pick an image from the camera
  Future<void> _pickImage() async {
    final ImagePicker _picker = ImagePicker();

    // Pick an image from the camera
    final XFile? image = await _picker.pickImage(source: ImageSource.camera);

    // If an image is selected, update the state
    if (image != null) {
      setState(() {
        _image = File(image.path); // Store the image as a File
      });
    }
  }

  // Get the JWT token from storage
  Future<String?> getAuthToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString('jwt_token'); // Fetch token from SharedPreferences
  }

  // Clear the JWT token from storage
  Future<void> clearAuthToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
  }

  // Upload the image to the server
  void uploadImage() async {
    if (_image == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Please select an image first")));
      return;
    }

    // Check if the user is authenticated
    String? token = await getAuthToken();
    if (token == null) {
      // If no token, show an error and navigate to login
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("You must log in first")));
      Navigator.pushReplacementNamed(context, '/login');
      return;
    }

    setState(() {
      _isUploading = true;
    });

    var response = await ApiService.uploadImage(
      _image!,
      token,
    ); // Send token with the image upload request
    setState(() {
      _isUploading = false;
    });

    if (response != null) {
      if (response.containsKey('error')) {
        // If the server response contains an error (e.g., invalid token), handle it
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Upload failed: ${response['error']}")),
        );
        // Clear the token and navigate to login if needed
        await clearAuthToken();
        Navigator.pushReplacementNamed(context, '/login');
      } else {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text("Image uploaded successfully")));
      }
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Upload failed")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Camera Screen')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            // Display the selected image, if any
            _image == null
                ? Text('No image selected.')
                : Image.file(
                  _image!,
                  width: 300,
                  height: 300,
                  fit: BoxFit.cover,
                ),

            SizedBox(height: 20),

            // Button to launch the camera
            ElevatedButton(onPressed: _pickImage, child: Text('Take a Photo')),

            SizedBox(height: 20),

            // Upload button to upload the image to the server
            _image == null || _isUploading
                ? Container() // Hide the button if no image is selected or during upload
                : ElevatedButton(
                  onPressed: uploadImage,
                  child: Text('Upload Image'),
                ),

            // Display loading indicator when uploading
            if (_isUploading) CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}
