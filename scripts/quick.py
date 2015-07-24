import sys
import os
import logging
import argparse
import shutil
import base64
import json
import subprocess
from tempfile import NamedTemporaryFile
from qconvert.convert import resize
from qconvert.utils import setup_command_logger



image_processors = {
    '.jpg': {
        'bin': 'mozcjpeg',
        'options': ['-outfile', None, '-quality', '75']
    },
    '.png': {
        'bin': 'pngquant',
        'options': ['--force', '--speed', '1', '--ext', '-opt.png']
    }
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Quickly convert some images')
    parser.add_argument('infilename', metavar='INFILE', type=str, help="path to input file")
    parser.add_argument('outfilename', metavar='OUTFILE', type=str, help="path to output file")
    parser.add_argument('-f', '--scale-factor', type=float, help="scale factor", dest="scale_factor")
    parser.add_argument('-x', '--width', type=int, help="output image width", dest="width")
    parser.add_argument('-y', '--height', type=int, help="scale image height", dest="height")
    parser.add_argument('-v', '--verbose', action="store_true", dest="verbose", default=False)
    parser.add_argument('-no-opt', help="optimize image output size", action="store_false", dest="optimize", default="True")
    parser.add_argument('--no-b64', help="disable b64 output", action="store_false", dest="b64", default=True)
    args = parser.parse_args()


    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logger = setup_command_logger(log_level)

    image = resize(args.infilename, args.scale_factor, args.width, args.height)

    # optimization
    path_segment, ext = os.path.splitext(args.outfilename.lower())
    if ext in image_processors and args.optimize:
        temp_resized = "/tmp/temp{0}".format(ext)
        optimized_filename = "/tmp/temp-opt{0}".format(ext)

        format = ext[1:] # extension without the dot
        if format.lower() == 'jpg':
            format = 'jpeg'
        image.save(temp_resized, format)

        cmd_params = image_processors.get(ext)
        executable = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../bin", cmd_params["bin"])
        cmd_args = [executable]
        for param in cmd_params["options"]:
            if param is None:
                cmd_args.append(optimized_filename)
            else:
                cmd_args.append(param)
        cmd_args.append(temp_resized)

        rv = subprocess.call(cmd_args, stdout=sys.stdout, stderr=sys.stderr)
        if rv != 0:
            logger.error("optimization failed")
            sys.exit(rv)

        # check if optimized image is actually smaller
        resized_size = os.stat(temp_resized).st_size
        optimized_size = os.stat(optimized_filename).st_size
        logger.info("{0}-optimized size: {1} regular: {2}".format(cmd_params["bin"], optimized_size, resized_size))

        if optimized_size > resized_size:
            shutil.move(optimized_filename, args.outfilename)
            os.remove(temp_resized)
        else:
            shutil.move(temp_resized, args.outfilename)
            os.remove(optimized_filename)

        logger.info("wrote {0}".format(args.outfilename))

    # base64 dataURI
    if args.b64:
        with open(args.outfilename, 'r') as infile:
            with open("{0}.json".format(path_segment), 'w') as outfile:
                data = infile.read()
                encoded = base64.b64encode(data)
                json.dump({"dataURI": encoded}, outfile)
                logger.info("wrote ./out.json")

