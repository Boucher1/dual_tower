# coding=utf-8

from sklearn.preprocessing import label_binarize
from semantic_model import BaseModel
import abc
import time
from loguru import logger
import torch
import torch.nn.functional as F
import numpy as np
from torch import nn
from sklearn import metrics
from sklearn.metrics import mean_squared_error


class Scaled_Dot_Product_Attention(nn.Module):
    '''Scaled Dot-Product Attention '''

    def __init__(self):
        super(Scaled_Dot_Product_Attention, self).__init__()

    def forward(self, Q, K, V, scale=None):
        attention = torch.matmul(Q, K.permute(0, 2, 1))
        if scale:
            attention = attention * scale
        # if mask:  # TODO change this
        #     attention = attention.masked_fill_(mask == 0, -1e9)
        attention = F.softmax(attention, dim=-1)
        context = torch.matmul(attention, V)
        return context


class Multi_Head_Attention(nn.Module):
    def __init__(self, dim_model, num_head, dropout=0.0):
        super(Multi_Head_Attention, self).__init__()
        self.num_head = num_head
        assert dim_model % num_head == 0
        self.dim_head = dim_model // self.num_head
        self.fc_Q = nn.Linear(dim_model, num_head * self.dim_head)
        self.fc_K = nn.Linear(dim_model, num_head * self.dim_head)
        self.fc_V = nn.Linear(dim_model, num_head * self.dim_head)
        self.attention = Scaled_Dot_Product_Attention()
        self.fc = nn.Linear(num_head * self.dim_head, dim_model)
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(dim_model)

    def forward(self, x):
        batch_size = x.size(0)
        Q = self.fc_Q(x)
        K = self.fc_K(x)
        V = self.fc_V(x)
        Q = Q.view(batch_size * self.num_head, -1, self.dim_head)
        K = K.view(batch_size * self.num_head, -1, self.dim_head)
        V = V.view(batch_size * self.num_head, -1, self.dim_head)
        # if mask:  # TODO
        #     mask = mask.repeat(self.num_head, 1, 1)  # TODO change this
        scale = K.size(-1) ** -0.5
        context = self.attention(Q, K, V, scale)

        context = context.view(batch_size, -1, self.dim_head * self.num_head)
        out = self.fc(context)
        out = self.dropout(out)
        out = out + x
        out = self.layer_norm(out)
        return out


class Position_wise_Feed_Forward(nn.Module):
    def __init__(self, dim_model, hidden, dropout=0.0):
        super(Position_wise_Feed_Forward, self).__init__()
        self.fc1 = nn.Linear(dim_model, hidden)
        self.fc2 = nn.Linear(hidden, dim_model)
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(dim_model)

    def forward(self, x):
        out = self.fc1(x)
        out = F.relu(out)
        out = self.fc2(out)
        out = self.dropout(out)
        out = out + x
        out = self.layer_norm(out)
        return out


class Encoder(nn.Module):
    def __init__(self, dim_model, num_head, hidden, dropout):
        super(Encoder, self).__init__()
        self.attention = Multi_Head_Attention(dim_model, num_head, dropout)
        self.feed_forward = Position_wise_Feed_Forward(dim_model, hidden, dropout)

    def forward(self, x):
        out = self.attention(x)

        out = self.feed_forward(out)

        return out


