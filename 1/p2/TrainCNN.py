r""" This file is to train and eval the classify-model """
r"""博1bo  学2xue  笃3du  志4zhi,
    切5qie 问6wen  近7jin 思8si, 
    自9zi  由10you 无11wu 用12yong """

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from CNNModel import CNNModel
from MyDataset import MyDataset
from torch.utils.data import DataLoader
import argparse
import yaml
from easydict import EasyDict


parser = argparse.ArgumentParser(description='Classifier Task With CNN')
parser.add_argument("--config_path", type=str, default="config.yaml")
args = parser.parse_args()
config_path =args.config_path
config = yaml.load(open(config_path, 'r'), Loader=yaml.Loader)
config = EasyDict(config)
config = config["CNN"]

anno_train_path = config["Train"]["annotation_path"]
anno_val_path = config["Val"]["annotation_path"]
class_num = config["General"]["class_num"]
batch_size = config["Train"]["batch_size"]
epochs = config["Train"]["epochs"]
lr = config["Train"]["lr"]
is_load = config["Train"]["is_load"]
load_path = config["Train"]["load_path"]
save_path = config["Train"]["save_path"]


def eval(model):
    print(" -------< Evaluating >------- \n")
    eval_dataset = MyDataset(annotation_path = anno_val_path,
                              class_num = class_num, )
    eval_loader = DataLoader(dataset = eval_dataset, 
                              shuffle = True, 
                              batch_size = batch_size,
                              drop_last = False)
    acc_num = 0
    # total_loss = 0
    for i, batch in enumerate(eval_loader):
        img_tensor, label_tensor = batch # torch.tensor
        with torch.no_grad():
            pred_tensor = model(img_tensor.to(device))
            for j in range(pred_tensor.size(0)):
                pred = torch.argmax(pred_tensor[j]).item()
                # label = torch.argmax(label_tensor[j]).item()
                if pred==label_tensor[j]:
                    acc_num+=1

    acc_rate = acc_num / len(eval_dataset)
    # avg_loss = total_loss / len(eval_dataset)
    # print("eval_accuracy, %.2f total loss in %d data size" 
        #   % (total_loss, len(eval_dataset)))
    print("Acc_rate %.2f%% \n" % (acc_rate*100))
    return acc_rate


if __name__ == "__main__":
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # device = torch.device("cpu")
    model = CNNModel()
    model.to(device)
    loss_function = nn.CrossEntropyLoss() # including softmax
    train_dataset = MyDataset(annotation_path = anno_train_path,
                              class_num = class_num, )
    train_loader = DataLoader(dataset = train_dataset, 
                              shuffle = True, 
                              batch_size = batch_size,
                              drop_last = True)
    best_acc = 0.0
    # best_acc = 0.874
    epoch_record_x = []
    # avg_loss_record_y = []
    acc_rate_record_y = []
    epoch_record_x.append(0)
    acc_rate_y = eval(model)
    # avg_loss_record_y.append(avg_loss_y)
    acc_rate_record_y.append(acc_rate_y)

    for epoch in range(0, epochs+1):
        for i, batch in enumerate(train_loader):
            img_tensor, label_tensor = batch # torch.tensor
            # print("img&label size: {}, {}"
            #       .format(img_tensor.shape, label_tensor.shape))
            pred_tensor = model(img_tensor.to(device))
            # print("pred size: {}".format(pred_tensor.shape))
            # print(pred_tensor[0])
            # print("dim=0: ", torch.argmax(pred_tensor[0]))
            # print("dim=0: ", torch.argmax(pred_tensor[0]).item())
            # print("dim=1: ", torch.argmax(pred_tensor[0],dim=1))
            loss = loss_function(pred_tensor, label_tensor.to(device))
            loss.backward()
        
        if epoch % 10 == 0:
            print("Epoch" , epoch)
            epoch_record_x.append(epoch)
            acc_rate_y = eval(model)
            
            if best_acc < acc_rate_y:
                print(" -------< Saving Best Model >------- \n")
                torch.save(model.state_dict(), save_path)
                best_acc = acc_rate_y

            # avg_loss_record_y.append(avg_loss_y)
            acc_rate_record_y.append(acc_rate_y)
    
    # plt.plot(epoch_record_x, avg_loss_record_y,
    #             color="red", label="avg_loss_record")
    plt.plot(epoch_record_x, acc_rate_record_y, 
                color="green", label="acc_rate_record")
    plt.title("Loss with epoch")
    plt.legend()
    plt.show()
