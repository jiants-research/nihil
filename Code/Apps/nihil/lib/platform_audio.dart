import 'package:flutter/services.dart';

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
