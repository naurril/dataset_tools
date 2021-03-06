
import os
import sys
from pyproj import Proj #wgs84->utm transformation

from progress.bar import Bar

import align_frame_time
import rectify_image
import pcd_restore
import json
import numpy as np
import math
import argparse





camera_list = [
  'front', 'front_left', 'front_right','rear',
  'rear_left', 'rear_right']

aux_lidar_list=[] #['front','rear','left','right']

camera_time_offset = {
    'rear': 0,
    'rear_left': -17,
    'front': -50, 
    'front_left': -33,
    'front_right': -67,
    'rear_right': -83,
}


radar_list = [
    'points_front', 'points_front_left', 'points_front_right','points_rear', 'points_rear_left', 'points_rear_right',
    'tracks_front', 'tracks_front_left', 'tracks_front_right','tracks_rear', 'tracks_rear_left', 'tracks_rear_right'
]


def rectify_one_camera(camera, calib_path, raw_data_path, output_path):
    calib_file = os.path.join(calib_path, 'camera', camera, 'ost.yaml')
    rectify_image.rectify_folder(calib_file, 
                                os.path.join(raw_data_path, 'cameras', camera, 'image_color/compressed'),
                                os.path.join(output_path, 'intermediate', 'camera', camera, 'rectified'))
def rectify_one_infrared_camera(camera, calib_path, raw_data_path, output_path):
    calib_file = os.path.join(calib_path, 'infrared_camera', camera, 'ost.yaml')
    rectify_image.rectify_folder(calib_file, 
                                os.path.join(raw_data_path, 'infrared_camera', camera, 'image_color'),
                                os.path.join(output_path, 'intermediate', 'infrared_camera', camera, 'rectified'))
def color_one_infrared_camera(camera, raw_data_path, output_path):
    rectify_image.color_folder(os.path.join(output_path, 'intermediate', 'infrared_camera',  camera, 'rectified'),
                                os.path.join(output_path, 'intermediate', 'infrared_camera', camera, 'colored'))

def prepare_dirs(path):
    if not os.path.exists(path):
            os.makedirs(path)


# if use restored lidar point clouds,
# we compensate motion effect for calibration.

