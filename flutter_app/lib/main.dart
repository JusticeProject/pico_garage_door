import 'package:flutter/material.dart';
import 'utilities.dart' as utilities;

//*************************************************************************************************

void main() {
  runApp(MyApp());
}

//*************************************************************************************************

class MyApp extends StatelessWidget
{
  MyApp({super.key});
  final GlobalKey<ScaffoldMessengerState> _scaffoldMessengerKey = GlobalKey<ScaffoldMessengerState>();

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context)
  {
    return MaterialApp(
      scaffoldMessengerKey: _scaffoldMessengerKey,
      title: 'Garage Door Opener',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.lightBlue),
      ),
      home: MyHomePage(title: 'Pico Garage Door Opener', scaffoldMessengerKey: _scaffoldMessengerKey),
    );
  }
}

//*************************************************************************************************
//*************************************************************************************************
//*************************************************************************************************

class MyHomePage extends StatefulWidget
{
  const MyHomePage({super.key, required this.title, required this.scaffoldMessengerKey});

  final String title;
  // this scaffold messenger key is used to show the SnackBar (toast) outside of a build function since otherwise 
  // we would need the BuildContext
  final GlobalKey<ScaffoldMessengerState> scaffoldMessengerKey;

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

  void _showMessageToUser(String msg)
  {
    // widget in this case refers to the corresponding StatefulWidget
    widget.scaffoldMessengerKey.currentState!.showSnackBar(SnackBar(content: Text(msg)));
  }

  //*********************************************

  void _onOpenPressed() async
  {
    setState((){
      _buttonsEnabled = false;
    });

    String addr = _textController.text;
    try
    {
      await utilities.sendCmd(addr);
    }
    catch (err)
    {
      _showMessageToUser(err.toString());
      utilities.logDebugMsg("caught error: $err");
    }  

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

    try
    {
      String addr = await utilities.lookupHostname("picow.local");
      utilities.logDebugMsg("Found addr = $addr");
      _textController.text = addr;
    }
    catch (err)
    {
      _showMessageToUser(err.toString());
      utilities.logDebugMsg(err.toString());
    }

    // This call to setState tells the Flutter framework that something has
    // changed in this State, which causes it to rerun the build method below
    // so that the display can reflect the updated values. If we changed
    // the variable without calling setState(), then the build method would not be
    // called again, and so nothing would appear to happen.
    setState(() {
      _buttonsEnabled = true;
    });
  }

  //*********************************************

  void _onDefaultIP()
  {
    // not sure if setState is actually needed here
    setState((){
      _textController.text = "192.168.1.160";
    });
  }

  //*********************************************

  @override
  Widget build(BuildContext context)
  {
    final theme = Theme.of(context);
    // a color that's legible when drawn on primary color (green):
    final onPrimary = theme.textTheme.headlineMedium!.copyWith(color: theme.colorScheme.onPrimary);
    // the primary color:
    final primary = theme.textTheme.headlineMedium!.copyWith(color: theme.colorScheme.primary);
    
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
            SizedBox(height: 75, child: 
              FilledButton(onPressed: _buttonsEnabled ? _onOpenPressed : null, child: 
                Text("Open / Close Door", style: onPrimary))),
            SizedBox(height: 40),
            SizedBox(width: 250, child: 
              TextField(style: primary, controller: _textController, decoration: 
                InputDecoration(border: OutlineInputBorder(), labelText: "IP Address"),
              ),
            ),
            SizedBox(height: 50),
            SizedBox(height: 60, child: 
              ElevatedButton(onPressed: _buttonsEnabled ? _onScanPressed : null, child: 
                Text("Scan for PicoW", style: _buttonsEnabled ? primary : onPrimary))),
            SizedBox(height: 30),
            SizedBox(height: 60, child: 
              ElevatedButton(onPressed: _buttonsEnabled ? _onDefaultIP : null, child:
                Text("Default IP", style: _buttonsEnabled ? primary : onPrimary)))
          ],
        ),
      ),
    );
  }
}
