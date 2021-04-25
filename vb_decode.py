import argparse
import math
import multiprocessing
import os
from os import listdir
from os.path import isfile, join
from PIL import Image
from reedsolo import RSCodec, ReedSolomonError
import shutil
import subprocess
import sys
import time
import threading
import vb_common


ENC_VERSION_NUM = 2
BLOCK_SIZE = 128
# still not the prettiest implementation but hey, it works
COLOR_PALETTES = {
    "256": [(0, 0, 0), (0, 0, 85), (36, 0, 85), (0, 182, 85), (73, 0, 85), (109, 0, 85), (73, 182, 170), (182, 182, 255), (255, 255, 0), (0, 0, 170), (182, 0, 85), (146, 182, 170), (219, 0, 85), (109, 109, 0), (182, 146, 255), (255, 0, 85), (0, 73, 255), (109, 219, 170), (36, 0, 0), (182, 73, 170), (0, 255, 170), (73, 73, 170), (219, 109, 170), (36, 109, 255), (255, 109, 85), (0, 146, 255), (182, 219, 170), (109, 255, 85), (182, 73, 85), (219, 219, 85), (255, 219, 170), (0, 36, 255), (146, 219, 255), (255, 109, 0), (0, 146, 170), (219, 255, 0), (255, 255, 85), (0, 0, 255), (36, 36, 85), (182, 0, 255), (219, 219, 255), (73, 0, 0), (73, 146, 0), (109, 146, 0), (73, 36, 170), (146, 146, 0), (182, 36, 85), (73, 146, 85), (146, 219, 170), (36, 219, 170), (255, 0, 170), (219, 36, 170), (255, 182, 85), (182, 219, 85), (0, 255, 255), (73, 109, 0), (182, 109, 255), (36, 255, 170), (109, 0, 0), (255, 219, 85), (0, 36, 170), (73, 255, 170), (146, 255, 0), (109, 109, 255), (109, 255, 170), (109, 146, 170), (182, 255, 0), (255, 219, 0), (0, 36, 85), (219, 255, 85), (255, 109, 170), (73, 0, 255), (73, 146, 170), (109, 146, 85), (255, 146, 85), (0, 109, 85), (146, 0, 0), (146, 36, 0), (182, 36, 0), (146, 146, 255), (219, 0, 170), (255, 36, 0), (0, 73, 170), (146, 36, 85), (0, 219, 170), (73, 73, 255), (109, 73, 170), (255, 73, 255), (0, 182, 0), (146, 109, 85), (255, 255, 170), (182, 0, 0), (73, 182, 85), (219, 109, 85), (182, 219, 255), (36, 182, 85), (146, 182, 85), (73, 36, 85), (255, 109, 255), (73, 182, 0), (36, 146, 170), (146, 0, 255), (0, 255, 0), (146, 182, 0), (146, 36, 170), (182, 0, 170), (219, 36, 85), (73, 255, 0), (219, 0, 0), (219, 182, 0), (36, 255, 255), (255, 182, 0), (0, 73, 85), (73, 255, 255), (255, 146, 170), (0, 109, 255), (109, 255, 255), (73, 73, 85), (219, 182, 85), (182, 255, 85), (146, 73, 85), (219, 255, 170), (182, 219, 0), (146, 109, 255), (73, 36, 0), (146, 219, 0), (219, 73, 85), (73, 146, 255), (255, 0, 0), (0, 73, 0), (146, 0, 170), (109, 219, 255), (36, 146, 0), (182, 182, 85), (0, 182, 170), (255, 219, 255), (109, 36, 85), (36, 36, 255), (36, 146, 255), (146, 146, 170), (73, 182, 255), (146, 0, 85), (20, 219, 85), (219, 146, 170), (73, 109, 85), (219, 36, 0), (182, 36, 255), (219, 182, 170), (255, 146, 0), (0, 109, 0), (146, 73, 255), (36, 73, 0), (36, 73, 85), (146, 182, 255), (109, 73, 85), (73, 255, 85), (36, 219, 255), (146, 109, 0), (36, 73, 170), (146, 255, 255), (219, 73, 170), (255, 73, 85), (0, 146, 85), (146, 146, 85), (36, 0, 255), (146, 36, 255), (0, 182, 255), (73, 73, 0), (219, 146, 85), (109, 0, 170), (255, 36, 170), (73, 36, 255), (182, 146, 0), (109, 182, 85), (73, 219, 85), (219, 146, 0), (0, 109, 170), (36, 109, 0), (219, 36, 255), (109, 182, 170), (255, 182, 170), (36, 73, 255), (73, 219, 0), (219, 219, 0), (146, 219, 85), (109, 73, 0), (73, 109, 255), (109, 109, 170), (219, 219, 170), (255, 182, 255), (219, 109, 0), (109, 219, 0), (0, 36, 0), (36, 36, 0), (255, 255, 255), (73, 0, 170), (219, 0, 255), (36, 182, 170), (109, 36, 0), (219, 182, 255), (146, 73, 0), (109, 36, 170), (109, 182, 255), (182, 182, 0), (255, 0, 255), (0, 255, 85), (182, 182, 170), (36, 255, 85), (146, 109, 170), (109, 36, 255), (255, 36, 255), (0, 219, 255), (109, 255, 0), (219, 73, 255), (109, 73, 255), (146, 255, 170), (73, 219, 170), (109, 219, 85), (146, 73, 170), (36, 36, 170), (182, 73, 0), (182, 109, 0), (36, 219, 0), (255, 73, 170), (0, 146, 0), (182, 255, 255), (36, 0, 170), (219, 255, 255), (182, 109, 85), (36, 146, 85), (109, 0, 255), (182, 255, 170), (109, 146, 255), (36, 255, 0), (182, 36, 170), (219, 73, 0), (182, 146, 85), (255, 36, 85), (0, 219, 0), (146, 255, 85), (219, 146, 255), (73, 109, 170), (109, 109, 85), (36, 109, 85), (36, 219, 85), (182, 146, 170), (73, 219, 255), (182, 73, 255), (36, 182, 0), (255, 146, 255), (219, 109, 255), (182, 109, 170), (36, 109, 170), (109, 182, 0), (36, 182, 255), (255, 73, 0)],
    "16": [(0, 0, 0), (17, 21, 178), (33, 181, 50), (40, 182, 183), (192, 27, 25), (190, 38, 179), (190, 106, 37), (184, 184, 184), (104, 104, 104), (99, 109, 247), (76, 251, 122), (70, 253, 253), (251, 111, 109), (252, 116, 249), (254, 253, 127), (255, 255, 255)],
    "4": [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)],
    "2": [(0, 0, 0), (255, 255, 255)]
}


