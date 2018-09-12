Tv-dl
=====

Slouží ke stahování videí z archivu převážně českých televizí.

Závislosti
----------

* Python >= 3.2
* wget

Podporované systémy
-------------------

* Linux
* Windows
    * wget není standardní součástí Windows, ale existuje několik způsobů, jak ho získat: GNUWin32, Cygwin, MinGW, Bash on Windows...
* (Mac OS - netestováno, ale mělo by fungovat)

Podporované archivy
-------------------

* ČT iVysílání (http://www.ceskatelevize.cz/ivysilani/)

Použití
-------

1. Najdi si v archivu pořad, který chceš stáhnout

2. Spusť `tv-dl` a jako parametr mu dej URL stránky s pořadem, například:

```
./tv-dl http://www.ceskatelevize.cz/ivysilani/10348527168-jak-na-ryby-s-rudou-hrusinskym/211562220200013-jak-na-ryby-s-rudou-hrusinskym/
```

Pokud systém neumí najít interpret Pythonu 3, je nutné spouštět program takto (cesty je samozřejmě nutné přizpůsobit danému systému):

```
C:\Python3\python.exe C:\Users\me\tv-dl\tv-dl http://www.ceskatelevize.cz/ivysilani/10348527168-jak-na-ryby-s-rudou-hrusinskym/211562220200013-jak-na-ryby-s-rudou-hrusinskym/
```

3. Skript stáhne pořad v nejvyšší možné kvalitě.


### Vypsání seznamu kvalit/videí

Pro vypsání možných kvalit spusť `tv-dl` s parametry ve tvaru:

    ./tv-dl -q list URL

Pro stažení poté použij místo slova list jeden z identifikátorů, který bude vypsán v levém sloupci.
Obdobně probíhá výběr videa ze stránky u Show Jana krause (parametr `-m`).

### Volby

    -g, --get-url
                        nestahuje, použe vypíše URL adresu videa (dá se použít v některých přehrávačích)
    -q QUALITY, --quality QUALITY
                        nastavuje kvalitu (list pro vypsání možností)
    -m MOVIE, --movie MOVIE
                        vybírá video ze stránky (list pro vypsání možností)
    -o OUTPUT, --output OUTPUT
                        nastavuje výstupní soubor
    -k, --insecure
                        dovolí stahovat zabezpečené HTTPS stránky i přes problémy s certifikátem

### Skript tv-play

Tento skript nestahuje, ale přímo spustí přehrávač s daným pořadem. Přijímá stejné parametry jako `tv-dl`. Jako výchozí přehrávač se používá `totem`.

Výběr jiného přehrávače je možný vytvořením souboru `~/.tv-play` s obsahem ve tvaru `player=příkaz_pro_spuštění_přehrávače`
Bohužel to asi funguje jenom s totemem...