def generate_dataset(extrinsic_calib_path, dataset_path, timeslots, lidar_type="restored", sub_actions=""):
    print("generate dataset",dataset_path, timeslots)

    prepare_dirs(dataset_path)
    prepare_dirs(os.path.join(dataset_path, 'camera'))

    if os.path.exists(os.path.join(dataset_path, 'infrared_camera')):
        os.system("mv "+os.path.join(dataset_path, 'infrared_camera') + " " + os.path.join(dataset_path, 'aux_camera'))
        
    prepare_dirs(os.path.join(dataset_path, 'aux_camera'))
    prepare_dirs(os.path.join(dataset_path, 'lidar'))
    prepare_dirs(os.path.join(dataset_path, 'aux_lidar'))
    prepare_dirs(os.path.join(dataset_path, 'radar'))    

    prepare_dirs(os.path.join(dataset_path, 'label'))
    prepare_dirs(os.path.join(dataset_path, 'ego_pose'))


    #prepare_dirs(os.path.join(dataset_path, 'calib'))
    #prepare_dirs(os.path.join(dataset_path, 'calib/camera'))

    os.chdir(dataset_path)


    if len(sub_actions)>=1:
        actions = sub_actions.split(",")        
    else:
        actions = ['calib','default_calib', 'camera','aux_camera','ego_pose','lidar','aux_lidar']

    print('actions', actions)

    for action in actions:
        if action == 'calib':
            if lidar_type == 'restored':
                if os.path.islink(os.path.join(dataset_path, "calib")):
                    os.system("rm calib")

                for camera in camera_list:
                    prepare_dirs(os.path.join(dataset_path, "calib", "camera", camera))
                    os.chdir(os.path.join(dataset_path, "calib", "camera", camera))
                    for slot in timeslots:
                        os.system("ln -s -f  ../../../../intermediate/calib_lidar_transform/camera/" + camera + "/*" + slot+".json  ./")
                
                for camera in camera_list:
                    prepare_dirs(os.path.join(dataset_path, "calib", "aux_camera", camera))
                    os.chdir(os.path.join(dataset_path, "calib", "aux_camera", camera))
                    for slot in timeslots:
                        os.system("ln -s -f  ../../../../intermediate/calib_lidar_transform/aux_camera/" + camera + "/*" + slot+".json  ./")

            else:
                os.system("ln -s -f " + os.path.relpath(extrinsic_calib_path) + " ./calib")

        if action == 'default_calib':

            if lidar_type == 'restored':
                prepare_dirs(os.path.join(dataset_path, "calib", "camera"))
                os.chdir(os.path.join(dataset_path, "calib", "camera"))
                os.system("ln -s -f " + extrinsic_calib_path + '/camera/*' +" ./")

                prepare_dirs(os.path.join(dataset_path, "calib", "aux_camera"))
                os.chdir(os.path.join(dataset_path, "calib", "aux_camera"))
                os.system("ln -s -f " + extrinsic_calib_path + "/aux_camera/* ./")

        if action == 'camera':
            for camera in camera_list:
                prepare_dirs(os.path.join(dataset_path, "camera",  camera))
                os.chdir(os.path.join(dataset_path, "camera", camera))

                for slot in timeslots:
                    os.system("ln -s -f  ../../../intermediate/camera/" + camera + "/aligned/*"+slot+".jpg  ./")

        if action == 'aux_camera':
            for camera in camera_list:
                prepare_dirs(os.path.join(dataset_path, "aux_camera",  camera))
                os.chdir(os.path.join(dataset_path, "aux_camera", camera))

                for slot in timeslots:
                    os.system("ln -s -f  ../../../intermediate/infrared_camera/" + camera + "/aligned/*"+slot+".jpg  ./")

        if action == 'lidar':            
            os.chdir(os.path.join(dataset_path, "lidar"))

            for slot in timeslots:
                os.system("ln -s -f ../../intermediate/lidar/" + lidar_type +"/*"+slot+".pcd ./")
        
        if action == 'ego_pose':
            os.chdir(os.path.join(dataset_path, "ego_pose"))

            for slot in timeslots:
                os.system("ln -s -f ../../intermediate/ego_pose/aligned/*"+slot+".json ./")
        
        if action == 'aux_lidar':
            for al in aux_lidar_list:
                
                dir = os.path.join(dataset_path, "aux_lidar", al)
                prepare_dirs(dir)
                os.chdir(dir)

                for slot in timeslots:
                    os.system("ln -s -f  ../../../intermediate/aux_lidar/" + al + "/*"+slot+".pcd  ./")
        
        if action == 'radar':
            for r in radar_list:                
                dir = os.path.join(dataset_path, "radar", r)
                prepare_dirs(dir)
                os.chdir(dir)

                for slot in timeslots:
                    os.system("ln -s -f  ../../../intermediate/radar/" + r + "/*"+slot+".pcd  ./")

