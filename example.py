"""
Example for how to load data and display results on one subject's cortical surface.
"""

import matplotlib.pyplot as plt
import numpy as np
import utils
import os
from scipy.stats import zscore
import matplotlib.animation as animation

# Get path to data files
datadir = os.path.abspath('/mnt/zamia/youyuan/Deniz_et_al_2019')
filedir = os.path.dirname(os.path.abspath(__file__))
savepath = os.path.join(filedir, 'sub02')
 
modality = "listening"
subject = "02"

# Load training data for subject 1, Listening dataset 
fname_trn = os.path.join(datadir, 'subject{}_{}_fmri_data_trn.hdf'.format(subject, modality))
trndata = utils.load_data(fname_trn)
for k in trndata.keys():
    print(trndata[k].shape)

# Load validation data for subject 1, Listening dataset
# story_11 is the validation story ==> Check README
fname_val = os.path.join(datadir, 'subject{}_{}_fmri_data_val.hdf'.format(subject, modality))
valdata = utils.load_data(fname_val, "story_11")["story_11"]
print(valdata.shape) # (2, 311, 81133)


# Correlate repetitions across time points (per voxel)
valdata_corr = np.fromiter(map(lambda c1,c2: (zscore(c1)*zscore(c2)).mean(0), valdata[0].T, valdata[1].T), dtype=valdata.dtype)

# Map to subject flatmap
map_file = os.path.join(datadir, 'subject02_mappers.hdf')

for k in trndata.keys():

    # Plot flatmap
    fig, ax = plt.subplots()
    # _ = ax.imshow(flatmap, cmap='inferno')
    ax.axis('off')
    # plt.savefig(os.path.join(savepath, 'flatmap.png'), bbox_inches='tight')

    def init():
        flatmap = utils.map_to_flat(trndata[k][0], map_file)
        ax.imshow(flatmap, cmap='inferno')
        return ax,

    def update(frame):
        flatmap = utils.map_to_flat(trndata[k][frame], map_file)
        ax.cla()
        ax.imshow(flatmap, cmap='inferno')
        return ax,

    anim = animation.FuncAnimation(fig, update, init_func=init, frames=100, interval=20, blit=False)
    anim.save(os.path.join(savepath, '{}.gif'.format(k)))