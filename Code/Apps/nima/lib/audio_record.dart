import 'dart:async';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';

/// A simple audio recorder service using the `record` package
class AudioRecorderService {
  final Record _recorder = Record();
  bool _isRecording = false;
  String? _recordedFilePath;

  /// Initialize the recorder and request microphone permission
  Future<void> init() async {
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      throw RecordingPermissionException('Microphone permission not granted');
    }
  }

  /// Toggle recording: start if stopped, stop if recording.
  ///
  /// Returns the file path of the recorded file when stopped, or null when started.
  Future<String?> toggleRecording() async {
    if (!_isRecording) {
      final dir = await getTemporaryDirectory();
      _recordedFilePath = '${dir.path}/recording.m4a';
      await _recorder.start(
        path: _recordedFilePath,
        encoder: AudioEncoder.AAC,
        bitRate: 128000,
        samplingRate: 44100,
      );
      _isRecording = true;
      return null;
    } else {
      await _recorder.stop();
      _isRecording = false;
      return _recordedFilePath;
    }
  }

  /// Dispose resources if needed
  Future<void> dispose() async {
    // No explicit dispose needed for `record` package
  }
}
