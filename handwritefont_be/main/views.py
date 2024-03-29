from rest_framework.generics import RetrieveUpdateAPIView,RetrieveAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import permission_classes

from .models import Font, preview
from .serializers import FontSerializer,FontLookAroundSerializer,FontPublicSerializer, NameUniqueCheckSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from os import mkdir
from PIL import Image
from pathlib import Path
from django.conf import settings

import os
import subprocess
import cv2
import numpy as np

# Model Import
import json
from pathlib import Path
from PIL import Image
import torch
from sconf import Config
from torchvision import transforms
from base.dataset import read_font, render
from base.utils import save_tensor_to_image, load_reference
from DM.models import Generator
from model.inference import infer_DM


transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# Png2Svg
from .png2svg import png2svg

# Create your views here.
words = ['값', '같', '곬', '곶', '깎', '넋', '늪', '닫', '닭', '닻', '됩', '뗌', '략', '몃', '밟', '볘', '뺐',
            '뽈', '솩', '쐐', '앉', '않', '얘', '얾', '엌', '옳', '읊', '죡', '쮜', '춰', '츄', '퀭', '틔', '핀', '핥', '훟']

#데이터 전처리 함수(crop → resize → padding)
def tight_crop_image(img, verbose=False, resize_fix=False):
    full_white = 255
    col_sum = np.where(np.sum(full_white-img, axis=0) > 1000) # axis가 0이면 열 단위의 합, 1이면 행 단위의 합
    row_sum = np.where(np.sum(full_white-img, axis=1) > 1000) 
    y1, y2 = row_sum[0][0], row_sum[0][-1]
    x1, x2 = col_sum[0][0], col_sum[0][-1]
    cropped_image = img[y1:y2, x1:x2]
    cropped_image_size = cropped_image.shape

    if verbose:
        print("Img : ",img)
        print("Full White : ", full_white)
        print("NP Sum axis=0 : ", np.sum(full_white-img, axis=0))
        print("NP Sum axis=1 : ", np.sum(full_white-img, axis=1))
        print("Col Sum : ", col_sum)
        print("Row Sum : ", row_sum)
        print("y1, y2 : ", y1, y2)
        print("x1, x2 : ", x1, x2)
        print('(left x1, top y1):', (x1, y1))
        print('(right x2, bottom y2):', (x2, y2))
        print('cropped_image size:', cropped_image_size)

    if type(resize_fix) == int:
        origin_h, origin_w = cropped_image.shape
        if origin_h > origin_w:
            resize_w = int(origin_w * (resize_fix / origin_h))
            resize_h = resize_fix
        else:
            resize_h = int(origin_h * (resize_fix / origin_w))
            resize_w = resize_fix
        if verbose:
            print('resize_h:', resize_h)
            print('resize_w:', resize_w, \
                  '[origin_w %d / origin_h %d * target_h]' % (origin_w, origin_h))
        
        # resize
        array2pillow = Image.fromarray(cropped_image)
        cropped_image = array2pillow.resize((resize_w,resize_h))
        cropped_image = np.array(cropped_image)
        # cropped_image = normalize_image(cropped_image).astype(np.uint8)
        cropped_image_size = cropped_image.shape
        if verbose:
            print('resized_image size:', cropped_image_size)
        
    elif type(resize_fix) == float:
        origin_h, origin_w = cropped_image.shape
        resize_h, resize_w = int(origin_h * resize_fix), int(origin_w * resize_fix)
        if resize_h > 120:
            resize_h = 120
            resize_w = int(resize_w * 120 / resize_h)
        if resize_w > 120:
            resize_w = 120
            resize_h = int(resize_h * 120 / resize_w)
        if verbose:
            print('resize_h:', resize_h)
            print('resize_w:', resize_w)
        
        # resize
        array2pillow = Image.fromarray(cropped_image)
        cropped_image = array2pillow.resize((resize_w,resize_h))
        cropped_image = np.array(cropped_image)
        cropped_image_size = cropped_image.shape
        if verbose:
            print("Cropped Image : ",cropped_image)
            print('resized_image size:', cropped_image_size)
    
    return cropped_image

