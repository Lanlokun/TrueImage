import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = "http://10.0.2.2:5000/";

  // Login User
  static Future<Map<String, dynamic>?> loginUser(
    String phone,
    String password,
  ) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/login"),
        body: jsonEncode({"phone": phone, "password": password}),
        headers: {"Content-Type": "application/json"},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Login failed: ${response.body}');
        return {
          'error': jsonDecode(response.body)['message'] ?? 'Login failed',
        };
      }
    } catch (e) {
      debugPrint("Network error: $e");
      return {'error': 'Network error: $e'};
    }
  }

  // Register User
  static Future<Map<String, dynamic>?> registerUser(
    String phone,
    String password,
    String nationalId,
  ) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/register"),
        body: jsonEncode({
          "phone": phone,
          "password": password,
          "national_id": nationalId,
        }),
        headers: {"Content-Type": "application/json"},
      );

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Registration failed: ${response.body}');
        return {
          'error':
              jsonDecode(response.body)['message'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      debugPrint("Network error: $e");
      return {'error': 'Network error: $e'};
    }
  }

  // Upload Image
  static Future<Map<String, dynamic>?> uploadImage(
    File image,
    String token,
  ) async {
    try {
      var request = http.MultipartRequest("POST", Uri.parse("$baseUrl/upload"));

      // Add the image file to the request
      request.files.add(await http.MultipartFile.fromPath('image', image.path));

      // Add the Authorization header with the token
      request.headers['Authorization'] = 'Bearer $token';

      var response = await request.send();

      if (response.statusCode == 200) {
        // If the response is successful, decode the JSON
        return jsonDecode(await response.stream.bytesToString());
      } else {
        debugPrint(
          "Error: Server responded with status code ${response.statusCode}",
        );
        return {'error': 'Server error: ${response.statusCode}'};
      }
    } catch (e) {
      debugPrint("Error uploading image: $e");
      return {'error': 'Network error: $e'};
    }
  }

  // Verify Image
  static Future<Map<String, dynamic>?> verifyImage(
    File image,
    String token,
  ) async {
    try {
      var request = http.MultipartRequest("POST", Uri.parse("$baseUrl/verify"));

      // Add the image file to the request
      request.files.add(await http.MultipartFile.fromPath('image', image.path));

      // Add the Authorization header with the token
      request.headers['Authorization'] = 'Bearer $token';

      var response = await request.send();

      if (response.statusCode == 200) {
        return jsonDecode(await response.stream.bytesToString());
      } else {
        debugPrint(
          "Error verifying image: Server responded with status code ${response.statusCode}",
        );
        return {'error': 'Verification failed: ${response.statusCode}'};
      }
    } catch (e) {
      debugPrint("Error verifying image: $e");
      return {'error': 'Network error: $e'};
    }
  }

  // Fetch Gallery Images
  static Future<List<String>?> fetchGallery(String token) async {
    try {
      final response = await http.get(
        Uri.parse("$baseUrl/gallery"),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['images']);
      } else {
        debugPrint('Error fetching gallery: ${response.body}');
        return null;
      }
    } catch (e) {
      debugPrint("Error fetching gallery: $e");
      return null;
    }
  }

  // Store JWT token
  static Future<void> storeToken(String token) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('jwt_token', token);
  }

  // ApiService to handle image deletion
  static Future<Map<String, dynamic>?> deleteImage(
    String token,
    String imageUrl,
  ) async {
    try {
      final response = await http.delete(
        Uri.parse("$baseUrl/deleteImage"),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({'imageUrl': imageUrl}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint("Error: ${response.statusCode}, Response: ${response.body}");
        return {'error': 'Failed to delete image'};
      }
    } catch (e) {
      debugPrint("Error deleting image: $e");
      return {'error': 'Network error: $e'};
    }
  }
}
