import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:mime/mime.dart';
import 'package:http_parser/http_parser.dart';
import 'package:path_provider/path_provider.dart';
import 'package:audioplayers/audioplayers.dart';

class ApiService {
  // TODO: Replace with your actual server address
  static const String _baseUrl = 'http://192.168.5.206:8000';

  final AudioPlayer _audioPlayer = AudioPlayer();

  /// Translates [text] into [targetLang] ('en', 'fr', or 'bas').
  Future<String> translate(String text, String targetLang) async {
    final uri = Uri.parse('$_baseUrl/translate/');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
        'target_language': targetLang,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['translation'] as String;
    } else {
      throw Exception('Translation failed (status: ${response.statusCode})');
    }
  }

  /// Calls the TTS endpoint with [text] and [lang] ('en' or 'fr'),
  /// saves the returned WAV to a temp file, and returns it.
  Future<File> fetchTts(String text, String lang) async {
    final uri = Uri.parse('$_baseUrl/tts/');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
        'language': lang,
      }),
    );

    if (response.statusCode == 200) {
      final tempDir = await getTemporaryDirectory();
      final file = File('${tempDir.path}/tts_output.wav');
      await file.writeAsBytes(response.bodyBytes);
      return file;
    } else {
      throw Exception('TTS request failed (status: ${response.statusCode})');
    }
  }

  /// Fetches TTS audio for [text] in [lang] and plays it directly.
  Future<void> playTts(String text, String lang) async {
    try {
      final file = await fetchTts(text, lang);
      // Use AudioPlayer to play local file
      await _audioPlayer.play(DeviceFileSource(file.path));
    } catch (e) {
      throw Exception('Playback failed: $e');
    }
  }

  /// Uploads [audioFile] with form field 'language' = [lang] to the STT endpoint,
  /// and returns the transcript.
  Future<String> stt(File audioFile, String lang) async {
    final uri = Uri.parse('$_baseUrl/stt/');
    final mimeType = lookupMimeType(audioFile.path) ?? 'application/octet-stream';
    final request = http.MultipartRequest('POST', uri)
      ..fields['language'] = lang
      ..files.add(
        await http.MultipartFile.fromPath(
          'audio_file',
          audioFile.path,
          contentType: MediaType.parse(mimeType),
        ),
      );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['transcript'] as String;
    } else {
      throw Exception('STT failed (status: ${response.statusCode})');
    }
  }

  /// Uploads [audioFile] to the transcription endpoint and returns the result.
  Future<String> transcribe(File audioFile) async {
    final uri = Uri.parse('$_baseUrl/transcribe/');
    final mimeType = lookupMimeType(audioFile.path) ?? 'application/octet-stream';
    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        await http.MultipartFile.fromPath(
          'file',
          audioFile.path,
          contentType: MediaType.parse(mimeType),
        ),
      );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['transcription'] as String;
    } else {
      throw Exception('Transcription failed (status: ${response.statusCode})');
    }
  }
}
