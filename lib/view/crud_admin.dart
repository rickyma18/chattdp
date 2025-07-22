import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme.dart';

class CrudAdminPage extends StatefulWidget {
  const CrudAdminPage({Key? key}) : super(key: key);

  @override
  State<CrudAdminPage> createState() => _CrudAdminPageState();
}

class _CrudAdminPageState extends State<CrudAdminPage> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _roleController = TextEditingController();
  final TextEditingController _incidentCountController = TextEditingController();
  String? _currentEditingId;

  @override
  void dispose() {
    _emailController.dispose();
    _roleController.dispose();
    _incidentCountController.dispose();
    super.dispose();
  }

  void _addOrEditUser() {
    if (_emailController.text.isEmpty || _roleController.text.isEmpty || _incidentCountController.text.isEmpty) {
      _showError('Los campos de email, rol e incidentes restantes no pueden estar vacíos.');
      return;
    }

    if (_currentEditingId == null) {
      // Adding a new user
      FirebaseFirestore.instance.collection('users').add({
        'email': _emailController.text,
        'role': _roleController.text,
        'emailVerified': false,
        'incidentCount': int.tryParse(_incidentCountController.text) ?? 0,
        'maxIncidents': 50,
        'sessionToken': '',
      }).then((value) {
        _clearFields();
      }).catchError((error) {
        _showError('Error al añadir usuario: $error');
      });
    } else {
      // Editing an existing user
      FirebaseFirestore.instance.collection('users').doc(_currentEditingId).update({
        'email': _emailController.text,
        'role': _roleController.text,
        'incidentCount': int.tryParse(_incidentCountController.text) ?? 0,
      }).then((value) {
        _clearFields();
      }).catchError((error) {
        _showError('Error al actualizar usuario: $error');
      });
    }
  }

  void _deleteUser(String documentId) {
    FirebaseFirestore.instance.collection('users').doc(documentId).delete().catchError((error) {
      _showError('Error al eliminar usuario: $error');
    });
  }

  void _clearFields() {
    _emailController.clear();
    _roleController.clear();
    _incidentCountController.clear();
    setState(() {
      _currentEditingId = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'CRUD Admin Page',
          style: kWhiteText.copyWith(fontSize: 20, fontWeight: kSemiBold),
        ),
        backgroundColor: kBg300Color,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                labelStyle: kWhiteText,
                filled: true,
                fillColor: kBg100Color,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide(color: kPrimaryColor),
                ),
              ),
              style: kWhiteText,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _roleController,
              decoration: InputDecoration(
                labelText: 'Role',
                labelStyle: kWhiteText,
                filled: true,
                fillColor: kBg100Color,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide(color: kPrimaryColor),
                ),
              ),
              style: kWhiteText,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _incidentCountController,
              decoration: InputDecoration(
                labelText: 'Incident Count',
                labelStyle: kWhiteText,
                filled: true,
                fillColor: kBg100Color,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide(color: kPrimaryColor),
                ),
              ),
              style: kWhiteText,
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _addOrEditUser,
              style: ElevatedButton.styleFrom(
                backgroundColor: kPrimaryColor,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                textStyle: kWhiteText.copyWith(fontWeight: kSemiBold),
              ),
              child: Text(_currentEditingId == null ? 'Add User' : 'Update User'),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: StreamBuilder<QuerySnapshot>(
                stream: FirebaseFirestore.instance.collection('users').snapshots(),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    return const Center(child: Text('Error al cargar datos'));
                  }

                  final data = snapshot.data?.docs;

                  if (data == null || data.isEmpty) {
                    return const Center(child: Text('No hay usuarios disponibles'));
                  }

                  return ListView.builder(
                    itemCount: data.length,
                    itemBuilder: (context, index) {
                      final doc = data[index];
                      return Card(
                        color: kBg100Color,
                        child: ListTile(
                          title: Text(doc['email'], style: kWhiteText),
                          subtitle: Text(
                            'Role: ${doc['role']}\nIncident Count: ${doc['incidentCount']}',
                            style: kWhiteText.copyWith(fontWeight: kRegular),
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.edit, color: kWhiteColor),
                                onPressed: () {
                                  setState(() {
                                    _emailController.text = doc['email'];
                                    _roleController.text = doc['role'];
                                    _incidentCountController.text = doc['incidentCount'].toString();
                                    _currentEditingId = doc.id;
                                  });
                                },
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete, color: kWhiteColor),
                                onPressed: () => _deleteUser(doc.id),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
      backgroundColor: kBg500Color,
    );
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
}
