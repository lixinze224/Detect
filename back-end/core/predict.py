import cv2
import numpy as np
def predict(dataset, model, ext):
    global img_y
    #x是文件临时保存的相对路径
    x = dataset[0].replace('\\', '/')
    file_name = dataset[1]
    # x = cv2.imread(x) 读取图片
    img_y, image_info = model.detect(x)
    #print("img_y = ",img_y)
    # print(type(img_y))
    file_name = './tmp/draw/{}.{}'.format(file_name, ext)
    if type(img_y) is np.ndarray:
        cv2.imwrite(file_name, img_y)
    else:
        img_y.save(file_name)
    # if cv2.imwrite('./tmp/draw/{}.{}'.format(file_name, ext), img_y):
    #     raise Exception('保存图片时出错.Error saving thepicture.')
    return image_info
