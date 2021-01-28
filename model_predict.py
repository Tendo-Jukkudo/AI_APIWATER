import tensorflow as tf
import watermodel
import requests
import numpy as np
import pandas as pd
import os
import data_function as d_f
import create_data as cd
import logging

def futures_predict(input_data,type_data,path_weights,past_history,future_target,STEP,mean,std,mean_std=False):
  data_mean = mean
  data_std = std
  predict_data = []
  true_data = []
  uni_data = d_f.add_predict(input_data,future_target)
  uni_data = np.array(uni_data)
  x_data, y_data = d_f.multivariate_data(uni_data, uni_data[:,type_data],0, None, past_history,future_target, STEP,single_step=True)

  X_data = x_data[x_data.shape[0]-future_target:x_data.shape[0]]
  Y_data = y_data[x_data.shape[0]-future_target:x_data.shape[0]] 

  test_data = tf.data.Dataset.from_tensor_slices((X_data,Y_data))
  test_data = test_data.batch(1)

  model = watermodel.model_main(input_shape=X_data.shape[-2:])
  model.load_weights(path_weights)
  for x, y in test_data.take(future_target):
    if(mean_std == True):
      data_p = model.predict(x)[0]*data_std[type_data] + data_mean[type_data]
    else:
      data_p = model.predict(x)[0]
    predict_data.append(data_p) 
  return predict_data

def run_prediction(type_feature,row_infor,his,target,path_weight,url_get,f_ex,means,stds,mean_std=False):
  step = 60/f_ex
  nb_past = his*24*step
  nb_future = target*24*step
  if(type_feature == 0):
    logging.info('Predict '+row_infor[1]+' Data')
  else:
    logging.info('Predict '+row_infor[2]+' Data')

  data_mean = means
  data_std = stds
  logging.info("Data loading ...")
  df = pd.read_csv(url_get,parse_dates=[row_infor[0]],index_col=row_infor[0])
  uni_data = df[[row_infor[1],row_infor[2]]]
  logging.info("Data processing ...")
  dataset_duplicated = uni_data[~uni_data.index.duplicated()]
  dataset_asfreq=dataset_duplicated.asfreq(freq=str(f_ex)+"T")

  count_nan = (dataset_asfreq[row_infor[1]].isnull())
  count_nan = pd.Series(count_nan[count_nan == True].index)

  dataset_new = cd.offset_insertdata(dataset_asfreq,count_nan,row_infor[1],type_date="D")
  logging.info("Data Checking ...")
  datetime = list(map(str,dataset_new.index))
  nb_error = len(d_f.check_datestep(datetime,f_ex))

  uni_data_new = np.array(dataset_new)
  if(mean_std==True):
    uni_data_new = (uni_data_new - data_mean)/data_std

  if(nb_error == 0):
    logging.info("Good Data")
    logging.info("Start predict...")
    data_predict = futures_predict(input_data=uni_data_new,type_data=type_feature,
                                    path_weights=path_weight,
                                    past_history=int(nb_past),future_target=int(nb_future),
                                    STEP=int(step),mean=data_mean,std=data_std,mean_std=mean_std)
    Now_time = datetime[len(datetime)-1]
    data_json = d_f.datatime_json(Now_time,data_predict,f_ex)
    output = np.array(data_json)
    error_date = d_f.check_datestep(datetime,f_ex)
    logging.info("Successfully Training Process")
  else:
    logging.error("Data Error No: " +nb_error)
    error_date = d_f.check_datestep(datetime,f_ex)
    output = []
  logging.info("PROCESS END")
  return output,error_date