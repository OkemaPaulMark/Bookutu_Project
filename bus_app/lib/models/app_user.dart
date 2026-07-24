class AppUser {
  final String id;
  final String email;
  final String? username;
  final String? firstName;
  final String? lastName;
  final String? phoneNumber;
  final String userType;

  AppUser({
    required this.id,
    required this.email,
    this.username,
    this.firstName,
    this.lastName,
    this.phoneNumber,
    required this.userType,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'].toString(),
      email: json['email']?.toString() ?? '',
      username: json['username']?.toString(),
      firstName: json['firstName']?.toString(),
      lastName: json['lastName']?.toString(),
      phoneNumber: json['phoneNumber']?.toString(),
      userType: json['userType']?.toString() ?? 'PASSENGER',
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'username': username,
        'firstName': firstName,
        'lastName': lastName,
        'phoneNumber': phoneNumber,
        'userType': userType,
      };
}
