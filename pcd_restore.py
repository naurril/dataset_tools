

import numpy as np
import math
import json
import os


def euler_angle_to_rotate_matrix(eu, t):
    theta = eu
    # Calculate rotation about x axis
    R_x = np.array([
        [1,       0,              0],
        [0,       math.cos(theta[0]),   -math.sin(theta[0])],
        [0,       math.sin(theta[0]),   math.cos(theta[0])]
    ])

    # Calculate rotation about y axis
    R_y = np.array([
        [math.cos(theta[1]),      0,      math.sin(theta[1])],
        [0,                       1,      0],
        [-math.sin(theta[1]),     0,      math.cos(theta[1])]
    ])

    # Calculate rotation about z axis
    R_z = np.array([
        [math.cos(theta[2]),    -math.sin(theta[2]),      0],
        [math.sin(theta[2]),    math.cos(theta[2]),       0],
        [0,               0,                  1]])

    R = np.matmul(R_y, np.matmul(R_x, R_z))  # zxy order.

    t = t.reshape([-1, 1])
    R = np.concatenate([R, t], axis=-1)
    R = np.concatenate([R, np.array([0, 0, 0, 1]).reshape([1, -1])], axis=0)
    return R


def egocar_to_utm(roll, pitch, yaw, x, y, z):
    return euler_angle_to_rotate_matrix([roll, pitch, yaw], np.array([x, y, z]))


def lidar_to_egocar():
    return euler_angle_to_rotate_matrix([0, 0, math.pi], np.array([0, 0, -0.4]))


def lidar_to_utm(roll, pitch, yaw, x, y, z):
    return np.matmul(egocar_to_utm(roll, pitch, yaw, x, y, z), lidar_to_egocar())



def utm_translate(pose1, pose2):
    translate_utm = [pose2["x"]-pose1["x"],
                     pose2["y"]-pose1["y"],
                     pose2["z"]-pose1["z"],
                     0]  # 0 for vector sub

    #print("utm translate", translate_utm)

    transmatrix = lidar_to_utm(
        pose1["roll"], pose1["pitch"], pose1["azimuth"], pose1['x'], pose1['y'], pose1['z'])

    utm_to_lidar = np.linalg.inv(transmatrix)

    # print('trans matrix', transmatrix)
    # print("inv matrix", utm_to_lidar)

    translate_lidar1 = np.matmul(utm_to_lidar, np.array(
        [pose1['x'], pose1['y'], pose1['z'], 1]))
    translate_lidar2 = np.matmul(utm_to_lidar, np.array(
        [pose2['x'], pose2['y'], pose2['z'], 1]))
    return translate_lidar2 - translate_lidar1
    # return np.matmul(utm_to_lidar, translate_utm)


def formatpose(p):
    p["x"] = float(p['x'])
    p["y"] = float(p['y'])
    p["z"] = float(p['z'])

    p["roll"] = float(p['roll'])*math.pi/180
    p["pitch"] = float(p['pitch'])*math.pi/180
    p["azimuth"] = -float(p['azimuth'])*math.pi/180  # azimuth is left handled angle in degree
    return p


def get_pcd_restore_bin():
    dir = os.path.dirname(__file__)
    return os.path.join(dir, "pcd_restore/build/pcd_restore")


bin_pcd_restore = get_pcd_restore_bin()


def lidar_pose_delta_by_utm_pose(pose1, pose2):
    delta = utm_translate(pose1, pose2)

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

    return [delta[0], delta[1], delta[2], pitch, roll, azimuth_delta ]

def pcd_restore(pcdfile, outputfile, pose1_file, pose2_file, timestamp):
    with open(pose1_file) as f:
        pose1 = formatpose(json.load(f))

    with open(pose2_file) as f:
        pose2 = formatpose(json.load(f))

    delta = utm_translate(pose1, pose2)

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

    #
    # important: pose delta is in point cloud frame.
    # 
    cmd = bin_pcd_restore + " " + pcdfile + " " + outputfile + " " + str(timestamp) + " " +\
        str(delta[0]) + " " + str(delta[1]) + " " + str(delta[2]) + " " +\
        str(roll) + " " +\
        str(pitch) + " " +\
        str(azimuth_delta) + " ZXY"

    #print(cmd)
    os.system(cmd)


if __name__ == "__main__":
    pcd_restore("/home/lie/nas/2021-08-31/2021-08-31-02-28-58_preprocessed/intermediate/lidar/aligned/1630376972.000.pcd",
                "/home/lie/nas/2021-08-31/2021-08-31-02-28-58_preprocessed/intermediate/lidar/restored/1630376972.000.pcd",
                "/home/lie/nas/2021-08-31/2021-08-31-02-28-58_preprocessed/intermediate/ego_pose/aligned/1630376972.000.json",
                "/home/lie/nas/2021-08-31/2021-08-31-02-28-58_preprocessed/intermediate/ego_pose/aligned/1630376972.100.json",
                "1630376972.000")
