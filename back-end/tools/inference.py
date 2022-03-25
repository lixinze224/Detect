import os
import sys
#from this import s

import cv2
import torch
import numpy as np

sys.path.insert(0, '../lib')
from utils import misc_utils, visual_utils, nms_utils
class Detector(object):
    def __init__(self) -> None:
        self.model_dir = 'rcnn_emd_refine'
        self.resume_weights = '40'
        model_root_dir = os.path.join('../model/', self.model_dir)
        # 切换路径 到model/rcnn_***
        sys.path.insert(0, model_root_dir)
        print(model_root_dir)
        from config import config
        from network import Network
        # from models.rcnn_emd_refine.config import config
        # from models.rcnn_emd_refine.network import Network
        self.config = config
        self.network = Network
        self.init_net()

    '''
    pred_boxes: 六个参数：四个坐标,score(置信度得分),class(类别:crowdhuman 只有'background', 'person'),框的序号
    '''    

    def init_net(self):
        # model_path
        misc_utils.ensure_dir('outputs')
        saveDir = os.path.join('../model', self.model_dir, self.config.model_dir)
        model_file = os.path.join(saveDir,
                'dump-{}.pth'.format(self.resume_weights))
        assert os.path.exists(model_file)
        # build network
        self.net = self.network()
        self.net.eval()
        check_point = torch.load(model_file, map_location=torch.device('cpu'))
        self.net.load_state_dict(check_point['state_dict'])
    #预测图片
    def detect(self,img_path):
        # get data 获得缩放大小
        image, resized_img, im_info = self.get_data(
                img_path, self.config.eval_image_short_size, self.config.eval_image_max_size) 
        pred_boxes = self.net(resized_img, im_info).numpy()
        pred_boxes = self.post_process(pred_boxes,  im_info[0, 2])
        # inplace draw 画框
        image = visual_utils.draw_boxes(
                image,
                pred_boxes[:, :4],
                line_thick=2)
        name = img_path.split('/')[-1].split('.')[-2]

        fpath = 'outputs/{}.png'.format(name)
        cv2.imwrite(fpath, image)
        image_info = {}
        count = 0
        for det in pred_boxes[:,:6]:
            #numpy转list
            det = det[np.newaxis, :]
            for *x, conf, cls_id in det:
                lbl = self.config.class_names[int(cls_id)]
                x1, y1 = int(x[0]), int(x[1])
                x2, y2 = int(x[2]), int(x[3])
                count += 1
                key = '{}-{:02}'.format(lbl, count)
                image_info[key] = ['{}×{}'.format(
                    x2-x1, y2-y1), np.round(float(conf), 3)]

        return image,image_info
        #return image_info
    #返回预测框 pred_boxes
    def post_process(self,pred_boxes, scale):
        if self.config.test_nms_method == 'set_nms':
            assert pred_boxes.shape[-1] > 6, "Not EMD Network! Using normal_nms instead."
            assert pred_boxes.shape[-1] % 6 == 0, "Prediction dim Error!"
            top_k = pred_boxes.shape[-1] // 6
            n = pred_boxes.shape[0]
            #此时pred_boxes 四个坐标,score(置信度得分),class(类别:crowdhuman 只有'background', 'person')
            pred_boxes = pred_boxes.reshape(-1, 6)
            #idents 标个序号
            idents = np.tile(np.arange(n)[:,None], (1, top_k)).reshape(-1, 1)
            pred_boxes = np.hstack((pred_boxes, idents))
            keep = pred_boxes[:, 4] > self.config.pred_cls_threshold
            pred_boxes = pred_boxes[keep]
            keep = nms_utils.set_cpu_nms(pred_boxes, 0.5)
            pred_boxes = pred_boxes[keep]
        elif self.config.test_nms_method == 'normal_nms':
            assert pred_boxes.shape[-1] % 6 == 0, "Prediction dim Error!"
            pred_boxes = pred_boxes.reshape(-1, 6)
            keep = pred_boxes[:, 4] > self.config.pred_cls_threshold
            pred_boxes = pred_boxes[keep]
            keep = nms_utils.cpu_nms(pred_boxes, self.config.test_nms)
            pred_boxes = pred_boxes[keep]
        elif self.config.test_nms_method == 'none':
            assert pred_boxes.shape[-1] % 6 == 0, "Prediction dim Error!"
            pred_boxes = pred_boxes.reshape(-1, 6)
            keep = pred_boxes[:, 4] > self.config.pred_cls_threshold
            pred_boxes = pred_boxes[keep]
        #if pred_boxes.shape[0] > config.detection_per_image and \
        #    config.test_nms_method != 'none':
        #    order = np.argsort(-pred_boxes[:, 4])
        #    order = order[:config.detection_per_image]
        #    pred_boxes = pred_boxes[order]
        # recovery the scale
        pred_boxes[:, :4] /= scale
        keep = pred_boxes[:, 4] > self.config.visulize_threshold
        pred_boxes = pred_boxes[keep]
        return pred_boxes
    #返回图片、变换后h w、原始h、w
    def get_data(self, img_path, short_size, max_size):
        image = cv2.imread( img_path, cv2.IMREAD_COLOR)
        resized_img, scale = self.resize_img(
                image, short_size, max_size)

        original_height, original_width = image.shape[0:2]
        height, width = resized_img.shape[0:2]
        #transpose转置矩阵 XYZ换
        resized_img = resized_img.transpose(2, 0, 1)
        im_info = np.array([height, width, scale, original_height, original_width, 0])
        return image, torch.tensor([resized_img]).float(), torch.tensor([im_info])
    #图片缩放 返回缩放后图片和图片信息
    def resize_img(self, image, short_size, max_size):
        height = image.shape[0]
        width = image.shape[1]
        im_size_min = np.min([height, width])
        im_size_max = np.max([height, width])
        scale = (short_size + 0.0) / im_size_min
        if scale * im_size_max > max_size:
            scale = (max_size + 0.0) / im_size_max
        t_height, t_width = int(round(height * scale)), int(
            round(width * scale))
        resized_image = cv2.resize(
                image, (t_width, t_height), interpolation=cv2.INTER_LINEAR)
        return resized_image, scale


if __name__ == '__main__':
    model = Detector()
    model.detect('inputs/8.jpg')
