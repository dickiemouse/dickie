import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('main_replastering.jpg')

def draw_image_histogram(image, channels, color='k'):
    hist = cv2.calcHist([image], channels, None, [256], [0, 256])
    plt.plot(hist, color=color)
    plt.xlim([0, 256])

def show_color_histogram(image):
    for i, col in enumerate(['b', 'g', 'r']):
        draw_image_histogram(image, [i], color=col)
    plt.show()

def show_image_histogram_2d(image, bins=32, tick_spacing=5):
    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    channels_mapping = {0: 'B', 1: 'G', 2: 'R'}
    for i, channels in enumerate([[0, 1], [0, 2], [1, 2]]):
        hist = cv2.calcHist(
            [image], channels, None, [bins] * 2, [0, 256] * 2)

        channel_x = channels_mapping[channels[0]]
        channel_y = channels_mapping[channels[1]]

        ax = axes[i]
        ax.set_xlim([0, bins - 1])
        ax.set_ylim([0, bins - 1])

        ax.set_xlabel(f'Channel {channel_x}')
        ax.set_ylabel(f'Channel {channel_y}')
        ax.set_title(f'2D Color Histogram for {channel_x} and {channel_y}')

        ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        im = ax.imshow(hist)

    fig.colorbar(im, ax=axes.ravel().tolist(), orientation='orizontal')
    fig.suptitle(f'2D Color Histograms with {bins} bins', fontsize=16)
    plt.show()
def rgb_equalized(image):
    channels = cv2.split(image)
    eq_channels = []
    for ch, color in zip(channels, ['B', 'G', 'R']):
        eq_channels.append(cv2.equalizeHist(ch))

    eq_image = cv2.merge(eq_channels)
    eq_image = cv2.cvtColor(eq_image, cv2.COLOR_BGR2RGB)
    return eq_image
def show_rgb_equalized(image):
    channels = cv2.split(image)
    eq_channels = []
    for ch, color in zip(channels, ['B', 'G', 'R']):
        eq_channels.append(cv2.equalizeHist(ch))

    eq_image = cv2.merge(eq_channels)
    eq_image = cv2.cvtColor(eq_image, cv2.COLOR_BGR2RGB)
    plt.imshow(eq_image)
    plt.show()
def hsv_equalized(image):
    H, S, V = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))
    eq_V = cv2.equalizeHist(V)
    eq_image = cv2.cvtColor(cv2.merge([H, S, eq_V]), cv2.COLOR_HSV2RGB)
    return eq_image
def show_hsv_equalized(image):
    H, S, V = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))
    eq_V = cv2.equalizeHist(V)
    eq_image = cv2.cvtColor(cv2.merge([H, S, eq_V]), cv2.COLOR_HSV2RGB)
    plt.imshow(eq_image)
    plt.show()
show_hsv_equalized(img)

img_y_cr_cb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
y, cr, cb = cv2.split(img_y_cr_cb)

# Applying equalize Hist operation on Y channel.
y_eq = cv2.equalizeHist(y)

img_y_cr_cb_eq = cv2.merge((y_eq, cr, cb))
img_rgb_eq = cv2.cvtColor(img_y_cr_cb_eq, cv2.COLOR_YCR_CB2BGR)
vis = np.concatenate((img, img_rgb_eq), axis=1)
cv2.imwrite('out.png', vis)
cv2.imshow('image',img_rgb_eq)
cv2.waitKey(0)

# hist,bins = np.histogram(img.flatten(),256,[0,256])
#
# cdf = hist.cumsum()
# cdf_normalized = cdf * hist.max()/ cdf.max()
# cdf_m = np.ma.masked_equal(cdf,0)
# cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
# cdf = np.ma.filled(cdf_m,0).astype('uint8')
# img2 = cdf[img]
#
# plt.plot(cdf_normalized, color = 'b')
# plt.hist(img.flatten(),256,[0,256], color = 'r')
# plt.xlim([0,256])
# plt.legend(('cdf','histogram'), loc = 'upper left')
# plt.show()
#
# equ = cv2.equalizeHist(img)
# res = np.hstack((img,equ)) #stacking images side-by-side
# cv2.imwrite('res.png',res)
