# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import argparse
import glob
import multiprocessing as mp
import os
import time
import cv2
from matplotlib.pyplot import box
from numpy import argsort
import tqdm
import numpy as np
from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from detectron2.utils.logger import setup_logger

from tools.predictor import VisualizationDemo

# constants
WINDOW_NAME = "COCO detections"

class NohDetector(object):
    def __init__(self) -> None:
        # self.config_file = r"configs\CrowdHuman\faster_rcnn_R_50_FPN_baseline_iou_0.5_noh_nms.yaml"
        self.config_file = r"model\noh_nms\configs\faster_rcnn_R_50_FPN_baseline_iou_0.5_noh_nms.yaml"
        #input 是list
        self.confidence_threshold = 0.5
        self.opts =['MODEL.WEIGHTS', 'model\\noh_nms\\noh_nms_model_final.pth']
        setup_logger(name="fvcore")
        self.logger = setup_logger()
        cfg = self.setup_cfg()
        self.demo = VisualizationDemo(cfg)

    def detect(self,img_path):
        image_info = {}
        if img_path:
            self.logger.info("Arguments: " + str(img_path) )
            # use PIL, to be consistent with evaluation
            img = read_image(img_path, format="BGR")
            start_time = time.time()

            #visualized_output : <class 'detectron2.utils.visualizer.VisImage'>
            predictions, visualized_output = self.demo.run_on_image(img)
            
            pred_boxes = predictions['instances'].get("pred_boxes").tensor.numpy()
            scores = predictions['instances'].get("scores").numpy()
            #shape从(8,)变成(8,1)
            scores=scores[:,np.newaxis]
            # print(pred_boxes.shape) 行链接起来
            boxes =  np.hstack((pred_boxes, scores))
            count = 0
            for det in boxes[:,:5]:
                #numpy转list
                det = det[np.newaxis, :]
                for *x, conf in det:
                    lbl = 'person'
                    x1, y1 = int(x[0]), int(x[1])
                    x2, y2 = int(x[2]), int(x[3])
                    count += 1
                    key = '{}-{:02}'.format(lbl, count)
                    image_info[key] = ['{}×{}'.format(
                        x2-x1, y2-y1), np.round(float(conf), 3)]
            #print(image_info)

            self.logger.info(
                "{}: {} in {:.2f}s".format(
                    img_path,
                    "detected {} instances".format(len(predictions["instances"]))
                    if "instances" in predictions
                    else "finished",
                    time.time() - start_time,
                )
            )
        #图片存到这个位置
        name = img_path.split('/')[-1].split('.')[-2]
        fpath = 'outputs/{}.png'.format(name)
        visualized_output.save(fpath)
        return visualized_output , image_info

    def setup_cfg(self):
        # load config from file and command-line arguments
        cfg = get_cfg()
        cfg.merge_from_file(self.config_file)
        cfg.merge_from_list(self.opts)
        # Set score_threshold for builtin models
        cfg.MODEL.RETINANET.SCORE_THRESH_TEST = self.confidence_threshold
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.confidence_threshold
        cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = self.confidence_threshold
        cfg.freeze()
        return cfg
    def print_name(self):
        print("Now It's NOH NMS!")

if __name__ == "__main__":
    #mp.set_start_method("spawn", force=True)
    d = NohDetector()
    d.detect("tools/input/51.jpg")
