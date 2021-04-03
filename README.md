# videobackup

A set of Python scripts that can turn any file into a video file and vice versa.

## About this tool

The set consists out of two Python scripts: ``vb_encode.py`` that encodes any file into a video and ``vb_decode.py``, that can decode a video file back into its original form.
If you plan on uploading such a video file to a video hosting service, please make sure that the service's compression isn't too harsh on the video since this can quickly make the file unrecoverable. When in doubt, go for a 2 color palette, a pixel size of 2 and 2160p resolution. While this will give you an extremely low efficiency, it makes the file more resilient against compression.
Keep in mind that decoding, especially when the video has been compressed, can be *very* slow, atleast until I managed to implement multithreaded decoding.

## Requirements

- Python >= 3.8.6
- pillow >= 7.2.0
- ffmpeg
- Beefy hardware
  
Earlier versions of the requirements probably work too but this is what I tested it with.

## Todo

- Improve multithreaded encoding
- Implement multithreaded decoding
- Better error correction
- Less spaghetti code (e. g. decoding algorithm)
- Fix that weird bug where the encoder adds a bunch of unnecessary NULL frames - it doesn't hurt as the decoder truncates it anyways but still
