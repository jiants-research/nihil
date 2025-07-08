// lib/services.dart

import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

const url = 'http://192.168.5.206:8000';

/// Wraps Android's MediaPlayer via a MethodChannel.
class PlatformAudio {
  static const _audio = MethodChannel('my.audio');

  /// Stream & play a WAV from the given URL.
  static Future<void> playUrl(String url) async {
    await _audio.invokeMethod('playUrl', {'url': url});
  }

  /// Stop playback.
  static Future<void> stop() async {
    await _audio.invokeMethod('stop');
  }
}

/// Your HTTP client against the FastAPI backend.
class ApiService {
  // ← replace with your server’s IP / hostname
  static const _base = url;

  /// GET /translate/?text=…&target_language=…
  Future<String> translate(String text, String target) async {
    final uri = Uri.parse('$_base/translate/?'
        'text=${Uri.encodeComponent(text)}&'
        'target_language=$target');
    final resp = await http.get(uri);
    if (resp.statusCode != 200) {
      throw Exception('Translate failed: ${resp.statusCode}');
    }
    final data = jsonDecode(resp.body);
    return data['translation'] as String;
  }

  /// Stream & play TTS in one go (no local file).
  Future<void> speak(String text, String lang) async {
    final url = '$_base/tts/?'
        'text=${Uri.encodeComponent(text)}&'
        'language=$lang';
    await PlatformAudio.playUrl(url);
  }

  /// POST multipart /stt/ with file + language
  Future<String> stt(String filePath, String lang) async {
    final uri = Uri.parse('$_base/stt/');
    final req = http.MultipartRequest('POST', uri)
      ..fields['language'] = lang
      ..files.add(await http.MultipartFile.fromPath(
        'audio_file', filePath,
      ));
    final res = await req.send();
    final body = await http.Response.fromStream(res);
    if (body.statusCode != 200) {
      throw Exception('STT failed: ${body.statusCode}');
    }
    final data = jsonDecode(body.body);
    return data['transcript'] as String;
  }

  /// POST multipart /transcribe/ with file
  Future<String> transcribe(String filePath) async {
    final uri = Uri.parse('$_base/transcribe/');
    final req = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('file', filePath));
    final res = await req.send();
    final body = await http.Response.fromStream(res);
    if (body.statusCode != 200) {
      throw Exception('Transcription failed: ${body.statusCode}');
    }
    final data = jsonDecode(body.body);
    return data['transcription'] as String;
  }
}
