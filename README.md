# videobackup

A set of Python scripts that can turn any file into a video file and vice versa.

## About this tool

The set consists out of two Python scripts: ``vb_encode.py`` that encodes any file into a video and ``vb_decode.py``, that can decode a video file back into its original form.
If you plan on uploading such a video file to a video hosting service, please make sure that the service's compression isn't too harsh on the video since this can quickly make the file unrecoverable. When in doubt, go for a 2 color palette, a pixel size of 2 and 2160p resolution. While this will give you an extremely low efficiency, it makes the file more resilient against compression.

## Features

- Pixel-level error correction
- Byte-level error correction
- Quite configurable
- Dodgy multithreading
- Output files have enormous sizes (a good feature if you don't like disk space)

## Requirements

- Python >= 3.8.6
- pillow >= 7.2.0
- reedsolo >= 1.5.4
- ffmpeg
- Beefy hardware*
  
Earlier versions of the requirements probably work too but this is what I tested it with.

\*Especially CPU horsepower and RAM is important. This tool can make use of all of your threads, but keep in mind that every thread needs a lot of RAM (e. g. ~700 MiB *per thread* when decoding a 2160p video). Also be aware that depending on the encoding options, the result video can be 5 to 9 times as large as the original file.

## Todo (somewhat ordered from high to low priority)

- Write and read BMPs ourselves to speed up decoding (and hopefully encoding too)
- When encoding, append generated frames to a video directly without buffering on disk
- Improve multithreaded encoding
- Improve multithreaded decoding
- Automatic detection of color palette and pixel size when decoding
- Less spaghetti code (e. g. decoding algorithm)
