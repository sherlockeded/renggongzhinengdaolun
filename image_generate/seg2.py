from __future__ import print_function

import numpy as np
import scipy.ndimage as ndi
from skimage import measure,color
from skimage import filters
import matplotlib.pyplot as plt
from skimage import morphology
from skimage import io,transform,draw,img_as_ubyte

#编写一个函数来生成原始二值图像
def line_detect(dir,length=50,min_width=250,margin_col=20):
    gray = io.imread(dir, as_grey=True)
    img = io.imread(dir)
    if (gray.shape[0] * gray.shape[1] < 360000):
        gray = transform.rescale(gray,2)
        img = transform.rescale(img, 2,preserve_range=True)
        img = np.array(img, np.uint8)
        #img=img_as_ubyte(transform.resize(img, 2))
    thresh = filters.threshold_otsu(gray)  # 返回一个阈值
    data = (gray >= thresh) * 1.0  # 根据阈值进行分割
    unique, counts = np.unique(data, return_counts=True)

    if (unique[0] == 1):
        if (counts[0] > counts[1]):
            gray= 1 - gray
    elif (unique[1] == 1):
        if (counts[1] > counts[0]):
            gray = 1 - gray
    kernel = morphology.disk(3)
    # gray =morphology. closing(gray, kernel)
    gray2 = morphology.dilation(gray, kernel)
    thresh = filters.threshold_otsu(gray2)  # 返回一个阈值
    datat = (gray2 >= thresh) * 1.0  # 根据阈值进行分割
    labels = measure.label(datat, connectivity=2, background=-1)  # 8连通区域标记]

    row = labels.shape[0]
    col = labels.shape[1]
    unique, counts = np.unique(labels, return_counts=True)
    background = []
    copy = counts.copy()
    background1 = np.argmax(counts)
    background.append(unique[background1])
    copy[background1] = 0
    background2_count = np.max(copy)
    if (background2_count > counts[background1] / 3):
        background2 = np.argmax(copy)
        background.append(unique[background2])
    lines = []
    colors=[]
    dst = np.zeros([row, col, 3])
    for bgn in range(len(background)):
        bg=background[bgn]
        place = np.where(labels == bg)
        min_r = min(place[0])
        max_r = max(place[0])
        le=len(place[0])
        if(img.shape[2]==4):
            img = img[:,:,0:3]
        a1=place[0][int(le/2)]
        a2=place[1][int(le/2)]
        b1=place[0][int(le/3)]
        b2=place[1][int(le/3)]
        c1= place[0][int(2*le/3)]
        c2= place[1][int(2*le/3)]
        rr,gg,bb=img[a1,a2,:]/3+img[b1,b2,:]/3+img[c1,c2,:]/3
        rgb=[int(rr),int(gg),int(bb)]
        colors.append(rgb)
        max_r = min(max_r, row - length)
        for r in range(0, max_r, length):  # 获取行连通区域`
            temparr = np.uint8(datat[r:r + length, :])
            labelsr = measure.label(temparr, connectivity=1, background=-1)  # 行连通区域标记

            minn = []
            # for i in range(50):
            # place1 = np.where(labelsr[i] == 1)
            # minn.append(place1)
            dst[r:r + length, :] = color.label2rgb(np.array(labelsr))
            uniquer, countsr = np.unique(labelsr, return_counts=True)
            if (len(uniquer) == 1):  # 只有一个区域
                lines.append([r, margin_col, col - 1-margin_col,bgn,0])
                continue
            backgroundrs = []
            background1r = np.argmax(countsr)
            backgroundrs.append(background1r)
            copyr = countsr.copy()
            copyr[background1r] = 0
            background2r = np.argmax(copyr)
            backgroundrs.append(background2r)

            for backgroundr in backgroundrs:  # 对于每个行连通区域
                if (countsr[backgroundr] < length * min_width):
                    continue
                labelr_bg = uniquer[backgroundr]
                place_bgr = np.where(labelsr == labelr_bg)  # 行连通区
                va=np.var(gray[place_bgr])
                me = np.mean(gray[place_bgr])
                if(va>0.08):
                    continue
                r1 = place_bgr[0][3000] + r
                c1 = place_bgr[1][3000]
                if (labels[r1][c1] != bg):
                    continue
                c_bg_min = min(place_bgr[1])
                c_bg_max = max(place_bgr[1])
                place_other = np.where(labelsr[:,c_bg_min:c_bg_max] != labelr_bg)  # 行非连通区
                if len(place_other[0]) == 0:  # 没有其他杂质
                    lines.append([r, c_bg_min+margin_col, c_bg_max - c_bg_min-margin_col,bgn,va])
                    continue
                c_other_min = min(place_other[1]) + c_bg_min
                c_other_max = max(place_other[1]) + c_bg_min
                length1 = c_other_min - c_bg_min
                flag = 0
                if (length1 > min_width):
                    flag = 1
                    lines.append([r, c_bg_min+margin_col, length1-margin_col,bgn,va])
                length2 = c_bg_max - c_other_max
                if (length2 > min_width):
                    flag = 1
                    lines.append([r, c_other_max+margin_col, length2-margin_col,bgn,va])
                if flag == 1 or c_bg_min > int(col / 2) or c_bg_max < int(col / 2):
                    continue

                place_other_left = np.where(labelsr[:, c_bg_min:int(col / 2)] != labelr_bg)  # 也许中间才是空白的
                if len(place_other_left[0]) != 0:  # 没有其他杂质
                    c_other_min2 = max(place_other_left[1]) + c_bg_min
                else:
                    continue

                place_other_right = np.where(labelsr[:, int(col / 2):c_bg_max] != labelr_bg)
                if len(place_other_right[0]) != 0:  # 没有其他杂质
                    c_other_max2 = min(place_other_right[1]) + int(col / 2)
                else:
                    continue
                lengthother = c_other_max2 - c_other_min2
                if (c_other_max2 - c_other_min2 > min_width):
                    lines.append([r, c_other_min2+margin_col, lengthother-margin_col,bgn,va])
    for i in range(len(lines)):
        lin = lines[i]
        print(lines[i])
        # rr, cc = draw.line( lin[0] + length , lin[1],  lin[0] + length , lin[2] + lin[1])
        #rr, cc = draw.rectangle((lin[0], lin[1]), end=(lin[0] + length, lin[2] + lin[1]))
        #dst[rr, cc] = [255, 255, 255]
        # cv2.line(dst, ( lin[0] + length , lin[2] + lin[1]), (lin[0] + length , lin[1]), [0,0,0])
    # dst=color.label2rgb(labels)  #根据不同的标记显示不同的颜色
    print('line number:', len(lines))  # 显示连通区域块数(从0开始标记)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    ax1.imshow(gray, interpolation='nearest')
    ax1.axis('off')
    ax2.imshow(dst, interpolation='nearest')
    ax2.axis('off')

    fig.tight_layout()

    plt.savefig('plot123.png')  # 指定分辨率保存
    plt.show()
    return lines,img,colors