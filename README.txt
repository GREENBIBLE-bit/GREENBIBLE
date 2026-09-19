GREENBIBLE - ONE-GO CLEAN BUILD

Copy these files into your existing GREENBIBLE_v1 folder, alongside kjv.sqlite.
Then run INSTALL_GREENBIBLE.bat once, or use Command Prompt:
  py -m py_compile app.py smart_parser.py
  py app.py

The build uses SoundDevice at 48 kHz and does not require PyAudio.
Voice examples:
  John 3:16
  first Corinthians 15:1
  second Corinthians 3:5
  revelations 3:5
  James 12   (database-aware chapter/verse splitting)

The NDI/vMix output stage is intentionally the next module; this build keeps the working voice/KJV core stable.