def generate_dataset_10hz(extrinsic_calib_path, dataset_path, lidar_type="restored", sub_actions=""):
    print("generate 10hz dataset",dataset_path)
    prepare_dirs(dataset_path)
    prepare_dirs(os.path.join(dataset_path, 'camera'))

    if os.path.exists(os.path.join(dataset_path, 'infrared_camera')):
        os.system("mv "+os.path.join(dataset_path, 'infrared_camera') + " " + os.path.join(dataset_path, 'aux_camera'))
        
    prepare_dirs(os.path.join(dataset_path, 'aux_camera'))
    #prepare_dirs(os.path.join(dataset_path, 'lidar'))
    #prepare_dirs(os.path.join(dataset_path, 'aux_lidar'))
    prepare_dirs(os.path.join(dataset_path, 'radar'))    

    prepare_dirs(os.path.join(dataset_path, 'label'))
    prepare_dirs(os.path.join(dataset_path, 'ego_pose'))


    #prepare_dirs(os.path.join(dataset_path, 'calib'))
    #prepare_dirs(os.path.join(dataset_path, 'calib/camera'))

    os.chdir(dataset_path)

    if lidar_type == 'restored':
        if os.path.islink(os.path.join(dataset_path, "calib")):
            os.system("rm calib")
        
        prepare_dirs(os.path.join(dataset_path, "calib", "camera"))
        os.chdir(os.path.join(dataset_path, "calib", "camera"))
        os.system("ln -s -f  ../../../intermediate/calib_lidar_transform/camera/* ./")
        os.system("ln -s -f " + extrinsic_calib_path + "/camera/* ./")
        
        prepare_dirs(os.path.join(dataset_path, "calib", "aux_camera"))
        os.chdir(os.path.join(dataset_path, "calib", "aux_camera"))
        os.system("ln -s -f  ../../../intermediate/calib_lidar_transform/aux_camera/* ./")
        os.system("ln -s -f " + extrinsic_calib_path + "/aux_camera/* ./")
    else:
        os.system("ln -s -f " + extrinsic_calib_path + " ./calib")


    for camera in camera_list:
        prepare_dirs(os.path.join(dataset_path, "camera"))
        os.chdir(os.path.join(dataset_path, "camera"))
        os.system("ln -s -f  ../../intermediate/camera/" + camera + "/aligned ./"+camera)
    
    for camera in camera_list:
        prepare_dirs(os.path.join(dataset_path, "aux_camera"))
        os.chdir(os.path.join(dataset_path, "aux_camera"))
        os.system("ln -s -f  ../../intermediate/infrared_camera/" + camera + "/aligned ./"+camera)
        
    os.chdir(os.path.join(dataset_path))
    print(os.getcwd())
    print("ln -s ../intermediate/lidar/" + lidar_type +" lidar")
    os.system("ln -s ../intermediate/lidar/" + lidar_type +" lidar")
    
    os.chdir(os.path.join(dataset_path, "ego_pose"))
    os.system("ln -s -f ../../intermediate/ego_pose/aligned ./ego_pose")
    
    os.chdir(dataset_path)
    os.system("ln -s -f  ../intermediate/aux_lidar ./")

    
def generate_pose(raw_data_path, output_path):
    dst_folder = os.path.join(output_path, "intermediate", "ego_pose", "filtered")
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    src_folder = os.path.join(raw_data_path, "gps_imu", "insinfo")

    files = os.listdir(src_folder)
    files.sort()


    wgs84_utm50_proj = Proj(proj='utm',zone=50,ellps='WGS84', preserve_units=False)

    with Bar('filtering pose', max=len(files)) as bar:
        for f in files:
            bar.next()
            with open(os.path.join(src_folder, f)) as fin:
                line = fin.readlines()[0]   
                timestamp, content = line.split(' ')
                header, payload = content.split(';')
                #print(timestamp, header, payload)
                ins_status, pos_type, lat, lng, height, _, north_vel, east_vel, up_vel, roll, pitch, azimuth, \
                _,_,_,_,_,_,_,_,_,_,_ = payload.split(',')
                #print(ins_status, pos_type, lat, lng, height, north_vel, east_vel, up_vel, roll, pitch, azimuth)

                x,y = wgs84_utm50_proj(float(lng), float(lat))

                with open(os.path.join(dst_folder, os.path.splitext(f)[0]+".json"), "w") as fout:
                    fout.writelines([
                        '{\n',
                        '"ins_status":"' + ins_status +'\",\n',
                        '"pos_type":"' + pos_type +'\",\n',
                        '"lat":"' + lat +'\",\n',
                        '"lng":"' + lng +'\",\n',
                        '"height":"' + height +'\",\n',
                        '"north_vel":"' + north_vel +'\",\n',
                        '"east_vel":"' + east_vel +'\",\n',
                        '"up_vel":"' + up_vel +'\",\n',
                        '"roll":"' + roll +'\",\n',
                        '"pitch":"' + pitch +'\",\n',
                        '"azimuth":"' + azimuth +'\",\n',
                        '"x":"' + str(x) +'\",\n',
                        '"y":"' + str(y) +'\",\n',
                        '"z":"' + height +'\"\n',
                        '}\n'
                    ])
                


    
def rectify_cameras(intrinsic_calib_path, raw_data_path, output_path):
          
        for camera in camera_list:
            rectify_one_camera(camera, intrinsic_calib_path, raw_data_path, output_path)
            rectify_one_infrared_camera(camera, intrinsic_calib_path, raw_data_path, output_path)

def color_infrared_image(raw_data_path, output_path):
    for camera in camera_list:
            color_one_infrared_camera(camera, raw_data_path, output_path)

