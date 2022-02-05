import os
import pathlib
import re
import shutil
import sys


def make_file_list(path, protected_dirs):
    file_list = []

    def __handler(path, protected_dirs):
        p = pathlib.Path(path)
        if p not in protected_dirs:
            file_list.append(p)
            for item in p.iterdir():
                if item.is_file():
                    file_list.append(item)
                else:
                    __handler(item, protected_dirs)

    __handler(path, protected_dirs)
    return file_list


def to_latin(name):
    """Convert all symbols to latin"""
    symbols = (u"іїєабвгдеёжзийклмнопрстуфхцчшщъыьэюяІЇЄАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
               u"iieabvgdeejzijklmnoprstufhzcss_y_euaIIEABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")

    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    translated_name = name.translate(tr)
    translated_name = re.sub("[^A-Za-z0-9]", "_", translated_name)
    return translated_name


def normalize(element):
    element_name = element.name
    path = str(element)[:-len(element_name)]
    if element.is_file():
        element_suffix = element.suffix
        element_name = element_name.rsplit(element_suffix)
        translated_name = to_latin(element_name[0])
        name = f'{translated_name}{element_suffix}'
    else:
        name = to_latin(element_name)
    normalized_name = path + name
    return normalized_name


def remove_empty_dirs(path_abs, protected_dirs):
    walk = list(os.walk(path_abs))
    for path, _, _ in walk[::-1]:
        if pathlib.Path(path) not in protected_dirs:
            if len(os.listdir(path)) == 0:
                os.rmdir(path)


def sort_files(dir_path):
    file_types = {}
    key_types = ['images', 'document', 'audio', 'video', 'archives', 'unknown_file']
    protected_dirs = []
    for key in key_types:
        file_types[key] = []
    known_extensions = set()
    unknown_extensions = set()
    for new_fold in key_types:
        protected_path = f'{str(dir_path)}\\{new_fold}'
        protected_dirs.append(pathlib.Path(protected_path))
        if not os.path.exists(f'{str(dir_path)}\\{new_fold}'):
            os.makedirs(f'{str(dir_path)}\\{new_fold}')
    collections = make_file_list(dir_path, protected_dirs)
    if len(collections) > 0:
        for element in collections:
            normalized_name = normalize(element)
            try:
                os.rename(element, normalized_name)
            except FileExistsError:
                print(f'File with name {normalized_name} already exists, please try enter another name')
            normalized_name = pathlib.Path(normalized_name)
            if not normalized_name.is_dir():
                if normalized_name.suffix in ['.jpeg', '.png', '.jpg', '.svg']:
                    path_for_images = f"{str(dir_path)}\\images\\{normalized_name.name}"
                    try:
                        os.replace(normalized_name, path_for_images)
                    except FileExistsError:
                        print(f'File with name {path_for_images} already exists, please try enter another name')
                    file_types['images'].append(path_for_images)
                    path_for_images = pathlib.Path(path_for_images)
                    known_extensions.add(path_for_images.suffix)  
                elif normalized_name.suffix in ['.avi', '.mp4', '.mov', '.mkv']:
                    path_for_video = f"{str(dir_path)}\\video\\{normalized_name.name}"
                    try:
                        os.replace(normalized_name, path_for_video)
                    except FileExistsError:
                        print(f'File with name {path_for_video} already exists, please try enter another name')

                    file_types['video'].append(path_for_video)
                    path_for_video = pathlib.Path(path_for_video)
                    known_extensions.add(path_for_video.suffix)

                elif normalized_name.suffix in ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx']:
                    path_for_document = f"{str(dir_path)}\\document\\{normalized_name.name}"
                    try:
                        os.replace(normalized_name, path_for_document)
                    except FileExistsError:
                        print(f'File with name {path_for_document} already exists, please try enter another name')

                    file_types['document'].append(path_for_document)
                    path_for_document = pathlib.Path(path_for_document)
                    known_extensions.add(path_for_document.suffix)

                elif normalized_name.suffix in ['.mp3', '.ogg', '.wav', '.amr']:
                    path_for_audio = f"{str(dir_path)}\\audio\\{normalized_name.name}"
                    try:
                        os.replace(normalized_name, path_for_audio)
                    except FileExistsError:
                        print(f'File with name {path_for_audio} already exists, please try enter another name')

                    file_types['audio'].append(path_for_audio)
                    path_for_audio = pathlib.Path(path_for_audio)
                    known_extensions.add(path_for_audio.suffix)

                elif normalized_name.suffix in ['.zip', '.gz', '.tar']:
                    archive_name = str(normalized_name.name)[:-len(normalized_name.suffix)]
                    archives_dir = f"{str(dir_path)}\\archives\\{archive_name}"
                    path_for_archives = f"{archives_dir}\\{normalized_name.name}"
                    # Creating dirs with archive name
                    if not os.path.exists(archives_dir):
                        os.makedirs(archives_dir)
                    try:
                        # Unpacking archive
                        shutil.unpack_archive(normalized_name, archives_dir)
                        # Delete unzipped file
                        os.remove(normalized_name)
                    except:
                        try:
                            # If we have are problems with unpacking,
                            # than we replace archive to dir by appropriate type
                            os.replace(normalized_name, path_for_archives)
                        except FileExistsError:
                            print(f'File with name {path_for_archives} already exists, please try enter another name')

                    file_types['archives'].append(path_for_archives)
                    path_for_archives = pathlib.Path(path_for_archives)
                    known_extensions.add(path_for_archives.suffix)

                else:
                    path_for_unknown = f"{str(dir_path)}\\unknown_file\\{normalized_name.name}"
                    try:
                        os.replace(normalized_name, path_for_unknown)
                    except FileExistsError:
                        print(f'File with name {path_for_unknown} already exists, please try enter another name')

                    file_types['unknown_file'].append(path_for_unknown)
                    path_for_unknown = pathlib.Path(path_for_unknown)
                    unknown_extensions.add(path_for_unknown.suffix)
    else:
        return print(f'Directory {dir_path} is empty')

    try:
        remove_empty_dirs(dir_path, protected_dirs)
    except Exception as e:
        print(e)

    return file_types, known_extensions, unknown_extensions


if __name__ == '__main__':
    dir_name = sys.argv[1]
    dir_path = pathlib.Path(dir_name)
    try:
        file_types, known_extensions, unknown_extensions = sort_files(dir_path)
    except Exception as e:
        print(e)