def get_frames(input_file: str, start: int, amount: int):
    """Uses ffmpeg magic to get the nth frame of a video"""
    subprocess.run(["ffmpeg", "-i", input_file, "-vf", ("select=gte(n\,%i)" % start), "-vframes", str(amount), "-start_number", str(start), (os.path.join("tmp", "%04d.bmp"))],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.STDOUT)
    output_list = []
    for i in range(start, start + amount):
        output_list.append((os.path.join("tmp", f"{i:04}.bmp")))
    return output_list


class Frames():
    """Offers an easy interface for working with temporary frames of a video"""
    def __init__(self, input_file: str, start: int, amount: int):
        self.input_file = input_file
        self.start = start
        self.amount = amount
    
    def __enter__(self):
        return get_frames(self.input_file, self.start, self.amount)
    
    def __exit__(self, type, value, trace):
        for i in range(self.start, self.start + self.amount):
            os.remove((os.path.join("tmp", f"{i:04}.bmp")))


def try_read_pixel(color, color_palette, cps: str):
    try:
        return [color_palette.index(color), True]
    except ValueError:
        # TODO: Error correcting
        unsorted = {}
        for i in COLOR_PALETTES[cps]:
            distance = ((color[0]-i[0]) ** 2) + ((color[1]-i[1]) ** 2) + ((color[2]-i[2]) ** 2)
            unsorted[i] = distance
        return [color_palette.index(sorted(unsorted.items(), key=lambda t: t[1])[0][0]), False]


