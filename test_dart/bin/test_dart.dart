import 'dart:io';
import 'dart:typed_data';
import 'package:pointycastle/export.dart';
// see https://pub.dev/packages/pointycastle

//*************************************************************************************************

const keyBytes = [7,139,240,55,27,148,191,122,61,250,38,68,162,7,14,0,129,126,131,150,229,46,106,25,39,159,13,63,169,187,0,104,];

//*************************************************************************************************

void main()
{
  Uint8List presharedKey = Uint8List.fromList(keyBytes);
  print("key length = ${presharedKey.length}");
  print(presharedKey);

  File cipherTextFile = File("ciphertext.bin");
  Uint8List cipherText = cipherTextFile.readAsBytesSync();
  print("ciphertext length = ${cipherText.length}");

  Uint8List plainText = decryptFromPicoW(presharedKey, cipherText);
  prettyPrint(plainText);

  Uint8List check = encryptToPicoW(presharedKey, plainText);
  verifyEqualLists(cipherText, check);
}

//*************************************************************************************************

void verifyEqualLists(Uint8List first, Uint8List second)
{
  if (first.length != second.length)
  {
    print("lists have different lengths!");
    return;
  }

  bool equal = true;

  for (int i = 0; i < first.length; i++)
  {
    if (first[i] != second[i])
    {
      equal = false;
    }
  }

  if (equal)
  {
    print("equal");
  }
  else
  {
    print("not equal");
  }
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

void manipulateBytes()
{
  // TODO:
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

//*************************************************************************************************

void prettyPrint(Uint8List data)
{
  String stringData = String.fromCharCodes(data);
  print("stringData length = ${stringData.length}");
  print(stringData);
}