def add_padding(img, image_size=128, verbose=False, pad_value=None):
    height, width = img.shape
    if not pad_value:
        pad_value = img[0][0]
    if verbose:
        print('original cropped image size:', img.shape)
    
    # Adding padding of x axis - left, right
    pad_x_width = (image_size - width) // 2
    pad_x = np.full((height, pad_x_width), pad_value, dtype=np.uint8)
    img = np.concatenate((pad_x, img), axis=1)
    img = np.concatenate((img, pad_x), axis=1)
    
    width = img.shape[1]

    # Adding padding of y axis - top, bottom
    pad_y_height = (image_size - height) // 2
    pad_y = np.full((pad_y_height, width), pad_value, dtype=np.uint8)
    img = np.concatenate((pad_y, img), axis=0)
    img = np.concatenate((img, pad_y), axis=0)
    
    # Match to original image size
    width = img.shape[1]
    if img.shape[0] % 2:
        pad = np.full((1, width), pad_value, dtype=np.uint8)
        img = np.concatenate((pad, img), axis=0)
    height = img.shape[0]
    if img.shape[1] % 2:
        pad = np.full((height, 1), pad_value, dtype=np.uint8)
        img = np.concatenate((pad, img), axis=1)

    if verbose:
        print('final image size:', img.shape)
    
    return img

def centering_image(img, image_size=128, verbose=False, resize_fix=False, pad_value=None):
    if not pad_value:
        pad_value = img[0][0]
    cropped_image = tight_crop_image(img, verbose=verbose, resize_fix=resize_fix)
    centered_image = add_padding(cropped_image, image_size=image_size, verbose=verbose, pad_value=pad_value)

    return centered_image

def template2png(load_file, font_obj):

    load_path = Path(load_file)
    save_dir = Path(str((settings.MEDIA_ROOT)) + str(Path('/{0}/{1}/ref_glyphs/{2}'.format(font_obj.owner.email,font_obj.name,font_obj.name))))
    save_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(load_path)
    imgGray = img.convert('L')
    p2a = np.array(imgGray)
    
    th = cv2.adaptiveThreshold(p2a,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,127,5)
    template_cropped = tight_crop_image(th, verbose=False, resize_fix=False)

    template_cropped = Image.fromarray(template_cropped)

    template_cropped.save(load_path)
    template_resize = template_cropped.resize((1270, 755))
    x,y = 4,52
    letterN = 1

    while letterN <= 36:
        croppedImage = template_resize.crop((x, y, x + 130, y + 130))
        croppedImage = croppedImage.resize((128, 128))
        
        pillow2array = np.array(croppedImage)

        th = cv2.adaptiveThreshold(pillow2array,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,127,5)
        centeredImage = centering_image(th, resize_fix=1.3)
        output = Image.fromarray(centeredImage)
        save_path = save_dir / f"{words[letterN - 1]}.jpg" 
        output.save(save_path)

        x = x + 141

        if letterN == 9:
            x,y = 4,241
        elif letterN == 18:
            x,y = 4,427
        elif letterN == 27:
            x,y = 4,616

        letterN = letterN + 1
    return save_dir.parent

# Inference Model
def inference(ref_path):
    model_path = str(settings.MODEL_ROOT)
    weight_path = model_path + "/result/ttf_25/checkpoints/last.pth"  # path to weight to infer
    decomposition = model_path + "/data/kor/decomposition_DM.json"

    n_heads = 3
    n_comps = 68
    ###############################################################

    # building and loading the model (not recommended to modify)
    cfg = Config(model_path + "/cfgs/DM/default.yaml")
    decomposition = json.load(open(decomposition))

    gen = Generator(n_heads=n_heads, n_comps=n_comps).cuda().eval()
    weight = torch.load(weight_path)
    gen.load_state_dict(weight["generator_ema"])

    ###############################################################
    # ref_path = model_path + "/data_example/kor/jpg"
    extension = "jpg"
    ## Comment upper lines and uncomment lower lines to test with ttf files.
    # extension = "ttf"
    ref_chars = "값같곬곶깎넋늪닫닭닻됩뗌략몃밟볘뺐뽈솩쐐앉않얘얾엌옳읊죡쮜춰츄퀭틔핀핥훟"
    ###############################################################
    ref_dict, load_img = load_reference(ref_path, extension, ref_chars)

    ###############################################################
    gen_chars = json.load(open(model_path + "/data/kor/gen_all_chars.json"))     # characters to generate
    # gen_chars = json.load(open(model_path + "/data/kor/gen_chars.json"))     # characters to generate
    # gen_chars = "좋은하루되세요"  # characters to generate
    save_dir = str(os.path.join(Path(ref_path).parent, 'gen_glyphs'))
    batch_size = 32
    ###############################################################
     
    infer_DM(gen, save_dir, gen_chars, ref_dict, load_img, decomposition, batch_size)

    return save_dir

