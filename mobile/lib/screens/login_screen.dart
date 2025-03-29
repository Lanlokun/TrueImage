import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController phoneController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  bool isLoading = false;
  final _formKey = GlobalKey<FormState>(); // Form key for validation

  // Login function
  void loginUser() async {
    // Validate inputs
    if (!_formKey.currentState!.validate()) {
      return; // If form is invalid, stop the login process
    }

    setState(() {
      isLoading = true;
    });

    try {
      var response = await ApiService.loginUser(
        phoneController.text,
        passwordController.text,
      );

      setState(() {
        isLoading = false;
      });

      if (response != null && response.containsKey('token')) {
        // Store JWT token
        String token = response['token'];
        await ApiService.storeToken(token);

        // Navigate to the home screen
        Navigator.pushNamed(context, '/home');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(response?['error'] ?? "Login failed")),
        );
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("An error occurred: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          "Login",
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
            fontFamily: 'Roboto', // You can use your custom font here
          ),
        ),
        centerTitle: true, // Center the title
        backgroundColor:
            Colors.transparent, // Make background transparent to show gradient
        elevation: 0, // Remove default shadow
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.blue, // Start color
                Colors.purple, // End color
              ],
            ),
          ),
        ),
      ),
      body: Padding(
        padding: EdgeInsets.symmetric(horizontal: 32.0),
        child: SingleChildScrollView(
          // Wrap content in SingleChildScrollView
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo at the top
              Image.asset(
                'assets/images/logo.png', // Ensure your logo is in the assets folder
                height: 120,
                width: 120,
              ),
              SizedBox(height: 20),

              // Heading
              Text(
                "Welcome Back!",
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.black,
                ),
              ),
              SizedBox(height: 20),

              // Form with validation
              Form(
                key: _formKey, // Associate the form key
                child: Column(
                  children: [
                    // Phone number input field with validation
                    TextFormField(
                      controller: phoneController,
                      decoration: InputDecoration(
                        labelText: "Phone Number",
                        prefixIcon: Icon(Icons.phone),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.grey[200],
                      ),
                      keyboardType: TextInputType.phone,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your phone number';
                        }
                        return null;
                      },
                    ),
                    SizedBox(height: 16),

                    // Password input field with validation
                    TextFormField(
                      controller: passwordController,
                      decoration: InputDecoration(
                        labelText: "Password",
                        prefixIcon: Icon(Icons.lock),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: Colors.grey[200],
                      ),
                      obscureText: true,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        return null;
                      },
                    ),
                    SizedBox(height: 20),

                    // Loading button or normal button
                    isLoading
                        ? CircularProgressIndicator()
                        : Padding(
                          padding: const EdgeInsets.symmetric(
                            vertical: 16.0,
                          ), // Vertical padding around the button
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  Colors.blue, // Set the background color
                              padding: EdgeInsets.symmetric(
                                vertical: 18,
                                horizontal: 40,
                              ), // Padding inside the button (vertical and horizontal)
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              minimumSize: Size(
                                double.infinity,
                                50,
                              ), // Make the button width take up all available space
                            ),
                            onPressed: loginUser,
                            child: Text(
                              "Login",
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ),
                    SizedBox(height: 20),

                    // Register option
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text("Don't have an account?"),
                        TextButton(
                          onPressed: () {
                            Navigator.pushNamed(context, '/register');
                          },
                          child: Text(
                            "Register",
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.blue,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              SizedBox(height: 20), // Add space between the form and the footer
              // Footer
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: Column(
                  children: [
                    Text(
                      "By logging in, you agree to our",
                      style: TextStyle(fontSize: 14, color: Colors.grey),
                    ),
                    TextButton(
                      onPressed: () {
                        // Navigate to Terms and Conditions screen
                      },
                      child: Text(
                        "Terms and Conditions",
                        style: TextStyle(
                          color: Colors.blue,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