def align(raw_data_path, output_path):
        print(output_path)
        # ego pose
        align_frame_time.link_one_folder(os.path.join('../filtered'),
                                     os.path.join(output_path, 'intermediate', 'ego_pose', "aligned"),
                                     0,
                                     20, 
                                     9,
                                     50) #period


        for camera in camera_list:            
            align_frame_time.link_one_folder(os.path.join('../rectified'),
                                     os.path.join(output_path, 'intermediate', 'camera', camera, 'aligned'),
                                     camera_time_offset[camera]
                                    )
            
            align_frame_time.link_one_folder(os.path.join('../rectified'),
                                     os.path.join(output_path, 'intermediate', 'infrared_camera', camera, 'aligned'),
                                     camera_time_offset[camera],
                                     30, 0)

        if os.path.exists(os.path.join(raw_data_path, 'pandar_points')):
            align_frame_time.link_one_folder(os.path.join(raw_data_path, 'pandar_points'),  #after 07.15, this topic path has hesai prefix.
                                            os.path.join(output_path, 'intermediate', 'lidar/aligned'),
                                            0, 30, 0)
        else:
            align_frame_time.link_one_folder(os.path.join(raw_data_path, 'hesai', 'pandar_packets'),  #after 07.15, this topic path has hesai prefix.
                                            os.path.join(output_path, 'intermediate', 'lidar/aligned'),
                                            0, 30, 0)

        for al in aux_lidar_list:
            align_frame_time.link_one_folder(os.path.join(raw_data_path, 'rsbp_'+al+'/rslidar_points'),
                                     os.path.join(output_path, 'intermediate', 'aux_lidar',al),
                                     0,
                                     30, 100)
        

def align_radar(raw_data_path, output_path):
    radar_list = [ 'front', 'front_left', 'front_right','rear', 'rear_left', 'rear_right']

    for r in radar_list:
        align_frame_time.link_one_folder(os.path.join(raw_data_path, 'radar_points', r),
                                    os.path.join(output_path, 'intermediate', 'radar', "points_"+r),
                                    0,
                                    20,
                                    0,
                                    50,
                                    "")
    for r in radar_list:
        align_frame_time.link_one_folder(os.path.join(raw_data_path, 'radar_tracks', r),
                                    os.path.join(output_path, 'intermediate', 'radar', "tracks_"+r),
                                    0,
                                    20,
                                    0,
                                    50,
                                    "")

