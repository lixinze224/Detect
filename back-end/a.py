from tools.inference import Detector


if __name__ == '__main__':
    
    model = Detector()
    image,image_info = model.detect('tools\inputs\9.jpg')
    print(image_info)
