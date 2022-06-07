import os

def rename(file_list):
    for file in file_list:
        file_oldname = os.path.join(path_dir, file)
        file_new_name = os.path.join(path_dir, file.replace(" ","_"))
        print(file_oldname,file_new_name)
        os.rename(file_oldname,file_new_name)
    print("Done")

path_dir = '/home/kdh/jolsul/HandWriteFont_BE/handwritefont_be/model/data_example/kor/ttf_25/'
file_list = os.listdir(path_dir)

rename(file_list)