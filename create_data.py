import numpy as np
import pandas as pd
import data_function as d_f

def offset_insertdata(data,data_nan,row_infor,type_date="D"):
  for i in range(0,len(data_nan)):
    day_check = (data[row_infor][str(data_nan[i])[0:10]].isnull())
    day_nan = pd.Series(day_check[day_check == True].index)
    if(len(day_nan)>0):
      day_none = pd.Series(day_check[day_check == False].index)
      p_offset_date = day_none + pd.Timedelta(-1,str(type_date))
      D_data_offset = (np.abs(np.array(data.loc[day_none]) - np.array(data.loc[p_offset_date]))).mean(axis=0)
      for e in range(0,len(day_nan)):
        data.loc[day_nan[e]] = data.loc[day_nan[e] + pd.Timedelta(-1,str(type_date))] + D_data_offset
  return data

def create_datatrain(url_data,s_row_nb,row_infor,asixs,past_history,future_target,STEP,mean_std=False):
    dataset = pd.DataFrame([],columns=[row_infor[1],row_infor[2]])
    freq_time = 60/STEP
    check_datetime = True
    for i in url_data:
        data_load = pd.read_csv(i,parse_dates=[row_infor[0]],index_col=row_infor[0])
        data_load = data_load[[row_infor[1],row_infor[2]]]
        dataset = dataset.append(data_load)

    if(asixs == "desc"):
        dataset=dataset.iloc[::-1]
    try:
        dataset.loc[str(dataset.index[0]):str(dataset.index[len(dataset)-1])]
        check_datetime = True
    except:
        check_datetime = False

    if(check_datetime == False):
        X_data =[]
        Y_data = []
        data_mean = 0
        data_std = 0
        return np.array(X_data),np.array(Y_data),data_mean,data_std,dataset.index
    else:
        dataset_duplicated = dataset[~dataset.index.duplicated()]
        dataset_asfreq=dataset_duplicated.asfreq(freq=str(freq_time)+"T")
        count_nan = (dataset_asfreq[row_infor[1]].isnull())
        count_nan = pd.Series(count_nan[count_nan == True].index)

        dataset_new = offset_insertdata(dataset_asfreq,count_nan,row_infor[1],type_date="D")
        print(dataset_new)
        uni_data = np.array(dataset_new)

        data_mean = uni_data[:int(len(uni_data)*0.8)].mean(axis=0)
        data_std = uni_data[:int(len(uni_data)*0.8)].std(axis=0)

        if(mean_std==True):
           uni_data = (uni_data-data_mean)/data_std
        X_data,Y_data = d_f.multivariate_data(uni_data, uni_data[:,s_row_nb], 0,None,int(past_history),int(future_target), step=STEP,single_step=True)
    return np.array(X_data),np.array(Y_data),data_mean,data_std,dataset_new.index