@permission_classes([IsAuthenticatedOrReadOnly])
class FontListView(ListCreateAPIView):
    queryset = Font.objects.all().order_by('-created_date').exclude(ttf_file="", public=False)
    serializer_class = FontSerializer

    def post(self, request, *args, **kwargs):
        request.data['name'] = request.data['name'].replace(" ","_")
        output =  self.create(request, *args, **kwargs)
        obj = Font.objects.get(name = request.data['name'])
        load_file = str((settings.BASE_DIR)) + str(Path(obj.file.url)).replace("%40","@")
        template_path = template2png(load_file=load_file, font_obj=obj)
        
        print("Inference Start")
        png_path = inference(template_path)
        png_path = os.path.join(Path(png_path), obj.name)
        print("Inference End")
        
        print("Png 2 Svg Start")
        svg2font = png2svg(png_path)
        print("Png 2 Svg End")
        
        print("Svg 2 Ttf Start")
        # print(svg2font)
        # print(str(os.path.join(Path(svg2font).parent, 'output')))
        # os.system('/usr/bin/fontforge svgs2ttf font.json' + " " + str(svg2font) + " " + str(os.path.join(Path(svg2font).parent, 'output')) + " " + obj.name)
        # svg2ttf('font.json', svgs2font, str(os.path.join(Path(svg2font).parent, 'output')), obj.name)
        subprocess.run(['/usr/bin/fontforge','-script','/home/dice/HandWriteFont_BE/handwritefont_be/main/svgs2ttf','/home/dice/HandWriteFont_BE/handwritefont_be/main/font.json',svg2font,str(os.path.join(Path(svg2font).parent.parent, 'fonts')), obj.name ])
        # subprocess.run(['sh','/home/kdh/jolsul/HandWriteFont_BE/handwritefont_be/main/test.sh'])
        # subprocess.run(['/usr/bin/fontforge','-script','/home/dice/HandWriteFont_BE/handwritefont_be/main/svgs2ttf','/home/dice/HandWriteFont_BE/handwritefont_be/main/font.json', '/home/dice/HandWriteFont_BE/handwritefont_be/media/admin@admin.com/Test7/gen_glyphs/svg_glyphs','/home/dice/HandWriteFont_BE/handwritefont_be/media/admin@admin.com/Test7/gen_glyphs/output', 'success'])
        print("Svg 2 Ttf End")
        
        obj.ttf_file = str(os.path.join(Path(svg2font).parent.parent, 'fonts')).replace('/home/dice/HandWriteFont_BE/handwritefont_be/','http://218.150.183.52:8000/') +"/"+obj.name + '.ttf'
        obj.woff_file = str(os.path.join(Path(svg2font).parent.parent, 'fonts')).replace('/home/dice/HandWriteFont_BE/handwritefont_be/','http://218.150.183.52:8000/') +"/"+obj.name + '.woff'
        for ch in "안녕하세요당신의폰트입니다":
            target = preview.objects.create(name=ch, path = str(Path(svg2font)).replace('/home/dice/HandWriteFont_BE/handwritefont_be/','http://218.150.183.52:8000/')+"/"+ch+".svg")
            obj.previews.add(target)
        obj.save()
        return output

class FontView(RetrieveUpdateAPIView):
    queryset = Font.objects.all()
    serializer_class = FontSerializer

class NameUniqueCheck(CreateAPIView):
    serializer_class = NameUniqueCheckSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            return Response(data={'detail':'You can use this Name :)'}, status=status.HTTP_200_OK)
        else:
            detail = dict()
            detail['detail'] = 'This Name is alreay Used :('
            return Response(data=detail, status=status.HTTP_200_OK)

@api_view(['GET'])
def fontview(request):
    queryset = Font.objects.filter(public=True).exclude(ttf_file="")
    name = request.query_params.get('name')
    if name is not None:
        queryset = queryset.get(name=name, public=True)
        serializer = FontLookAroundSerializer(queryset, context={'request':request}).data
    else:
        serializer = FontLookAroundSerializer(queryset,many=True, context={'request':request}).data
    return Response(serializer)
