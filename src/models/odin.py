#!/usr/bin/env python
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.autograd import Variable

import numpy as np
import time
import os

import config

import pdb


def apply_odin(net, test_in, test_out):

    criterion = nn.CrossEntropyLoss()
    t0 = time.time()
    if os.path.exists(config.sf_scores_path) == False:
        os.makedirs(config.sf_scores_path)
    f1 = open(config.base_in_path, "w")
    f2 = open(config.base_out_path, "w")
    g1 = open(config.odin_in_path, "w")
    g2 = open(config.odin_out_path, "w")

    #  pdb.set_trace()
    temper = config.odin_temperature
    noise_magnitude = config.odin_perturbation_magnitude

    #  test_loader = DataLoader(test_data)
    for j, data in enumerate(test_in):

        inputs = Variable(data.cuda(config.device), requires_grad=True)
        outputs = net(inputs)

        # Calculating the confidence of the output, no perturbation added here, no temperature scaling used
        nnOutputs = outputs.data.cpu()
        nnOutputs = nnOutputs.numpy()
        nnOutputs = nnOutputs[0]
        nnOutputs = nnOutputs - np.max(nnOutputs)
        nnOutputs = np.exp(nnOutputs) / np.sum(np.exp(nnOutputs))

        #  print("base, in-dist, confidence")
        #  print("{}, {}, {}\n".format(temper, noise_magnitude,
        #                              np.max(nnOutputs)))

        f1.write("{}, {}, {}\n".format(temper, noise_magnitude,
                                       np.max(nnOutputs)))

        # Using temperature scaling
        outputs = outputs / temper

        # Calculating the perturbation we need to add, that is,
        # the sign of gradient of cross entropy loss w.r.t input
        maxIndexTemp = np.argmax(nnOutputs)
        labels = Variable(torch.LongTensor([maxIndexTemp]).cuda(config.device))
        loss = criterion(outputs, labels)
        loss.backward()

        gradient = torch.ge(inputs.grad.data, 0)
        gradient = (gradient.float() - 0.5) * 2

        gradient = gradient / (63.0 / 255.0)
        tempInputs = torch.add(inputs.data, -noise_magnitude, gradient)
        outputs = net(Variable(tempInputs))
        outputs = outputs / temper

        nnOutputs = outputs.data.cpu()
        nnOutputs = nnOutputs.numpy()
        nnOutputs = nnOutputs[0]
        nnOutputs = nnOutputs - np.max(nnOutputs)
        nnOutputs = np.exp(nnOutputs) / np.sum(np.exp(nnOutputs))

        #  print("odin, in_dist, confidence")
        #  print("{}, {}, {}\n".format(temper, noise_magnitude,
        #                              np.max(nnOutputs)))
        g1.write("{}, {}, {}\n".format(temper, noise_magnitude,
                                       np.max(nnOutputs)))

        if j % 100 == 99:
            print("{:4}/{:4} data processed, {:.1f} seconds used.".format(
                j + 1, len(test_in),
                time.time() - t0))
            t0 = time.time()

        # out distribution test


#  print("out-of-distribution images")

    for j, data in enumerate(test_out):

        inputs = Variable(data.cuda(config.device), requires_grad=True)
        outputs = net(inputs)

        # Calculating the confidence of the output, no pertyrbation added here
        nnOutputs = outputs.data.cpu()
        nnOutputs = nnOutputs.numpy()
        nnOutputs = nnOutputs[0]
        nnOutputs = nnOutputs - np.max(nnOutputs)
        nnOutputs = np.exp(nnOutputs) / np.sum(np.exp(nnOutputs))

        #  print("base, out_dist, confidence")
        #  print("{}, {}, {}\n".format(temper, noise_magnitude,
        #                              np.max(nnOutputs)))
        f2.write("{}, {}, {}\n".format(temper, noise_magnitude,
                                       np.max(nnOutputs)))

        # Using temperature scaling
        outputs = outputs / temper

        # Calculating the perturbation we need to add, that is,
        # the sign of gradient of cross entropy loss w.r.t. input
        maxIndexTemp = np.argmax(nnOutputs)
        labels = Variable(torch.LongTensor([maxIndexTemp]).cuda(config.device))
        loss = criterion(outputs, labels)
        loss.backward()

        # Normalizing the gradient to binary in {0, 1}
        gradient = torch.ge(inputs.grad.data, 0)
        gradient = (gradient.float() - 0.5) * 2
        # Normalizing the gradient to the same space of image
        gradient = gradient / (63.0 / 255.0)
        # Adding small perturbations to images
        tempInputs = torch.add(inputs.data, -noise_magnitude, gradient)
        outputs = net(Variable(tempInputs))
        outputs = outputs / temper
        # Calculating the confidence after adding perturbations
        nnOutputs = outputs.data.cpu()
        nnOutputs = nnOutputs.numpy()
        nnOutputs = nnOutputs[0]
        nnOutputs = nnOutputs - np.max(nnOutputs)
        nnOutputs = np.exp(nnOutputs) / np.sum(np.exp(nnOutputs))

        #  print("odin, out_dist, confidence")
        #  print("{}, {}, {}\n".format(temper, noise_magnitude,
        #                              np.max(nnOutputs)))
        g2.write("{}, {}, {}\n".format(temper, noise_magnitude,
                                       np.max(nnOutputs)))

        if j % 100 == 99:
            print("{:4}/{:4} data processed, {:.1f} seconds used.".format(
                j + 1, len(test_out),
                time.time() - t0))
            t0 = time.time()