import cv2
import potrace
import os
from pathlib import Path
from svg.file import SVGFileV2
from svg.basic import draw_path

def path_potrace(data):
    """get path from raster image data

    Args:
        data (array): M*N array, white and black image
    """

    # Create a bitmap from the array
    bmp = potrace.Bitmap(data)

    # Trace the bitmap to a path
    path = bmp.trace()

    # print('len(path)=', len(path))
    parts = []
    for curve in path:
        fs = curve.start_point
        parts.append("M%f,%f" % (fs.x, fs.y))
        for segment in curve.segments:
            if segment.is_corner:
                a = segment.c
                parts.append("L%f,%f" % (a.x, a.y))
                b = segment.end_point
                parts.append("L%f,%f" % (b.x, b.y))
            else:
                a = segment.c1
                b = segment.c2
                c = segment.end_point
                parts.append("C%f,%f %f,%f %f,%f" % (a.x, a.y, b.x, b.y, c.x, c.y))
        parts.append("z")

    return "".join(parts)


def path_potrace_jagged(data):
    """get path from raster image data

    Args:
        data (array): M*N array, white and black image
    """

    # Create a bitmap from the array
    bmp = potrace.Bitmap(data)

    # Trace the bitmap to a path
    path = bmp.trace()
    parts = []
    for curve in path:
        parts.append("M")
        for point in curve.decomposition_points:
            parts.append(" %f,%f" % (point.x, point.y))
        parts.append("z")
    return "".join(parts)


def png2svg(load_path):
    save_path = Path(os.path.join(Path(load_path).parent,'svg_glyphs'))
    save_path.mkdir(parents=True, exist_ok=True)
    file_list = os.listdir(load_path)

    for file in file_list:
        target_path = os.path.join(load_path, file)
        img = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE)
        svg = SVGFileV2(os.path.join(save_path,file.split('.')[0] + '.svg'), W=img.shape[1], H=img.shape[0])
        path = path_potrace(img)
        svg.draw(draw_path(path, color='none', fillColor='black', fill_rule='evenodd'))

    return save_path