def read_frame(input_file: str, pixel_size: int, cp: int):
    image = Image.open(input_file)
    size = image.size
    scaled_size = (int(size[0] / pixel_size), int(size[1] / pixel_size))
    image = image.resize(scaled_size, Image.NEAREST)
    read_bytes = bytearray()
    color_palette = COLOR_PALETTES[str(cp)]
    pixels = list(image.getdata())
    correct_pixels = 0
    estimated_pixels = 0
    cur_byte = 0x0
    for (num, p) in enumerate(pixels):
        read_color = p
        read_pixel = try_read_pixel(read_color, color_palette, str(cp))
        if cp == 256:
            read_bytes.append(read_pixel)
        elif cp == 16:
            if num % 2 == 0:
                cur_byte = cur_byte | (read_pixel[0] << 4)
            else:
                cur_byte = cur_byte | read_pixel[0]
                read_bytes.append(cur_byte)
                cur_byte = 0x0
        elif cp == 4:
            cur_byte = cur_byte | (read_pixel[0] << (6 - ((num % 4) * 2)))
            if num % 4 == 3:
                read_bytes.append(cur_byte)
                cur_byte = 0x0
        elif cp == 2:
            cur_byte = cur_byte | (read_pixel[0] << (7 - (num % 8)))
            if num % 8 == 7:
                read_bytes.append(cur_byte)
                cur_byte = 0x0
        if read_pixel[1]:
            correct_pixels += 1
        else:
            estimated_pixels += 1
    return (read_bytes, (correct_pixels, estimated_pixels), scaled_size)


def work(number: int, pixel_size: int, palette_size: int, frame: str, ecc_bytes_count: int):
    final_bytes = bytearray()
    ecc = RSCodec(ecc_bytes_count)
    read_bytes = read_frame(frame, pixel_size, palette_size)
    blocks_per_frame = math.floor((read_bytes[2][0] * read_bytes[2][1]) / (pixel_size ** 2) / int(math.log(256, palette_size)) / BLOCK_SIZE)
    content_bytes_per_block = BLOCK_SIZE - ecc_bytes_count
    content_bytes_per_frame = blocks_per_frame * content_bytes_per_block
    for i in range(0, blocks_per_frame):
        sli = read_bytes[0][(i * BLOCK_SIZE):((i + 1) * BLOCK_SIZE)]
        try:
            final_bytes += ecc.decode(sli)[0]
        except ReedSolomonError:
            final_bytes += sli[:(BLOCK_SIZE - ecc_bytes_count)]
            print(f"WARNING: Encountered an unrecoverable data block starting at 0x{(i * BLOCK_SIZE):x}. The block will be inserted without any error-correcting, your file will most likely be damaged.")
    return (number, (final_bytes, read_bytes[1]))
    

