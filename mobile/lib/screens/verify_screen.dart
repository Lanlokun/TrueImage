import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:intl/intl.dart';

class VerifyScreen extends StatefulWidget {
  const VerifyScreen({super.key});

  @override
  _VerifyScreenState createState() => _VerifyScreenState();
}

class _VerifyScreenState extends State<VerifyScreen> {
  File? _image;
  String verificationResult = "";
  String uploaderPhoneNumber = "";
  String imageUploadTimestamp = "";

  // Function to format the timestamp
  String formatTimestamp(String timestamp) {
    try {
      final dateTime = DateTime.parse(timestamp);
      final formatter = DateFormat('dd MMM yyyy, hh:mm a');
      return formatter.format(dateTime);
    } catch (e) {
      return "Invalid timestamp";
    }
  }

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
          if (response["verified"]) {
            verificationResult =
                "✅ The image is authentic and has not been modified.";
          } else {
            // Handle verification failure
            verificationResult = "❌ The image has been tampered with!";
          }

          // Set uploader information
          if (response["uploader"] != null) {
            uploaderPhoneNumber =
                response["uploader"]["phone_number"] ?? "Unknown";
          }

          // Set image metadata
          if (response["image_metadata"] != null) {
            imageUploadTimestamp = formatTimestamp(
              response["image_metadata"]["uploaded_at"] ?? "Unknown",
            );
          }
        });
      } else if (response["error"] != null) {
        // Handle specific error messages from backend
        setState(() {
          verificationResult = "❌ ${response["error"]}";
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
            // Image picker display
            _image == null
                ? Text("No image selected")
                : Image.file(_image!, height: 200),
            SizedBox(height: 20),
            ElevatedButton(onPressed: pickImage, child: Text("Pick Image")),
            SizedBox(height: 10),
            ElevatedButton(onPressed: verifyImage, child: Text("Verify Image")),
            SizedBox(height: 20),

            // Only show verification result when it's available
            if (verificationResult.isNotEmpty) ...[
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color:
                      verificationResult.contains("✅")
                          ? Colors.green[100]
                          : Colors.red[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  verificationResult,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color:
                        verificationResult.contains("✅")
                            ? Colors.green[800]
                            : Colors.red[800],
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              SizedBox(height: 20),
            ],

            // Display image details only if available
            if (uploaderPhoneNumber.isNotEmpty ||
                imageUploadTimestamp.isNotEmpty) ...[
              Text(
                "Image Details:",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              SizedBox(height: 10),
              Text(
                "Image Owner Phone:",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Colors.black54,
                ),
              ),
              SizedBox(height: 5),
              Text(
                uploaderPhoneNumber,
                style: TextStyle(fontSize: 16, color: Colors.black87),
              ),
              SizedBox(height: 10),
              Text(
                "Captured On:",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Colors.black54,
                ),
              ),
              SizedBox(height: 5),
              Text(
                imageUploadTimestamp,
                style: TextStyle(fontSize: 16, color: Colors.black87),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
