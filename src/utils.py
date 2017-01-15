import tensorflow as tf
from tensorflow.contrib.layers import batch_norm
from tensorflow.contrib.layers import xavier_initializer

# Seems that it is better to put batch normalization after activation function
# https://github.com/ducha-aiki/caffenet-benchmark/blob/master/batchnorm.md


def conv(input, filter_size, stride, out_channels, name):
    in_channels = input.get_shape()[3]
    w = tf.get_variable('W_%s' % name, shape=[filter_size, filter_size, in_channels, out_channels],
                        initializer=xavier_initializer())
    b = tf.get_variable('b_%s' % name, shape=[out_channels],
                        initializer=tf.constant_initializer(0))
    c_i = tf.nn.conv2d(input, w, strides=[1, stride, stride, 1], padding="SAME") + b
    return c_i


def relu_bn_conv(input, filter_size, stride, out_channels, bn_settings, name):
    c_i = tf.maximum(0.2 * input, input)
    c_i = batch_norm(c_i, scope='bn_%s' % name, **bn_settings)
    c_i = conv(c_i, filter_size, stride, out_channels, name)
    return c_i


def tconv(input, filter_size, stride, batch_size, out_channels, name):
    in_channels = input.get_shape()[3]
    # Assume square
    in_size = input.get_shape()[1]
    out_size = stride * int(in_size)

    w = tf.get_variable('W_%s' % name, shape=[filter_size, filter_size, out_channels, in_channels],
                        initializer=tf.contrib.layers.xavier_initializer())
    b = tf.get_variable('b_%s' % name, shape=[out_channels],
                        initializer=tf.constant_initializer(0))
    c_i = tf.nn.conv2d_transpose(input, w, output_shape=[batch_size, out_size, out_size, out_channels],
                                 strides=[1, stride, stride, 1])
    return c_i


def relu_bn_tconv(input, filter_size, stride, batch_size, out_channels, bn_settings, name):
    c_i = tf.maximum(0.2 * input, input)
    c_i = batch_norm(c_i, scope='bn_%s' % name, **bn_settings)
    c_i = tconv(c_i, filter_size, stride, batch_size, out_channels, name)
    return c_i


def lin(input, size, name):
    in_size = input.get_shape()[1]
    w = tf.get_variable('W_%s' % name, shape=[in_size, size],
                        initializer=tf.contrib.layers.xavier_initializer())
    b = tf.get_variable('b_%s' % name, shape=[size],
                        initializer=tf.constant_initializer())
    c_i = tf.matmul(input, w) + b
    return c_i


def lin_relu_bn(input, size, bn_settings, name):
    c_i = lin(input, size, name)
    c_i = tf.maximum(0.2 * c_i, c_i)
    c_i = batch_norm(c_i, scope='b_n_%s' % name, **bn_settings)
    return c_i


# https://github.com/Tetrachrome/subpixel
def _phase_shift(I, r):
    # Helper function with main phase shift operation
    bsize, a, b, c = I.get_shape().as_list()
    X = tf.reshape(I, (bsize, a, b, r, r))
    X = tf.transpose(X, (0, 1, 2, 4, 3))  # bsize, a, b, 1, 1
    X = tf.split(1, a, X)  # a, [bsize, b, r, r]
    X = tf.concat(2, [tf.squeeze(x) for x in X])  # bsize, b, a*r, r
    X = tf.split(1, b, X)  # b, [bsize, a*r, r]
    X = tf.concat(2, [tf.squeeze(x) for x in X])  #
    bsize, a*r, b*r
    return tf.reshape(X, (bsize, a*r, b*r, 1))


def PS(X, r, color=False):
    # Main OP that you can arbitrarily use in you tensorflow code
    if color:
        Xc = tf.split(3, 3, X)
        X = tf.concat(3, [_phase_shift(x, r) for x in Xc])
    else:
        X = _phase_shift(X, r)
    return X


