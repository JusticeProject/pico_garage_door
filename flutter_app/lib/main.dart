import 'package:flutter/material.dart';
import 'utilities.dart' as utilities;

//*************************************************************************************************

void main() {
  runApp(const MyApp());
}

//*************************************************************************************************

class MyApp extends StatelessWidget
{
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context)
  {
    return MaterialApp(
      title: 'Garage Door Opener',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.greenAccent),
      ),
      home: const MyHomePage(title: 'Pico Garage Door Opener'),
    );
  }
}

//*************************************************************************************************
//*************************************************************************************************
//*************************************************************************************************

class MyHomePage extends StatefulWidget
{
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

//*************************************************************************************************
//*************************************************************************************************
//*************************************************************************************************

class _MyHomePageState extends State<MyHomePage>
{
  final _textController = TextEditingController();
  bool _buttonsEnabled = true;

  //*********************************************

  @override
  void dispose()
  {
    _textController.dispose();
    super.dispose();
  }

  //*********************************************

  void _onOpenPressed() async
  {
    setState((){
      _buttonsEnabled = false;
    });

    String addr = _textController.text;
    await utilities.sendCmd(addr, onOpenDone).catchError((err) 
      {
        // TODO: need to notify user, probably bad IP address
        print("caught error: $err");
        onOpenDone();
      });
  }

  //*********************************************

  void onOpenDone()
  {
    setState((){
      _buttonsEnabled = true;
    });
  }

  //*********************************************

  void _onScanPressed() async
  {
    setState((){
      _buttonsEnabled = false;
      _textController.clear();
    });

    String addr = await utilities.lookupHostname("picow.local");
    if (addr.isEmpty)
    {
      addr = "Not found";
    }

    print("Found addr = $addr");
    // TODO: do I need to put setState() around this? It seems to work without it.
    // This call to setState tells the Flutter framework that something has
    // changed in this State, which causes it to rerun the build method below
    // so that the display can reflect the updated values. If we changed
    // the variable without calling setState(), then the build method would not be
    // called again, and so nothing would appear to happen.
    setState(() {
      _buttonsEnabled = true;
      _textController.text = addr;
    });
  }

  //*********************************************

  @override
  Widget build(BuildContext context)
  {
    final theme = Theme.of(context);
    // a color that's legible when drawn on primary color (green):
    final filledStyle = theme.textTheme.headlineMedium!.copyWith(color: theme.colorScheme.onPrimary);
    // the primary color:
    final elevatedStyle = theme.textTheme.headlineMedium!.copyWith(color: theme.colorScheme.primary);
    
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SizedBox(height: 75, 
              child: FilledButton(onPressed: _buttonsEnabled ? _onOpenPressed : null, child: Text("Open / Close Door", style: filledStyle))),
            SizedBox(height: 40),
            SizedBox(width: 200,
              child: TextField(controller: _textController, decoration: InputDecoration(border: OutlineInputBorder(), labelText: "IP Address"),
              ),
            ),
            SizedBox(height: 50),
            SizedBox(height: 60, 
              child: ElevatedButton(onPressed: _buttonsEnabled ? _onScanPressed : null, child: Text("Scan for PicoW", style: elevatedStyle)))
          ],
        ),
      ),
    );
  }
}
