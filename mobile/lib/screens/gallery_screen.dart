import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class GalleryScreen extends StatefulWidget {
  const GalleryScreen({super.key});

  @override
  _GalleryScreenState createState() => _GalleryScreenState();
}

class _GalleryScreenState extends State<GalleryScreen> {
  List<String> imageUrls = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchGalleryImages();
  }

  Future<void> _fetchGalleryImages() async {
    try {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      String? token = prefs.getString('jwt_token');

      if (token != null) {
        final data = await ApiService.fetchGallery(token);

        if (data != null) {
          setState(() {
            imageUrls = data;
            isLoading = false;
          });
        } else {
          throw Exception('Failed to load images');
        }
      } else {
        throw Exception('No token found');
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  void _showFullScreenImage(BuildContext context, String imageUrl, int index) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder:
            (context) => Scaffold(
              backgroundColor: Colors.black,
              appBar: AppBar(
                backgroundColor: Colors.transparent,
                elevation: 0,
                leading: IconButton(
                  icon: Icon(Icons.arrow_back, color: Colors.white),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
              body: Center(
                child: Hero(
                  tag: 'image_$index',
                  child: InteractiveViewer(
                    panEnabled: true,
                    minScale: 0.5,
                    maxScale: 4.0,
                    child: Image.network(imageUrl, fit: BoxFit.contain),
                  ),
                ),
              ),
            ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body:
          isLoading
              ? Center(child: CircularProgressIndicator())
              : imageUrls.isEmpty
              ? Center(
                child: Text('No images found', style: TextStyle(fontSize: 18)),
              )
              : GridView.builder(
                padding: EdgeInsets.all(8),
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 2,
                  mainAxisSpacing: 2,
                  childAspectRatio: 1,
                ),
                itemCount: imageUrls.length,
                itemBuilder: (context, index) {
                  return GestureDetector(
                    onTap:
                        () => _showFullScreenImage(
                          context,
                          imageUrls[index],
                          index,
                        ),
                    child: Hero(
                      tag: 'image_$index',
                      child: Container(
                        decoration: BoxDecoration(
                          border: Border.all(
                            color: Colors.grey.shade200,
                            width: 0.5,
                          ),
                        ),
                        child: Image.network(
                          imageUrls[index],
                          fit: BoxFit.cover,
                          loadingBuilder: (
                            BuildContext context,
                            Widget child,
                            ImageChunkEvent? loadingProgress,
                          ) {
                            if (loadingProgress == null) return child;
                            return Center(
                              child: CircularProgressIndicator(
                                value:
                                    loadingProgress.expectedTotalBytes != null
                                        ? loadingProgress
                                                .cumulativeBytesLoaded /
                                            loadingProgress.expectedTotalBytes!
                                        : null,
                              ),
                            );
                          },
                          errorBuilder:
                              (context, error, stackTrace) =>
                                  Icon(Icons.broken_image),
                        ),
                      ),
                    ),
                  );
                },
              ),
    );
  }
}
