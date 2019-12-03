#coding=utf-8

import os
from pygp import *


def main():
    data_dir = './data'
    fnames = os.listdir(data_dir)
    env_ds = EnvDataset()
    for fname in fnames:
        if fname in ['Bedrock']:
            layer = EnvLayer(filename=os.path.join(data_dir, fname), data_type=DataTypeEnum.CATEGORICAL)
        else:
            layer = EnvLayer(filename=os.path.join(data_dir, fname), data_type=DataTypeEnum.CONTINUOUS)
        env_ds.add_layer(layer)
    print('the boundary: xmin={}, ymin={}, xmax={}, ymax={}'.format(env_ds.desc.xmin, env_ds.desc.ymin, env_ds.desc.xmax, env_ds.desc.ymax))
    all_env_units = env_ds.env_units
    print(len(all_env_units))


if __name__ == '__main__':
    main()
