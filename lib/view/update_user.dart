import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../theme.dart';

class UpdateUserView extends StatefulWidget {
  const UpdateUserView({Key? key}) : super(key: key);
  @override
  _UpdateUserViewState createState() => _UpdateUserViewState();
}

class _UpdateUserViewState extends State<UpdateUserView> {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final _formKey = GlobalKey<FormState>();
  String? _newEmail;
  String? _newPassword;

  Future<void> _updateUser() async {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      User? user = _auth.currentUser;

      try {
        if (_newEmail != null && _newEmail!.isNotEmpty) {
          await user?.updateEmail(_newEmail!);
        }
        if (_newPassword != null && _newPassword!.isNotEmpty) {
          await user?.updatePassword(_newPassword!);
        }
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Usuario actualizado con éxito', style: kWhiteText)),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.toString()}', style: kWhiteText)),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBg500Color,
      appBar: AppBar(
        title: Text('Actualizar Usuario', style: kWhiteText),
        backgroundColor: kBg300Color,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                style: kWhiteText,
                decoration: InputDecoration(
                  labelText: 'Nuevo Correo Electrónico',
                  labelStyle: kWhiteText,
                  filled: true,
                  fillColor: kBg100Color,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.0),
                    borderSide: BorderSide.none,
                  ),
                ),
                keyboardType: TextInputType.emailAddress,
                onSaved: (value) => _newEmail = value,
                validator: (value) {
                  if (value != null && value.isNotEmpty && !value.contains('@')) {
                    return 'Por favor ingresa un correo válido';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                style: kWhiteText,
                decoration: InputDecoration(
                  labelText: 'Nueva Contraseña',
                  labelStyle: kWhiteText,
                  filled: true,
                  fillColor: kBg100Color,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.0),
                    borderSide: BorderSide.none,
                  ),
                ),
                obscureText: true,
                onSaved: (value) => _newPassword = value,
                validator: (value) {
                  if (value != null && value.isNotEmpty && value.length < 6) {
                    return 'La contraseña debe tener al menos 6 caracteres';
                  }
                  return null;
                },
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: _updateUser,
                style: ElevatedButton.styleFrom(
                  backgroundColor: kPrimaryColor,
                  padding: EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                ),
                child: Text('Actualizar Usuario', style: kWhiteText.copyWith(fontWeight: kMedium)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
