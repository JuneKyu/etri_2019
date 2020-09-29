#!/home/junekyu/anaconda3/bin python3
# -*- coding: utf-8 -*-
"""
python main.py for anomally detection
paper name : ''
"""
import time
import datetime
import os
import pdb
import argparse
import logging
import numpy as np
import warnings
import config
from data_util.main import load_dataset
from models.my_model import Model

warnings.filterwarnings('ignore')


def main():

    np.random.seed(777)

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='../data')
    parser.add_argument('--dataset_name', type=str, default='swat')
    parser.add_argument('--sentence_embedding',
                        type=str,
                        default='sentence_embedding')
    parser.add_argument('--normal_class_index_list', nargs='+',
                        default=[0])  # get a list of normal class indexes
    parser.add_argument('--classifier', type=str, default='linear')
    parser.add_argument('--cluster_num', type=int, default=5)
    parser.add_argument('--cluster_type', type=str, default='gmm')
    #  parser.add_argument('--use_noise_labeling', type=bool, default='True')
    # dataset_name : 'swat', 'wadi', 'cola', 'reuters', 'newsgroups', 'imdb'

    args = parser.parse_args()

    # data_path
    data_path = args.data_path
    # data_name
    dataset_name = args.dataset_name
    # if text data, set sentence embedding
    config.sentence_embedding = args.sentence_embedding
    # if image data, set rgb flag
    if (dataset_name in config.rgb_datasets):
        config.is_rgb = True
        config.cvae_channel = 3

    classifier = args.classifier
    config.classifier = classifier

    cluster_num = args.cluster_num
    cluster_type = args.cluster_type
    config.cluster_type = cluster_type

    normal_class_index_list = args.normal_class_index_list
    normal_class_index_list = [int(i) for i in normal_class_index_list]
    config.normal_class_index_list = normal_class_index_list
    config.cluster_num = cluster_num

    # logger
    log = config.logger
    folder_path = config.folder_path
    if os.path.exists(folder_path) == False:
        os.makedirs(folder_path)
    fileHandler = logging.FileHandler(\
            os.path.join(folder_path, config.current_time + '-' +\
            dataset_name + '-' +\
            cluster_type + '-' +\
            classifier + '.txt'))
    fileHandler.setFormatter(config.formatter)
    config.logger.addHandler(fileHandler)

    log.info("-" * 99)
    log.info("-" * 10 + str(args) + "-" * 10)
    log.info("-" * 99)

    log.info('START %s:%s:%s\n' %
             (datetime.datetime.now().hour, datetime.datetime.now().minute,
              datetime.datetime.now().second))

    log.info('%s:%s:%s\n' %
             (datetime.datetime.now().hour, datetime.datetime.now().minute,
              datetime.datetime.now().second))

    print("dataset name : " + dataset_name)
    log.info("dataset name : " + dataset_name)

    # data specific parameter configurations
    #  if (dataset_name in ("swat")) and (cluster_type in ("dec")):
    #      config.set_dec_lower_learning_rate = True

    print("normal_class_index_list : {}".format(normal_class_index_list))
    log.info("normal_class_index_list : {}".format(normal_class_index_list))

    # loading dataset
    dataset = load_dataset(dataset_name=dataset_name, data_path=data_path)

    print("")
    print("dataset loading successful!")
    log.info("dataset loading successful")

    model = Model(dataset_name=dataset_name,
                  dataset=dataset,
                  cluster_num=cluster_num,
                  cluster_type=cluster_type,
                  classifier=classifier)

    print("clustering...")
    log.info("clustering...")
    model.cluster()

    print("classifing...")
    log.info("classifing...")
    #  model.classify_naive()
    model.classify_nn(dataset_name)

    log.info("-" * 30)
    log.info("-" * 30)
    log.info('FINISH')
    log.info('%s:%s:%s' %
             (datetime.datetime.now().hour, datetime.datetime.now().minute,
              datetime.datetime.now().second))


if __name__ == "__main__":
    main()
