class Advert {
  final String id;
  final String title;
  final String description;
  final String imageUrl;
  final String? linkUrl;

  Advert({
    required this.id,
    required this.title,
    required this.description,
    required this.imageUrl,
    this.linkUrl,
  });

  factory Advert.fromJson(Map<String, dynamic> json) {
    return Advert(
      id: json['id'].toString(),
      title: json['title']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      imageUrl: json['imageUrl']?.toString() ?? '',
      linkUrl: json['linkUrl']?.toString(),
    );
  }
}
