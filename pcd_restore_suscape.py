
import sys
import os
import json
import pcd_restore

raw_data_root_path = "~/nas"


# if __name__ == "__main__":
#     pcd_restore("/home/lie/nas/2021-09-13/2021-09-13-08-39-11_preprocessed/intermediate/lidar/aligned/1631523695.000.pcd",
#                 "/home/lie/nas/2021-09-13/2021-09-13-08-39-11_preprocessed/intermediate/lidar/restored/1631523695.000.pcd",
#                 "/home/lie/nas/2021-09-13/2021-09-13-08-39-11_preprocessed/intermediate/ego_pose/aligned/1631523695.000.json",
#                 "/home/lie/nas/2021-09-13/2021-09-13-08-39-11_preprocessed/intermediate/ego_pose/aligned/1631523695.100.json",
#                 "1631523695.000")
#
# {'scene': 'turn right, red light,child on road', 'folder': '2021-08-31/2021-08-31-01-51-50_preprocessed/dataset_2hz', 'starttime': '1630374860', 'seconds': '20'}

def timestamp_add(ts, delta_ms):
    [s,ms] = ts.split(".")
    s = int(s)
    ms = int(ms)
    new_ms = ms+delta_ms    
    new_s = s + (new_ms // 1000)
    new_ms %= 1000
    return str(new_s)+"." + "{:03d}".format(new_ms)

    
if __name__ == "__main__":
    scene_path = sys.argv[1]

    with open(os.path.join(scene_path, 'desc.json')) as f:
        desc = json.load(f)


    raw_data_folder = os.path.join(raw_data_root_path, desc['folder'], "..", "intermediate")
    
    
    frames = os.listdir(os.path.join(scene_path, 'lidar'))

    for f in frames:
        timestamp = os.path.splitext(f)[0]
        aligned = os.path.join(raw_data_folder, 'lidar', 'aligned', f)
        restored = os.path.join(raw_data_folder, 'lidar', 'restored', f)
        egopose_begin = os.path.join(raw_data_folder, 'ego_pose', 'aligned', timestamp+".json")
        egopose_end = os.path.join(raw_data_folder, 'ego_pose', 'aligned', timestamp_add(timestamp, 100)+".json")
        #print(aligned, restored, egopose_begin, egopose_end, timestamp)
        pcd_restore.pcd_restore(aligned, restored, egopose_begin, egopose_end, timestamp)
    