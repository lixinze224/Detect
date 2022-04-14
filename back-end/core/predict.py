import cv2

def predict(dataset, model, ext):
    global img_y
    #x是文件临时保存的相对路径
    x = dataset[0].replace('\\', '/')
    file_name = dataset[1]
    # x = cv2.imread(x) 读取图片
    img_y, image_info = model.detect(x)
    #print("img_y = ",img_y)
    cv2.imwrite('./tmp/draw/{}.{}'.format(file_name, ext), img_y)
    # if cv2.imwrite('./tmp/draw/{}.{}'.format(file_name, ext), img_y):
    #     raise Exception('保存图片时出错.Error saving thepicture.')
    return image_info
