# Visdom须先启动服务
# 启动服务的命令为：
# python -m visdom.server

import numpy as np
from PIL import Image
import visdom

vis = visdom.Visdom(env='test2')  # env为区别不同的Visdom对象的标签

# vis.line的制作
x = np.arange(1, 30, 0.01)
y = np.sin(x)
vis.line(X=x, Y=y, win='sinx', opts={'title': 'y=sin(x)'})

# image的显示，需要先转换为np数组
img = Image.open('data\\test.jpg')
img = np.asarray(img).transpose([2, 0, 1])  # 转换为CxHxW的格式
vis.image(img, win='dilireba')

# svg可以直接显示
vis.svg(svgfile='data\\test.svg', win='svg_test')

x = np.arange(1, 30, 0.01)
y = np.sin(x)
vis.bar(X=y, Y=x, win='bar_test')  # bar图的特点，X表示bar的高度，Y表示每个bar的标签

x = np.array([0.3, 0.4, 0.6])
vis.bar(X=x, win='bar_test2', opts={'rownames': ['a', 'b', 'c']})