import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class VerifyScreen extends StatefulWidget {
  @override
  _VerifyScreenState createState() => _VerifyScreenState();
}

class _VerifyScreenState extends State<VerifyScreen> {
  File? _image;
  String verificationResult = "";

  Future<void> pickImage() async {
    final pickedFile = await ImagePicker().pickImage(
      source: ImageSource.gallery,
    );
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        verificationResult = ""; // Reset result when picking a new image
      });
    }
  }

  Future<void> verifyImage() async {
    if (_image == null) {
      setState(() {
        verificationResult = "⚠️ Please select an image first!";
      });
      return;
    }

    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? token = prefs.getString('jwt_token');

    if (token == null) {
      setState(() {
        verificationResult = "⚠️ Authentication required. Please log in.";
      });
      return;
    }

    try {
      var response = await ApiService.verifyImage(_image!, token);

      if (response == null) {
        setState(() {
          verificationResult = "❌ No response from server.";
        });
      } else if (response["verified"] != null && response["verified"] is bool) {
        setState(() {
          verificationResult =
              response["verified"]
                  ? "✅ Image is authentic!"
                  : "❌ Image verification failed!";
        });
      } else {
        setState(() {
          verificationResult = "❌ Invalid response structure from server.";
        });
      }
    } catch (e) {
      setState(() {
        verificationResult = "❌ Error verifying image: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Verify Image")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _image == null
                ? Text("No image selected")
                : Image.file(_image!, height: 200),
            SizedBox(height: 20),
            ElevatedButton(onPressed: pickImage, child: Text("Pick Image")),
            SizedBox(height: 10),
            ElevatedButton(onPressed: verifyImage, child: Text("Verify Image")),
            SizedBox(height: 20),
            Text(
              verificationResult,
              style: TextStyle(fontSize: 18),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
