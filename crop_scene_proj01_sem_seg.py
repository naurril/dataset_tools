

import argparse
from logging import root
import os
import re


parser = argparse.ArgumentParser(description='crop dataset')
parser.add_argument('src_dir', default='../proj01_scenes', type=str, help='')
parser.add_argument('--dst_dir', default='./', type=str, help='')
parser.add_argument('--scenes', default='.*', type=str, help='')    
parser.add_argument('--frames', default='.*[0|2|4|6|8]0\.000.*', type=str, help='')
args = parser.parse_args()



def prepare_dirs(path):
    if not os.path.exists(path):
            os.makedirs(path)


def generate_scene(s):
    print("generating", s)

    prepare_dirs(os.path.join(args.dst_dir, s))
    prepare_dirs(os.path.join(args.dst_dir, s, 'label'))
    prepare_dirs(os.path.join(args.dst_dir, s, 'image'))

    files = os.listdir(os.path.join(args.src_dir, s, 'camera', 'front'))
    print(files)
    for f in files:

        if not re.fullmatch(args.frames, f):
            continue

        print(f)
        os.system('ln -s -f ' + args.src_dir +'/' + s + '/camera/front/'+f + ' -t ' + args.dst_dir + '/' + s +'/image')



def run():
    
    scenes = os.listdir(args.src_dir)

    for s in scenes:
        if re.fullmatch(args.scenes, s):
            generate_scene(s)

run()
    

