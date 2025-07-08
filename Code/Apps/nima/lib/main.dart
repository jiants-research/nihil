// main.dart
import 'dart:async';
import 'package:flutter/material.dart';
import 'services.dart';
//import 'audio_record.dart';

void main() => runApp(const TranslationApp());

class TranslationApp extends StatelessWidget {
  const TranslationApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Traduction Demo',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.teal,
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF0FFF6),
        fontFamily: 'Amazing Grotesk'  // youthful grotesk font,
      ),
      home: const TranslationPage(),
    );
  }
}

class TranslationPage extends StatefulWidget {
  const TranslationPage({super.key});
  @override
  State<TranslationPage> createState() => _TranslationPageState();
}

class _TranslationPageState extends State<TranslationPage> {
  final Map<String, String> langs = {
    'bas': 'Bassa',
    'fr':  'Français',
    'en':  'English',
  };
  final Map<String, String> flags = {
    'bas': '🇨🇲',
    'fr':  '🇫🇷',
    'en':  '🇬🇧',
  };

  String _sourceLang = 'fr';
  String _targetLang = 'bas';
  bool _starred = false;
  final TextEditingController _sourceCtrl = TextEditingController(
    text: "On ne jette des pierres qu'à l'arbre chargé de fruits."
  );
  String _translatedText = '—';
  Timer? _debounce;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      extendBody: true,
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        toolbarHeight: 0,
      ),
      body: Stack(
        children: [
          // Header curve
          ClipPath(
            clipper: HeaderClipper(),
            child: Container(
              height: 240,
              color: scheme.primary,
            ),
          ),
          SafeArea(
            child: Column(
              children: [
                const SizedBox(height: 16),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Traduction',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: scheme.onPrimary,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                // Input Card
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 40),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF0FFF6),
                      borderRadius: BorderRadius.circular(30),
                      border: Border.all(
                        color: scheme.outline.withOpacity(0.3),
                        width: 0.5,
                      ),
                      boxShadow: const [
                        BoxShadow(
                          color: Colors.black12,
                          blurRadius: 8,
                          offset: Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // Language on left, icons on right
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            // dropdown with flag
                            DropdownButton<String>(
                              value: _sourceLang,
                              underline: const SizedBox(),
                              items: langs.entries.map((e) {
                                return DropdownMenuItem(
                                  value: e.key,
                                  child: Row(
                                    children: [
                                      Text(flags[e.key]!),
                                      const SizedBox(width: 4),
                                      Text(e.value),
                                    ],
                                  ),
                                );
                              }).toList(),
                              onChanged: (v) => setState(() => _sourceLang = v!),
                            ),
                            Row(
                              children: [
                                IconButton(
                                  icon: Icon(Icons.mic, color: scheme.primary),
                                  iconSize: 20,
                                  padding: EdgeInsets.zero,
                                  onPressed: _simulateStt,
                                ),
                                IconButton(
                                  icon: const Icon(Icons.translate),
                                  iconSize: 20,
                                  padding: EdgeInsets.zero,
                                  color: scheme.primary.withOpacity(0.6),
                                  onPressed: _doTranslate,
                                ),
                                IconButton(
                                  icon: const Icon(Icons.close),
                                  iconSize: 20,
                                  padding: EdgeInsets.zero,
                                  onPressed: () => _sourceCtrl.clear(),
                                ),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        TextField(
                          controller: _sourceCtrl,
                          minLines: 3,
                          maxLines: 6,
                          style: TextStyle(color: scheme.onBackground, fontSize: 16),
                          onChanged: _onSourceChanged,
                          decoration: InputDecoration(
                            isDense: true,
                            contentPadding: EdgeInsets.zero,
                            border: InputBorder.none,
                            hintText: 'Entrez le texte...',
                            hintStyle: TextStyle(color: scheme.onBackground.withOpacity(0.5)),
                          ),
                        ),
                        // Bottom-right speak button
                        Align(
                          alignment: Alignment.bottomRight,
                          child: IconButton(
                            icon: Icon(Icons.volume_up, color: scheme.primary),
                            iconSize: 24,
                            padding: EdgeInsets.zero,
                            onPressed: () => _simulateTts(_sourceCtrl.text, _sourceLang),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                // Output Card
                Expanded(
                  child: Transform.translate(
                    offset: const Offset(0, -20),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(30),
                          border: Border.all(
                            color: scheme.outline.withOpacity(0.3),
                            width: 0.5,
                          ),
                          boxShadow: const [
                            BoxShadow(
                              color: Colors.black12,
                              blurRadius: 8,
                              offset: Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                DropdownButton<String>(
                                  value: _targetLang,
                                  underline: const SizedBox(),
                                  items: langs.entries.map((e) {
                                    return DropdownMenuItem(
                                      value: e.key,
                                      child: Row(
                                        children: [
                                          Text(flags[e.key]!),
                                          const SizedBox(width: 4),
                                          Text(e.value),
                                        ],
                                      ),
                                    );
                                  }).toList(),
                                  onChanged: (v) {
                                    setState(() => _targetLang = v!);
                                    _doTranslate();
                                  },
                                ),
                                IconButton(
                                  icon: Icon(Icons.volume_up, color: scheme.primary),
                                  iconSize: 20,
                                  padding: EdgeInsets.zero,
                                  onPressed: () => _simulateTts(_translatedText, _targetLang),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Expanded(
                              child: Center(
                                child: Text(
                                  _translatedText,
                                  textAlign: TextAlign.center,
                                  style: TextStyle(color: scheme.onBackground, fontSize: 16),
                                ),
                              ),
                            ),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                IconButton(
                                  icon: Icon(
                                    _starred ? Icons.star : Icons.star_border,
                                    color: _starred ? Colors.amber : scheme.onSurface,
                                  ),
                                  iconSize: 24,
                                  padding: EdgeInsets.zero,
                                  onPressed: () => setState(() => _starred = !_starred),
                                ),
                                const SizedBox(width: 8),
                                IconButton(
                                  icon: const Icon(Icons.share),
                                  iconSize: 20,
                                  padding: EdgeInsets.zero,
                                  onPressed: () {},
                                ),
                                const SizedBox(width: 8),
                                IconButton(
                                  icon: const Icon(Icons.copy_outlined),
                                  iconSize: 20,
                                  padding: EdgeInsets.zero,
                                  onPressed: () => _copyToClipboard(_translatedText),
                                ),
                                const SizedBox(width: 8),
                                IconButton(
                                  icon: const Icon(Icons.more_vert),
                                  iconSize: 20,
                                  padding: EdgeInsets.zero,
                                  onPressed: () {},
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      // Bottom navigation
      bottomNavigationBar: BottomAppBar(
        color: Colors.white.withOpacity(0.4),
        elevation: 4,
        shape: const CircularNotchedRectangle(),
        notchMargin: 6,
        child: SizedBox(
          height: 30,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              IconButton(
                icon: Icon(Icons.translate, color: scheme.onSurface.withOpacity(0.4)),
                onPressed: () {},
                splashRadius: 20,
              ),
              IconButton(
                icon: Icon(Icons.chat, color: scheme.onSurface.withOpacity(0.4)),
                onPressed: () {},
                splashRadius: 20,
              ),
              const SizedBox(width: 48),
              IconButton(
                icon: Icon(Icons.group, color: scheme.onSurface.withOpacity(0.4)),
                onPressed: () {},
                splashRadius: 20,
              ),
              IconButton(
                icon: Icon(Icons.book, color: scheme.onSurface.withOpacity(0.4)),
                onPressed: () {},
                splashRadius: 20,
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: PhysicalModel(
        color: Colors.transparent,
        shadowColor: Colors.white,
        elevation: 8,
        shape: BoxShape.circle,
        child: FloatingActionButton(
          onPressed: _doTranslate,
          backgroundColor: Colors.greenAccent.withOpacity(0.2),
          elevation: 0,
          child: Icon(Icons.mic, color: Colors.white),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }

  void _onSourceChanged(String text) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 800), _doTranslate);
  }

  void _doTranslate() async {
    final input = _sourceCtrl.text.trim();
    String translation = await ApiService().translate(input, _targetLang);
    setState(() {
      _translatedText = translation.isEmpty ? '' : '$translation';
    });
  }

  void _simulateTts(String text, String lang) {

    if (lang!='bas'){
        ApiService().playTts(text, lang);
    } else {
      ScaffoldMessenger.of(context)
      .showSnackBar(SnackBar(content: Text('Le Text To Speech en Basaa n\'est pas encore disponible')));
    }
    
    
  }

  void _simulateStt() {
    const fakeSpeech = 'Ceci est un texte simulé.';
    setState(() {
      _sourceCtrl.text = fakeSpeech;
    });
    ScaffoldMessenger.of(context)
      .showSnackBar(const SnackBar(content: Text('STT simulated')));
  }

  void _copyToClipboard(String text) {
    ScaffoldMessenger.of(context)
      .showSnackBar(const SnackBar(content: Text('Copied')));
  }
}

class HeaderClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final path = Path();
    path.lineTo(0, size.height - 60);
    path.quadraticBezierTo(
      size.width * 0.5, size.height,
      size.width, size.height - 60,
    );
    path.lineTo(size.width, 0);
    path.close();
    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) => false;
}
