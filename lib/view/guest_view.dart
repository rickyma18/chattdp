import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:chat_gpt_flutter/chat_gpt_flutter.dart';
import 'package:chatgpt/model/question_answer.dart';
import 'package:chatgpt/theme.dart';
import 'package:chatgpt/view/components/chatgpt_answer_widget.dart' as answer_widget;
import 'package:chatgpt/view/components/loading_widget.dart';
import 'package:chatgpt/view/components/text_input_widget.dart' as input_widget;
import 'package:chatgpt/view/components/user_question_widget.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter/foundation.dart' show kIsWeb, Uint8List;
import 'login.dart';

class ChatScreenGuest extends StatefulWidget {
  const ChatScreenGuest({Key? key}) : super(key: key);

  @override
  State<ChatScreenGuest> createState() => _ChatScreenGuestState();
}

class _ChatScreenGuestState extends State<ChatScreenGuest> {
  String? answer;
  final loadingNotifier = ValueNotifier<bool>(false);
  final List<QuestionAnswer> questionAnswers = [];

  late ScrollController scrollController;
  late TextEditingController inputQuestionController;

  @override
  void initState() {
    super.initState();
    inputQuestionController = TextEditingController();
    scrollController = ScrollController();
  }

  @override
  void dispose() {
    inputQuestionController.dispose();
    loadingNotifier.dispose();
    scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBg500Color,
      appBar: AppBar(
        elevation: 1,
        shadowColor: Colors.white12,
        centerTitle: false,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: kWhiteColor),
          onPressed: () {
            Navigator.of(context).push(
              MaterialPageRoute(builder: (context) => const LoginPage()),
            );
          },
        ),
        title: Text(
          "ChatTDP Invitado",
          style: kWhiteText.copyWith(
            fontSize: 20,
            fontWeight: kSemiBold,
          ),
        ),
        backgroundColor: kBg300Color,
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(child: buildChatList()),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: input_widget.TextInputWidget(
                textController: inputQuestionController,
                onSubmitted: _showLoginPrompt,
                onImagePicked: (image) => _showLoginPrompt(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Expanded buildChatList() {
    return Expanded(
      child: ListView.separated(
        controller: scrollController,
        separatorBuilder: (context, index) => const SizedBox(height: 12),
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
        itemCount: questionAnswers.length,
        itemBuilder: (BuildContext context, int index) {
          final question = questionAnswers[index].question;
          final answer = questionAnswers[index].answer;
          final image = questionAnswers[index].image;

          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              UserQuestionWidget(
                question: question,
                imageBytes: image,
              ),
              const SizedBox(height: 16),
              answer_widget.ChatGptAnswerWidget(
                answer: answer.toString().trim(),
              ),
            ],
          );
        },
      ),
    );
  }

  void _showLoginPrompt() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: kBg300Color,
          title: Text(
            "Iniciar sesión o registrarse",
            style: kWhiteText.copyWith(fontWeight: kSemiBold),
          ),
          content: Text(
            "Debes iniciar sesión o registrarte para enviar mensajes.",
            style: kWhiteText,
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: Text(
                "Cancelar",
                style: kWhiteText.copyWith(fontWeight: kMedium),
              ),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: kPrimaryColor,
              ),
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (context) => const LoginPage()),
                );
              },
              child: Text(
                "Iniciar sesión",
                style: kWhiteText.copyWith(fontWeight: kMedium),
              ),
            ),
          ],
        );
      },
    );
  }
}
