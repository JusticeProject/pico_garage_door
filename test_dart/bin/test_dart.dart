import 'dart:ffi';
import 'dart:io';
import 'dart:typed_data';
import 'package:pointycastle/export.dart';
// see https://pub.dev/packages/pointycastle

//*************************************************************************************************

const keyBytes = [7,139,240,55,27,148,191,122,61,250,38,68,162,7,14,0,129,126,131,150,229,46,106,25,39,159,13,63,169,187,0,104,];

//*************************************************************************************************

void main() async
{
  Uint8List presharedKey = Uint8List.fromList(keyBytes);
  print("key length = ${presharedKey.length}");
  print(presharedKey);

  String addr = await lookupHostname("picow.local");
  print("found address for PicoW: $addr");
  if (addr.isEmpty)
  {
    addr = "192.168.1.160";
  }

  await sendCmd(addr, presharedKey);
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
    print(e);
    return "";
  }
}

//*************************************************************************************************

// from https://api.dart.dev/dart-io/RawDatagramSocket-class.html
Future<void> sendCmd(String addr, Uint8List key) async
{
  final clientSocket = await RawDatagramSocket.bind(InternetAddress.anyIPv4, 0);
  
  List<int> asciiValues = "Knock".codeUnits;
  Uint8List knockPacket = Uint8List.fromList(asciiValues);
  print(knockPacket);

  int bytesWritten = clientSocket.send(knockPacket, InternetAddress(addr), 12345);
  print("wrote $bytesWritten bytes");

  clientSocket.listen((event)
  {
    switch (event)
    {
      case RawSocketEvent.read:
        final datagram = clientSocket.receive();
        print("read event:");
        print("${datagram!.data.length} bytes");
        Uint8List cipherText = datagram.data;
        Uint8List plainText = decryptFromPicoW(key, cipherText);
        Uint8List newPlainText = manipulateBytes(plainText);
        Uint8List newCipherText = encryptToPicoW(key, newPlainText);
        int bytesWritten = clientSocket.send(newCipherText, InternetAddress(addr), 12345);
        print("wrote $bytesWritten bytes");
        clientSocket.close();
        break;
      case RawSocketEvent.write:
        print("write event");
        break;
      case RawSocketEvent.closed:
        print("closed event");
        break;
      default:
        print("unexpected event $event");
    }
  });
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
