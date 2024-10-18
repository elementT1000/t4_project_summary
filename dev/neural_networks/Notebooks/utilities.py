import os

#These access environment variables that must be set up on your system
home = os.environ["T4_DIR"]
downloads = os.environ["DOWNLOADS"]

config_dict = [
    {'ANTERIOR': [r'Anterior_Frontal\af_config.yaml', ["af"]]},
    {'POSTERIOR': [r'Posterior_Frontal\pf_config.yaml', ["pf"]]},
    {'SAGITTAL': [r'Sagittal\sag_config.yaml', ["sl", "sr"]]}
]

def get_value(key):
    for i in config_dict:
        if key in i:
            return i[key]
        

def list_videos(dir, plane_specifier):
    list_of_files = os.listdir(dir)

    full_path_list = []
    for i in list_of_files:
        if (i.endswith(".mp4")) or (i.endswith(".MP4")):
            name = i.split('_')
            if any(substring in name for substring in plane_specifier):
                i_var = dir + '\\' + i
                full_path_list.append(i_var)

    return full_path_list
    