class SentenceBERT(BaseModel):
    def __init__(
            self,
            pretrained_model,
            num_labels,
            pooling_mode='mean',
            concat_rep=True,
            concat_diff=True,
            concat_multiply=False,
            output_emb_size=None,
    ):
        super().__init__(pretrained_model, output_emb_size)

        self.concat_rep = concat_rep  # True
        self.concat_diff = concat_diff  # True
        self.concat_multiply = concat_multiply  # False
        self.pooling_mode = pooling_mode  # Linear

        dim_model = 768
        num_head = 3
        hidden = 3072
        dropout = 0.5
        self.selfAttenQ = Encoder(dim_model, num_head, hidden, dropout)
        self.selfAttenG = Encoder(dim_model, num_head, hidden, dropout)

        self.Q_linear = nn.Linear(768, 768)
        self.G_linear = nn.Linear(768, 768)
        self.relu_Q = nn.ReLU()
        self.relu_G = nn.ReLU()
        # self.dropout = nn.Dropout(0.2)

        self.cos = nn.CosineSimilarity(dim=1, eps=1e-6)

    def forward(
            self,
            input_ids,
            pair_input_ids,
            attention_mask=None,
            token_type_ids=None,
            pair_attention_mask=None,
            pair_token_type_ids=None,
            labels=None
    ):
        emb = self.encode(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            pooling_mode=self.pooling_mode,
            normalize_to_unit=False
        )

        pair_emb = self.encode(
            pair_input_ids,
            attention_mask=pair_attention_mask,
            token_type_ids=pair_token_type_ids,
            pooling_mode=self.pooling_mode,
            normalize_to_unit=False
        )

        """
            idea:
                在embedding之后进行交互
        """
        # print(emb.shape)
        # print("old emb shape", emb.shape)  # old emb shape torch.Size([32, 768])
        emb = self.selfAttenQ(emb)
        emb = torch.mean(emb, dim=0)  # 降维 [32, 32, 768]
        emb = self.Q_linear(emb)  # emb shape torch.Size([32, 768])
        emb = self.relu_Q(emb)

        pair_emb = self.selfAttenG(pair_emb)
        pair_emb = torch.mean(pair_emb, dim=0)
        pair_emb = self.G_linear(pair_emb)
        pair_emb = self.relu_G(pair_emb)

        output = self.cos(emb, pair_emb)  # output shape torch.Size([32])
        return output

    def add_optimizer(self, optimizer):
        self.optimizer = optimizer

    def reduce_lr(self):
        logger.info("Reducing LR ......")
        for g in self.optimizer.param_groups:
            g['lr'] = g['lr'] / 2

    def add_loss_op(self, loss_op):
        self.loss_op = loss_op

    def run_epoch(self, train_dataloader, dev_dataloader, device, epoch, epochs):
        train_losses = []
        losses = []
        self.train()

        if (epoch == int(epochs / 3)) or (epoch == int(2 * epochs / 3)):
            self.reduce_lr()

        for step, batch in enumerate(train_dataloader, start=1):
            tic_train = time.time()
            self.optimizer.zero_grad()

            input_ids, token_type_ids, attention_mask, pair_input_ids, pair_token_type_ids, pair_attention_mask, labels = batch
            input_ids = input_ids.to(device)
            token_type_ids = token_type_ids.to(device)
            attention_mask = attention_mask.to(device)
            pair_input_ids = pair_input_ids.to(device)
            pair_token_type_ids = pair_token_type_ids.to(device)
            pair_attention_mask = pair_attention_mask.to(device)
            labels = labels.to(device)

            y_pred = self.__call__(
                input_ids,
                pair_input_ids,
                token_type_ids=token_type_ids,
                attention_mask=attention_mask,
                pair_token_type_ids=pair_token_type_ids,
                pair_attention_mask=pair_attention_mask
            )
            loss = self.loss_op(y_pred, labels.float())
            loss.backward()
            losses.append(loss.data.cpu().numpy())
            self.optimizer.step()

            if step % 3000 == 0:
                avg_train_loss = np.mean(losses)
                train_losses.append(avg_train_loss)
                predicted = y_pred.cpu().data.numpy()
                MSE = mean_squared_error(predicted, labels.cpu().data.numpy())
                # print(predicted)
                j = 0
                for i in predicted:
                    # 阈值 0.5
                    if (predicted[j] > 0.50):
                        predicted[j] = 1
                    else:
                        predicted[j] = 0
                    j = j + 1

                # 将变为三分类 计算acc f1
                acc = metrics.accuracy_score(predicted, labels.cpu().data.numpy())
                f1 = metrics.f1_score(predicted, labels.cpu().data.numpy(), pos_label=1)
                rec = metrics.recall_score(labels.cpu().data.numpy(), predicted, average='binary')  # 计算为1的正样本的top3召回率

                time_diff = time.time() - tic_train

                logger.info(
                    " batch: %d, loss: %.5f, accuracy: %.5f,f1:%.5f,R@3:%.5f,MSE: %.5f,speed: %.2f step/s"
                    % (step, loss, acc, f1, rec, MSE, 20 / time_diff))
                losses = []
        acc, f1, rec, MSE = evaluate(self, dev_dataloader, device)
        return train_losses, acc, f1, rec, MSE


def evaluate(model, dataloader, device):
    """
    Evaluate model performance on a given dataset.
    """
    tic_train = time.time()
    all_preds, pred = [], []
    all_y, true = [], []
    model.eval()
    with torch.no_grad():
        for batch in dataloader:
            input_ids, token_type_ids, attention_mask, pair_input_ids, pair_token_type_ids, pair_attention_mask, labels = batch
            input_ids = input_ids.to(device)
            token_type_ids = token_type_ids.to(device)
            attention_mask = attention_mask.to(device)
            pair_input_ids = pair_input_ids.to(device)
            pair_token_type_ids = pair_token_type_ids.to(device)
            pair_attention_mask = pair_attention_mask.to(device)
            labels = labels.to(device)

            y_pred = model(
                input_ids,
                pair_input_ids,
                token_type_ids=token_type_ids,
                attention_mask=attention_mask,
                pair_token_type_ids=pair_token_type_ids,
                pair_attention_mask=pair_attention_mask
            )
            predicted = y_pred.cpu().data.numpy()
            pred.extend(predicted)
            true.extend(labels.cpu().data.numpy())
            j = 0
            for i in predicted:
                # 阈值 0.5
                if (predicted[j] > 0.50):
                    predicted[j] = 1
                else:
                    predicted[j] = 0

                j = j + 1
            all_preds.extend(predicted)
            all_y.extend(labels.cpu().data.numpy())

    MSE = mean_squared_error(pred, true)
    acc = metrics.accuracy_score(all_preds, all_y)
    f1 = metrics.f1_score(all_preds, all_y, pos_label=1)
    rec = metrics.recall_score(all_y, all_preds, average='binary')  # 计算为1的正样本的top3召回率

    time_diff = time.time() - tic_train
    logger.info(
        "Test accuracy: %.5f,f1:%.5f,R@3:%.5f,MSE:%.5f, speed: %.2f step/s"
        % (acc, f1, rec, MSE, 20 / time_diff))
    # print("ACC: " + str(acc * 100))
    # print("F1: " + str(f1 * 100))
    model.train()
    return acc, f1, rec, MSE
