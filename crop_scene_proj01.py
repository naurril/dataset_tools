


import argparse
import os
from select import select
import re

camera_list = ["front", "front_right", "front_left", "rear_left", "rear_right", "rear"]
aux_lidar_list = ["front","left","right","rear"]
slots = ["000", "500"]
radar_list = [
    'points_front', 'points_front_left', 'points_front_right','points_rear', 'points_rear_left', 'points_rear_right',
    'tracks_front', 'tracks_front_left', 'tracks_front_right','tracks_rear', 'tracks_rear_left', 'tracks_rear_right'
]



def prepare_dirs(path):
    if not os.path.exists(path):
            os.makedirs(path)


# in dataset folder
def generate_dataset_links(src_data_folder, start_time, end_time, exclude='', sub_actions=""):
   
    # assume we are already in target folder
    # and src_data_folder is abs path
    
    prepare_dirs('camera')
    prepare_dirs('lidar')
    prepare_dirs('label')
    prepare_dirs('aux_lidar')
    prepare_dirs('aux_camera')
    prepare_dirs('ego_pose')
    prepare_dirs("calib/camera")
    prepare_dirs("calib/aux_camera")

    # prepare_dirs(os.path.join(dataset_path, 'calib'))
    # prepare_dirs(os.path.join(dataset_path, 'calib/camera'))
    
    #os.system("ln -s -f ../../calib ./")
    if len(sub_actions)>0:
        sub_actions = sub_actions.split(",")
    else:
        sub_actions = ['camera','aux_camera','lidar','calib', 'ego_pose']

    

    src_frames = os.listdir(os.path.join(src_data_folder, 'lidar'))
    src_frames.sort()
    frames = list(map(lambda f: f.split(".")[0], src_frames))
    print('available', frames)

    def in_range(f):
        if start_time and f < start_time:
            return False
        if end_time and f > end_time:
            return False
        
        if exclude and re.fullmatch(exclude, f):
            return False

        return True


    selected_frames = list(filter(in_range, frames))
    print('selected', selected_frames)


    if len(selected_frames) == 0:
        print("no frame selected.")
        return


    print(sub_actions)

    for action in sub_actions:
        if action == 'camera':
            os.chdir("camera")

            for camera in camera_list:                
                prepare_dirs(camera)
                os.chdir(camera)
                for f in selected_frames:                                        
                        os.system("ln -s -f " + src_data_folder  + "/camera/" + camera + "/"+ f + "* ./")
                os.chdir("..")
            os.chdir("..")

        elif action == 'aux_camera':
            os.chdir("aux_camera")

            for camera in camera_list:                
                prepare_dirs(camera)
                os.chdir(camera)
                for f in selected_frames:                                        
                        os.system("ln -s -f " + src_data_folder  + "/aux_camera/" + camera + "/"+ f + "* ./")
                os.chdir("..")
            os.chdir("..")
        
        elif action == 'calib':
            os.chdir("calib/camera")
            
            #link basic calibration parameters
            os.system("ln -s  " + src_data_folder +"/calib/camera/*.json ./")

            for camera in camera_list:
                if os.path.exists(src_data_folder  + "/calib/camera/" + camera):
                    prepare_dirs(camera)
                    os.chdir(camera)

                    
                    for f in selected_frames:
                            os.system("ln -s  " + src_data_folder  + "/calib/camera/" + camera + "/"+ f + "* ./")
                    os.chdir("..")

            os.chdir("../..") #scene-xxx
            

            os.chdir("calib/aux_camera")
            os.system("ln -s  " + src_data_folder + "/calib/aux_camera/*.json ./")

            for camera in camera_list:
                if os.path.exists(src_data_folder  + "/calib/aux_camera/" + camera):
                    prepare_dirs(camera)
                    os.chdir(camera)

                    for f in selected_frames:
                            os.system("ln -s " + src_data_folder  + "/calib/aux_camera/" + camera + "/"+ f + "* ./")
                    os.chdir("..")

            os.chdir("../..") #scene-xxx

        elif action == 'lidar':            
            os.chdir("lidar")
            for f in selected_frames:
                    os.system("ln -s -f " + src_data_folder + "/lidar/" + str(f) + "* ./")
            os.chdir("..")

        elif action == 'ego_pose':
            os.chdir("ego_pose")
            for f in selected_frames:
                    os.system("ln -s -f " + src_data_folder + "/ego_pose/" + f + "* ./")
            os.chdir("..")

        elif action == 'aux_lidar':
            os.chdir("aux_lidar")

            for auxlidar in aux_lidar_list:
                
                prepare_dirs(auxlidar)
                os.chdir(auxlidar)

                for f in selected_frames:
                        os.system("ln -s " + src_data_folder  + "/aux_lidar/" + auxlidar + "/"+ f + "*  ./")
                os.chdir("..")
        elif action == 'radar':
            os.chdir("radar")

            for radar in radar_list:
                
                prepare_dirs(radar)
                os.chdir(radar)

                for f in selected_frames:
                        os.system("ln -s -f  " + src_data_folder  + "/radar/" + radar + "/"+ f + "*  ./")
                os.chdir("..")

        else:
            print("unknown action", action)

def generate_dataset(src_dataset_folder, target_dataset_folder,desc, start_time, end_time, exclude):
    
    savecwd = os.getcwd()

    if os.path.exists(target_dataset_folder):
        print("destination folder exists.")
        return
    prepare_dirs(target_dataset_folder)


    os.chdir(target_dataset_folder)
    src_dataset_folder = os.path.abspath(src_dataset_folder)
    with open("./desc.json", "w") as f:
        f.writelines([
            '{\n',
            '"scene":"' + desc +'\",\n',
            '"folder":"' + src_dataset_folder +'\",\n',
            '"starttime":"' + str(start_time) +'\",\n',
            '"endtime":"' + str(end_time) +'\"\n',
            '}\n'
        ])

    generate_dataset_links(src_dataset_folder, start_time, end_time, exclude)

    os.chdir(savecwd)
    return id



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='crop dataset')
    parser.add_argument('--hz', type=str, default='2hz', help="for generate dataset")
    parser.add_argument('src', type=str, help='')
    parser.add_argument('target', type=str,  help='')
    parser.add_argument('desc', type=str, help='')
    parser.add_argument('--start', type=str, help='')
    parser.add_argument('--end', type=str, help='')    
    parser.add_argument('--exclude', type=str, help='regular expression pattern')
    parser.add_argument('--sub_actions', type=str, help='')
    
    args = parser.parse_args()

    print(args)
    generate_dataset(args.src, args.target, args.desc, args.start, args.end, args.exclude)

