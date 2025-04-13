import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  _UploadScreenState createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  File? _image;
  bool _isUploading = false;

  // Pick an image from the gallery
  Future pickImage() async {
    final pickedFile = await ImagePicker().pickImage(
      source: ImageSource.gallery,
    );
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
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

  void uploadImage() async {
    if (_image == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Please select an image first")));
      return;
    }

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
    });

    if (response != null) {
      if (response.containsKey('error')) {
        final errorMsg = response['error'];
        final statusCode =
            response['statusCode']; // Assume your ApiService returns this

        String userFriendlyMsg;

        if (statusCode == 409) {
          userFriendlyMsg =
              "This image or a similar one already exists on the server.";
        } else if (errorMsg.toString().toLowerCase().contains('unauthorized') ||
            errorMsg.toString().toLowerCase().contains('token expired') ||
            errorMsg.toString().toLowerCase().contains('invalid token')) {
          userFriendlyMsg = "Session expired. Please log in again.";
          await clearAuthToken();
          Navigator.pushReplacementNamed(context, '/login');
          return;
        } else {
          userFriendlyMsg = "Upload failed: $errorMsg";
        }

        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(userFriendlyMsg)));
      } else {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text("Image uploaded successfully")));
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Upload failed: No response from server")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Upload & Sign Image")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _image == null
                ? Text("No image selected")
                : Image.file(_image!, height: 200),
            SizedBox(height: 20),
            ElevatedButton(onPressed: pickImage, child: Text("Pick Image")),
            SizedBox(height: 20),
            _image == null || _isUploading
                ? Container() // Hide the button if no image is selected or during upload
                : ElevatedButton(
                  onPressed: uploadImage,
                  child: Text("Upload Image"),
                ),
            // Display loading indicator when uploading
            if (_isUploading) CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}
