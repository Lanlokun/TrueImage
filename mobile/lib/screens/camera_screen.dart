import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  _CameraScreenState createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  File? _image;
  bool _isUploading = false;
  bool _isSigned = false;
  final ImagePicker _picker = ImagePicker();

  // Capture image from the camera and sign it automatically
  Future<void> _captureAndSignImage() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.camera);
      if (image != null) {
        setState(() {
          _image = File(image.path);
          _isSigned = false;
        });

        await _signImage(); // Automatically sign the image
      }
    } catch (e) {
      print("Error capturing image: $e");
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Error capturing image: $e")));
    }
  }

  // Get the JWT token from storage
  Future<String?> getAuthToken() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString('jwt_token');
  }

  // Sign the image before uploading
  Future<void> _signImage() async {
    if (_image == null) return;

    String? token = await getAuthToken();
    if (token == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("You must log in first")));
      Navigator.pushReplacementNamed(context, '/login');
      return;
    }

    setState(() {
      _isUploading = true;
    });

    var response = await ApiService.uploadImage(_image!, token);

    setState(() {
      _isUploading = false;
      _isSigned =
          response != null &&
          response.containsKey("message"); // ✅ Adjusted check
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _isSigned ? "Image successfully signed" : "Image signing failed",
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            _image == null
                ? Text(
                  'No image captured.',
                  style: TextStyle(fontSize: 18, color: Colors.black54),
                )
                : Stack(
                  alignment: Alignment.center,
                  children: [
                    Image.file(
                      _image!,
                      width: 300,
                      height: 300,
                      fit: BoxFit.cover,
                    ),
                    if (_isSigned)
                      Positioned(
                        bottom: 10,
                        right: 10,
                        child: Icon(
                          Icons.verified,
                          color: Colors.green,
                          size: 40,
                        ),
                      )
                    else if (!_isUploading)
                      Positioned(
                        bottom: 10,
                        right: 10,
                        child: Icon(Icons.warning, color: Colors.red, size: 40),
                      ),
                  ],
                ),

            SizedBox(height: 20),

            // Simplified Capture Photo Button
            TextButton.icon(
              onPressed: _captureAndSignImage,
              icon: Icon(Icons.camera_alt, color: Colors.blueAccent),
              label: Text(
                'Capture Photo',
                style: TextStyle(color: Colors.blueAccent, fontSize: 16),
              ),
            ),

            // Show Loading Indicator while signing
            if (_isUploading)
              Padding(
                padding: EdgeInsets.all(10),
                child: CircularProgressIndicator(),
              ),
          ],
        ),
      ),
    );
  }
}