def timestamp_add(ts, delta_ms):
    [s,ms] = ts.split(".")
    s = int(s)
    ms = int(ms)
    new_ms = ms+delta_ms    
    new_s = s + (new_ms // 1000)
    new_ms %= 1000
    return str(new_s)+"." + "{:03d}".format(new_ms)

def lidar_pcd_restore(output_path):
    dst_folder = os.path.join(output_path, "intermediate", "lidar", "restored")
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    src_folder = os.path.join(output_path, "intermediate", "lidar", "aligned")

    files = os.listdir(src_folder)
    files.sort()

    pose_folder = os.path.join(output_path, "intermediate", "ego_pose", "aligned")

    with Bar('restoring lidar', max=len(files)) as bar:
        for f in files:
            bar.next()
            timestamp = os.path.splitext(f)[0]
            nexttimestamp = timestamp_add(timestamp, 100)

            pose1file = os.path.join(pose_folder, timestamp+".json")
            pose2file = os.path.join(pose_folder, nexttimestamp+".json")

            if os.path.exists(pose1file) and os.path.exists(pose2file):
                dst_file = os.path.join(dst_folder, f)
                #if not os.path.exists(dst_file):
                pcd_restore.pcd_restore(os.path.join(src_folder, f), \
                                       os.path.join(dst_folder, f), \
                                       os.path.join(pose_folder, timestamp+".json"), \
                                       os.path.join(pose_folder, nexttimestamp+".json"), \
                                       timestamp)                                        
                # else:
                #     print("output file exists")
            else:
                print("pose file does not exist", timestamp, nexttimestamp)
    

def calib_motion_compensate(output_path): #, extrinsic_calib_path):

    if os.path.exists(os.path.join(output_path, "intermediate", "calib_motion_compensated")):
        os.system("mv "+output_path+"/intermediate/calib_motion_compensated "+output_path+"/intermediate/calib_lidar_transform")

    dst_folder = os.path.join(output_path, "intermediate", "calib_lidar_transform")
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    src_folder = os.path.join(output_path, "intermediate", "lidar", "aligned")


    #static_calib_camera = {}
    #static_calib_aux_camera = {}
    for camera in camera_list:
        prepare_dirs(os.path.join(output_path, "intermediate", "calib_lidar_transform", "camera",  camera))

        #with open(os.path.join(extrinsic_calib_path,'camera',camera+".json")) as f:
        #    static_calib_camera[camera] = json.load(f)
        
        prepare_dirs(os.path.join(output_path, "intermediate", "calib_lidar_transform", "aux_camera",  camera))

        #with open(os.path.join(extrinsic_calib_path,'aux_camera',camera+".json")) as f:
        #    static_calib_aux_camera[camera] = json.load(f)
        


    files = os.listdir(src_folder)
    files.sort()

    pose_folder = os.path.join(output_path, "intermediate", "ego_pose", "aligned")

    camera_in_order = ['rear','rear_left','front_left','front', 'front_right','rear_right']

    with Bar('compensating motion for calib', max=len(files)) as bar:
        for f in files:
            bar.next()
            timestamp = os.path.splitext(f)[0]
            nexttimestamp = timestamp_add(timestamp, 100)

            pose1file = os.path.join(pose_folder, timestamp+".json")
            pose2file = os.path.join(pose_folder, nexttimestamp+".json")

            if os.path.exists(pose1file) and os.path.exists(pose2file):

                with open(pose1file) as f:
                    pose1 = pcd_restore.formatpose(json.load(f))
                with open(pose2file) as f:
                    pose2  = pcd_restore.formatpose(json.load(f))

                # translate = [float(pose2['x'])-float(pose1['x']), 
                #              float(pose2['y'])-float(pose1['y']), 
                #              float(pose1['z'])-float(pose2['z'])]  # lidar start -> lidar end            
                # rotation = [float(pose2['pitch'])- float(pose1['pitch']), 
                #             float(pose2['roll']) - float(pose1['roll']), 
                #             float(pose2['azimuth'])  - float(pose1['azimuth'])] #lidar start -> lidar end

                delta = pcd_restore.utm_translate(pose1, pose2)

                # euler angles cannot be subtracted directly
                # but roll and pitch are near zero,
                # this cause little error.

                azimuth_delta = pose2["azimuth"] - pose1["azimuth"]

                if azimuth_delta > math.pi:
                    azimuth_delta -= math.pi * 2
                elif azimuth_delta < -math.pi:
                    azimuth_delta += math.pi * 2

                # because our lidar have azimuth rotated by pi, relative to imu/ego frame.
                # thus the pitch and roll are reversed in diretion.
                pitch = - (pose2["pitch"] - pose1["pitch"])
                roll  = - (pose2["roll"] - pose1["roll"])
                
                translate = delta[0:3]
                rotation = [pitch, roll, azimuth_delta]

                #print(translate, rotation)
                translate_step = - np.array(translate)/6
                rotation_step = - np.array(rotation)/6

                for i in range(6):
                    lidar_0_to_lidar_c = pcd_restore.euler_angle_to_rotate_matrix(rotation_step*i,translate_step*i)
                    
                    
                    #camera
                    #extrinsic = np.matmul(np.reshape(np.array(static_calib_camera[camera_in_order[i]]['extrinsic']),(4,4)), lidar_0_to_lidar_c)

                    calib = {
                        'lidar_transform': np.reshape(lidar_0_to_lidar_c,(-1)).tolist(),
                        #'intrinsic': static_calib_camera[camera_in_order[i]]['intrinsic']
                    }

                    #print(calib)
                    with open(os.path.join(output_path,"intermediate", "calib_lidar_transform",'camera',camera_in_order[i], timestamp+".json"), 'w') as f:
                        json.dump(calib, f, indent=2, sort_keys=True)


                    #infrared camera
                    #extrinsic = np.matmul(np.reshape(np.array(static_calib_aux_camera[camera_in_order[i]]['extrinsic']),(4,4)), lidar_0_to_lidar_c)

                    calib = {
                        'lidar_transform': np.reshape(lidar_0_to_lidar_c,(-1)).tolist(),                        
                    }

                    #print(calib)
                    with open(os.path.join(output_path,"intermediate", "calib_lidar_transform",'aux_camera',camera_in_order[i], timestamp+".json"), 'w') as f:
                        json.dump(calib, f, indent=2, sort_keys=True)
            else:
                print("pose file does not exist", timestamp, nexttimestamp)


#path should be abs path.
#
if __name__ == "__main__":

        parser = argparse.ArgumentParser(description='Preprocess dataset. walk subfolders of `data_folder` processing them.')
        parser.add_argument('func', type=str, default='all', help='functions to run: all, rectify, restore_camera, restore_lidar, generate_ego_pose, align, align_radar, calib_motion_compensate, generate_dataset')
        parser.add_argument('camera_calibration_folder', type=str,  help='camera intrinsic calibration')
        parser.add_argument('extrinsic_calibration_folder', type=str, help='lidar-camera calibration')
        parser.add_argument('data_folder', type=str, help='root data folder')
        parser.add_argument('--sub_folder', type=str, help='sub_folder')
        parser.add_argument('--lidar_format', type=str, default='aligned', choices=['restored', 'aligned'], help="use restored lidar or not")
        parser.add_argument('--sub_actions', type=str, default='', help="sub actions, depend on `func`")
        parser.add_argument('--time_slots', type=str, default='000,500', help="for generate dataset")
        parser.add_argument('--hz', type=str, default='2hz', help="for generate dataset")


        args = parser.parse_args()


        print(args)

        func = args.func
        intrinsic_calib_path = os.path.abspath(args.camera_calibration_folder)        
        extrinsic_calib_path = os.path.abspath(args.extrinsic_calibration_folder)
        raw_data_root_path = os.path.abspath(args.data_folder)
        


        savecwd = os.getcwd()
        
        if args.sub_folder:
            subfolders = [args.sub_folder]
        else:
            subfolders = os.listdir(raw_data_root_path)
            subfolders.sort()
        
        
        for f in subfolders:
            os.chdir(savecwd)
            print(f)

            raw_data_path = os.path.join(raw_data_root_path, f)
            if os.path.isdir(raw_data_path):
                if f.endswith("_preprocessed"):
                    continue

                if f.endswith("bagfile"):
                    continue

                output_path = os.path.join(raw_data_root_path, f + "_preprocessed")
                
                if os.path.exists(output_path) and func=='all':
                    continue

                if func == "restore_camera" or func=="all":
                    rectify_cameras(intrinsic_calib_path, raw_data_path, output_path)

                if func == 'color_infrared_image' or func == 'all':
                    color_infrared_image(raw_data_path, output_path)

                if func == "generate_ego_pose" or func=="all":
                    generate_pose(raw_data_path, output_path)

                if func == "align" or func=="all":
                    align(raw_data_path, output_path)

                if func == 'align_radar':
                    align_radar(raw_data_path, output_path)

                # restore shoulb be after aligned
                if  func == "restore_lidar" or (func =="all" and (args.lidar_format == "restored")):
                    lidar_pcd_restore(output_path)
                
                if func == "calib_motion_compensate" or (func =="all" and (args.lidar_format == "restored")):
                    calib_motion_compensate(output_path)
                
                if func == "generate_dataset":
                    dataset_name = "dataset_2hz"
                    timeslots = "000,500"
                    generate_dataset(extrinsic_calib_path,  os.path.join(output_path, dataset_name), timeslots.split(","), args.lidar_format, args.sub_actions)

                if func == "generate_dataset_10hz":
                    dataset_name = "dataset_10hz"
                    generate_dataset_10hz(extrinsic_calib_path,  os.path.join(output_path, dataset_name), args.lidar_format, args.sub_actions)

                if func == "generate_dataset_xhz":
                    if args.hz and args.time_slots:
                        dataset_name = "dataset_"+args.hz
                        timeslots = args.time_slots
                        generate_dataset(extrinsic_calib_path,  os.path.join(output_path, dataset_name), timeslots.split(","), args.lidar_format, args.sub_actions)

