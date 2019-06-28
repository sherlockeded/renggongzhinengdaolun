import os
import numpy as np
import matplotlib.pyplot as plt
from skimage import io,transform,draw,img_as_ubyte
gray = io.imread("/Users/iris/basic_math/background/6.jpg", as_grey=True)
img = io.imread("/Users/iris/basic_math/background/6.jpg")
if (gray.shape[0] * gray.shape[1] < 360000):
    gray = transform.rescale(gray,2)
    img = transform.rescale(img, 2,preserve_range=True)
    img=np.array(img,np.uint8)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
ax1.imshow(gray, interpolation='nearest')
ax1.axis('off')
ax2.imshow(img, interpolation='nearest')
ax2.axis('off')

fig.tight_layout()

plt.savefig('plot123.png')  # 指定分辨率保存
plt.show()