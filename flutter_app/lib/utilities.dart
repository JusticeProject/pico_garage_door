import 'package:flutter/foundation.dart';
import 'dart:io';
import 'package:pointycastle/export.dart';
// see https://pub.dev/packages/pointycastle

//*************************************************************************************************

const keyBytes = [7,139,240,55,27,148,191,122,61,250,38,68,162,7,14,0,129,126,131,150,229,46,106,25,39,159,13,63,169,187,0,104,];

//*************************************************************************************************

void logDebugMsg(String msg)
{
  if (kDebugMode)
  {
    print(msg);
  }
}

//*************************************************************************************************

Future<String> lookupHostname(String hostname) async
{
  try
  {
    List<InternetAddress> addrs = await InternetAddress.lookup(hostname, type: InternetAddressType.IPv4);
    return addrs.first.address;
  }
  on Exception catch (e)
  {
    logDebugMsg(e.toString());
    return "";
  }
}

//*************************************************************************************************

// from https://api.dart.dev/dart-io/RawDatagramSocket-class.html
Future<void> sendCmd(String addr) async
{
  final Uint8List key = Uint8List.fromList(keyBytes);
  const int port = 17812;

  final clientSocket = await RawDatagramSocket.bind(InternetAddress.anyIPv4, 0);
  final timedSocket = clientSocket.timeout(Duration(seconds: 3), onTimeout: (sink) {
    logDebugMsg("timeout");
    //sink.close(); // this will close the socket, and onDone will be called

    // add another read event that the clientSocket can see, although there won't be any data to go with it
    sink.add(RawSocketEvent.read);
  });
  
  // send the initial Knock packet
  List<int> asciiValues = "KnockKnock".codeUnits;
  Uint8List knockPacket = Uint8List.fromList(asciiValues);
  int bytesWritten = clientSocket.send(knockPacket, InternetAddress(addr), port);
  logDebugMsg("wrote $bytesWritten bytes");

  //*********************************************

  // setup the callback for when data arrives
  void onData(RawSocketEvent event)
  {
    logDebugMsg("onData");
    switch (event)
    {
      case RawSocketEvent.read:
        final datagram = clientSocket.receive();
        if (datagram == null)
        {
          logDebugMsg("read event: no data");
        }
        else
        {
          logDebugMsg("read event: ${datagram.data.length} bytes");
          Uint8List cipherText = datagram.data;
          Uint8List plainText = decryptFromPicoW(key, cipherText);
          Uint8List newPlainText = manipulateBytes(plainText);
          Uint8List newCipherText = encryptToPicoW(key, newPlainText);
          int bytesWritten = clientSocket.send(newCipherText, InternetAddress(addr), port);
          logDebugMsg("wrote $bytesWritten bytes");
        }
        clientSocket.close();
        break;
      case RawSocketEvent.write:
        logDebugMsg("write event");
        break;
      case RawSocketEvent.closed:
        logDebugMsg("closed event");
        break;
      default:
        logDebugMsg("unexpected event $event");
    }
  }

  //*********************************************

  // register the callback created above and wait for the data
  // from https://stackoverflow.com/questions/68527608/dart-socket-listen-doesnt-wait-until-done
  var subscription = timedSocket.listen(onData);
  await subscription.asFuture<void>();
  logDebugMsg("done listening");
}

//*************************************************************************************************

Uint8List decryptFromPicoW(Uint8List key, Uint8List cipherText)
{
  var decrypter = ECBBlockCipher(AESEngine());
  decrypter.init(false, KeyParameter(key));
  Uint8List plainText = Uint8List(cipherText.length); // allocate space

  var offset = 0;
  while (offset < cipherText.length)
  {
    offset += decrypter.processBlock(cipherText, offset, plainText, offset);
  }

  return plainText;
}

//*************************************************************************************************

Uint8List manipulateBytes(Uint8List input)
{
  //Uint8List output = Uint8List(input.length);
  for (int i = 0; i < input.length; i++)
  {
    int number = input[i] + i + 1;
    if (number > 255)
    {
      number -= 255;
    }
    input[i] = number;
  }
  return input;
}

//*************************************************************************************************

Uint8List encryptToPicoW(Uint8List key, Uint8List plainText)
{
  var encrypter = ECBBlockCipher(AESEngine());
  encrypter.init(true, KeyParameter(key));
  Uint8List cipherText = Uint8List(plainText.length); // allocate space

  var offset = 0;
  while (offset < plainText.length)
  {
    offset += encrypter.processBlock(plainText, offset, cipherText, offset);
  }

  return cipherText;
}
