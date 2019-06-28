import numpy as np
from tensorflow.python import pywrap_tensorflow

# 读取存储在checkpoint里的各层权重
model_dir = 'weights_best.ckpt'  # 注意这里名字的写法

reader = pywrap_tensorflow.NewCheckpointReader(model_dir)
var_to_shape_map = reader.get_variable_to_shape_map()

dict001 = {}  # 字典
for key in sorted(var_to_shape_map):
    if(key.find("BiRNN/BW/BW")!=-1):
        key2=key.replace("BiRNN/BW/BW","bidirectional_rnn/bw/bw")
    elif(key.find("BiRNN/FW/FW")!=-1):
        key2=key.replace("BiRNN/FW/FW","bidirectional_rnn/fw/fw")
    elif(key.find("RNN")!=-1):
        key2=key.replace("RNN","rnn")
    elif(key.find("MLP.1")!=-1):
        key2="rnn/while/"+key
    elif (key.find("Embedding") != -1):
        key2="rnn/while/"+key
    else:
        key2=key
    dict001[key2+":0" ] = reader.get_tensor(key) # numpy.ndarray

np.save("filename.npy", dict001)