import numpy as np
import pandas as pd
import trainapi

def multivariate_data(dataset, target, start_index, end_index, history_size,target_size, step, single_step=False):
  data = []
  labels = []

  start_index = start_index + history_size
  if end_index is None:
    end_index = len(dataset) - target_size

  for i in range(start_index, end_index):
    indices = range(i-history_size, i, step)
    data.append(dataset[indices])

    if single_step:
      labels.append(target[i+target_size])
    else:
      labels.append(target[i:i+target_size])

  return np.array(data), np.array(labels)

def add_predict(dataset,nb_predict):
  a = [0,0]
  data_new = []
  for i in range(0,dataset.shape[0]):
    data_new.append(dataset[i])
  for i in range(0,nb_predict):
    data_new.append(a)
  return data_new

def datatime_json(Now_time,data_predict,f_ex):
    data_json = []
    for i in range(0,len(data_predict)):
      Now_time = np.datetime64(Now_time) + np.timedelta64(f_ex, 'm')
      data_json.append([str(Now_time),round(data_predict[i][0],2)])
    return data_json

def check_datestep(data_time,f_ex):
  data_residual = []
  step=60/f_ex
  sum_date = 24*step
  ct = 0
  time_1 = 0
  time_2 = 0
  for i in range(0,len(data_time)):
    ct = ct + 1
    ct_1 = 0
    ct_2 = 0
    for e in data_time[i-1]:
      ct_1 = ct_1 + 1
      if (e == '-'):
        ct_2=ct_2+1
        if (ct_2 == 2):
          time_1 = data_time[i-1][ct_1-8:ct_1+2]
    ct_3 = 0
    ct_4 = 0
    for e in data_time[i]:
      ct_3 = ct_3 + 1
      if (e == '-'):
        ct_4=ct_4+1
        if (ct_4 == 2):
          time_2 = data_time[i][ct_3-8:ct_3+2]
    if (time_2 != time_1):
      if (ct < sum_date or ct > sum_date):
        data_residual.append([time_1,ct])
      ct = 0
  return data_residual[1:]

def array_reverse(dataset):
    data_new = []
    for i in range(dataset.shape[0]-1,-1,-1):
      data_new.append(dataset[i])
    return np.array(data_new)

def array_append(dataset,data_append):
  data_new = []
  for i in range(0,dataset.shape[0]):
      data_new.append(dataset[i])
  for i in range(0,data_append.shape[0]):
      data_new.append(data_append[i])
  return data_new

# def check_datetime(url_data,row_infor,f_ex,asixs):
#     e_date=[]
#     for i in url_data:
#         data_load = pd.read_csv(i,parse_dates=[row_infor[0]],index_col=row_infor[0])
#         if(asixs == "desc"):
#           data_load = data_load.iloc[::-1]
#         datetime = list(map(str,data_load.index))
#         error_date = check_datestep(datetime,f_ex)
#     return error_date

def accuracy_score(val_data,nb_test,model,mean,std,type_data,mean_std=False):
  score_list = []
  if(mean_std==True):
    for x, y in val_data.take(nb_test):
      y_true = float(y[0]*std[type_data] + mean[type_data])
      y_predict = (model.predict(x)[0][0])*std[type_data] + mean[type_data]
      score = abs(y_true-y_predict)/y_true
      score_list.append(round(score,3))
  else:
    for x, y in val_data.take(nb_test):
      y_true = float(y[0])
      y_predict = (model.predict(x)[0][0])
      score = abs(y_true-y_predict)/y_true
      score_list.append(round(score,3))
  return score_list