def rebuild_file(input_file: str, checksum: bool, pixel_size: int, color_palette: int, threads: int):
    # first read the metadata frame
    correct_pixels = 0
    estimated_pixels = 0
    # get the number of frames in the video
    try:
        frames_amount = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames", "-of", "default=nokey=1:noprint_wrappers=1", input_file],
                                           capture_output=True).stdout)
    # flv, mkv and some others don't support the ffprobe method
    except ValueError:
        print("Unable to get number of frames using fast method, resorting to slower method.")
        frames_amount = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "default=nokey=1:noprint_wrappers=1", input_file],
                                           capture_output=True).stdout)
    with Frames(input_file, 0, 1) as metadata_file:
        print(f"Reading metadata frame at {metadata_file[0]}; 1/{frames_amount} ({(1/frames_amount):.2f} %).")
        meta_ecc = RSCodec(32)
        metadata_frame = read_frame(metadata_file[0], pixel_size, color_palette)
        correct_pixels += metadata_frame[1][0]
        estimated_pixels += metadata_frame[1][1]
        try:
            metadata_bytes = meta_ecc.decode(metadata_frame[0][:546])[0]
        except ReedSolomonError:
            print("Metadata frame is unrecoverable, sorry. This is a sign of either too heavy compression or wrong command line arguments. Aborting.")
            sys.exit(1)
        version = int.from_bytes(metadata_bytes[:2], byteorder="big", signed=False)
        palette_size = int.from_bytes(metadata_bytes[2:4], byteorder="big", signed=False)
        pixel_size = int.from_bytes(metadata_bytes[4:5], byteorder="big", signed=False)
        file_size = int.from_bytes(metadata_bytes[5:13], byteorder="big", signed=False)
        sha_hash = metadata_bytes[13:33]
        ecc_bytes_count = int.from_bytes(metadata_bytes[33:34], byteorder="big", signed=False)
        # strip the file name of any NULLs because python cries when trying to save a file with NULL in its name
        file_name = metadata_bytes[34:546].decode("utf-8").rstrip("\x00")
    if version != ENC_VERSION_NUM:
        print("WARNING: The encoding version of the file doesn't match with the version of this decoder!")
    cur_frame = 1
    print("Starting decoding file \"%s\" (Size: %d bytes; Hash: %s; Encoding Version: %d; Palette Size: %d; Pixel Size: %d)." % (file_name, file_size, sha_hash.hex(), version, palette_size, pixel_size))
    # yes, the level of indentations is horrendous, no, I'm not proud of it, but it works
    with open(file_name, "wb") as file:
        while cur_frame < frames_amount:
            with multiprocessing.Pool(threads) as p:
                read_amount = vb_common.clamp(frames_amount - cur_frame, 0, threads)
                with Frames(input_file, cur_frame, read_amount) as frames_list:
                    arguments = []
                    for f in frames_list:
                        if cur_frame < frames_amount:
                            arguments.append((cur_frame, pixel_size, color_palette, f, ecc_bytes_count))
                            cur_frame += 1
                    # the threads probably won't finish in order, so we have to sort their results
                    results = sorted(p.starmap(work, arguments), key=lambda x: x[0])
                    for r in results:
                        correct_pixels += r[1][1][0]
                        estimated_pixels += r[1][1][1]
                        file.write(r[1][0])
            percent = ((cur_frame+1)/(frames_amount+1))*100
            print(f"Read all frames up to {cur_frame+1}/{frames_amount+1} ({percent:.2f} %).")
        # we probably have written a bunch of 0x00 at the end, truncate them
        print(f"Finished reading frames. Perfectly read pixels: {correct_pixels}, Guessed pixels: {estimated_pixels}, Total pixels: {correct_pixels + estimated_pixels}, Ratio of guessed bytes and total bytes: {estimated_pixels / (correct_pixels + estimated_pixels)}.\nTruncating trailing NULLs.")
        file.seek(file_size)
        file.truncate()
    if checksum:
        print("Comparing checksums.")
        if vb_common.sha1_file(file_name) == sha_hash:
            print("Checksum comparison successful!")
        else:
            print("Checksum comparison failed! It's very likely that the video file has been corrupted beyond repair in some way (likely due to compression).")
    


if __name__ == "__main__":
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="Tool to turn videos encoded by vb_encode.py into (hopefully) usable data again.")
    parser.add_argument("input", metavar="input_file", type=str, help="The encoded file to be decoded")
    parser.add_argument("--no_checksum", dest="no_checksum", action="store_true", default=False, help="Skips the checksum comparison after decoding.")
    parser.add_argument("--pixel_size", metavar="pixel_size", type=int, help="The size each pixel is in the video.", default=1)
    parser.add_argument("--color_palette", metavar="color_palette", type=int, help="The color palette used in the video.", default=4)
    parser.add_argument("--threads", metavar="threads", type=int, help="Amount of threads to use for encoding. Defaults to all available cores.", default=len(os.sched_getaffinity(0)))
    
    print("IMPORTANT: THIS TOOL COMES WITH NO WARRANTY WHATSOEVER. USE AT YOUR OWN RISK.")
    
    # TODO: determine pixel size and color palette automatically
    
    args = parser.parse_args()
    
    if str(args.color_palette) not in COLOR_PALETTES.keys():
        raise ValueError("Invalid color palette size! Use one of these values: %s." % str(list(COLOR_PALETTES.keys())))
    
    print("Starting decoding process.")
    
    if not os.path.exists("tmp"):
    	os.mkdir("tmp")
    
    rebuild_file(args.input, not args.no_checksum, args.pixel_size, args.color_palette, args.threads)
    print("Done! Cleaning up.")
    shutil.rmtree("tmp")
    
    print("Process took %.2fs seconds." % (time.time() - start_time))
