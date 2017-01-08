import tensorflow as tf
from tensorflow.contrib.layers import batch_norm

class ModelDenseMnist:

    def __init__(self, batch_size, z_dim):
        self.neuron_numbers = [800, 800]
        self.batch_size = batch_size
        self.input_dim = 784
        self.z_dim = z_dim
        self.x_image = tf.placeholder(tf.float32, [batch_size, self.input_dim], name='x_image')
        self.bn_settings = {'decay': 0.9,
                            'updates_collections': None,
                            'scale': True,
                            'epsilon': 1e-05}

    def encoder(self):
        current_input = self.x_image
        input_dim = self.input_dim
        for i, n in enumerate(self.neuron_numbers):
            w = tf.get_variable('W_enc_dens%d' % i, shape=[input_dim, n],
                                initializer=tf.contrib.layers.xavier_initializer())
            b = tf.get_variable('b_enc_dens%d' % i, shape=[n],
                                initializer=tf.constant_initializer())
            current_input = tf.matmul(current_input, w) + b
            current_input = batch_norm(current_input, scope=('batch_norm_enc%d' % i), **self.bn_settings)
            current_input = tf.nn.relu(current_input)
            input_dim = n

        w = tf.get_variable('W_enc_out', shape=[input_dim, self.z_dim],
                            initializer=tf.contrib.layers.xavier_initializer())
        b = tf.get_variable('b_enc_out', shape=[self.z_dim],
                            initializer=tf.constant_initializer())
        z = tf.matmul(current_input, w) + b
        return z

    def decoder(self, z, reuse=False, hq=False):
        with tf.variable_scope('decoder') as scope:
            if reuse:
                scope.reuse_variables()
            current_input = z
            input_dim = self.z_dim
            for i, n in enumerate(self.neuron_numbers[::-1]):
                w = tf.get_variable('W_dec_dens%d' % i, shape=[input_dim, n],
                                    initializer=tf.contrib.layers.xavier_initializer())
                b = tf.get_variable('b_dec_dens%d' % i, shape=[n],
                                    initializer=tf.constant_initializer())
                current_input = tf.matmul(current_input, w) + b
                current_input = batch_norm(current_input, scope=('batch_norm_dec%d' % i), **self.bn_settings)
                current_input = tf.nn.relu(current_input)
                input_dim = n

            w = tf.get_variable('W_dec_out', shape=[input_dim, self.input_dim],
                                initializer=tf.contrib.layers.xavier_initializer())
            b = tf.get_variable('b_dec_out', shape=[self.input_dim], initializer=tf.constant_initializer())
            x_reconstructed = tf.matmul(current_input, w) + b
            x_reconstructed = tf.nn.sigmoid(x_reconstructed)
            return x_reconstructed

    def discriminator(self, z, reuse=False):
        with tf.variable_scope('discriminator') as scope:
            if reuse:
                scope.reuse_variables()
            neuron_numbers = [250, 250]
            current_input = z
            input_dim = self.z_dim
            for i, n in enumerate(neuron_numbers):
                w = tf.get_variable('W_disc_dens%d' % i, shape=[input_dim, n],
                                    initializer=tf.contrib.layers.xavier_initializer())
                b = tf.get_variable('b_disc_dens%d' % i, shape=[n], initializer=tf.constant_initializer())
                current_input = tf.matmul(current_input, w) + b
                current_input = tf.nn.relu(current_input)
                input_dim = n

            w = tf.get_variable('W_disc_out', shape=[input_dim, 1],
                                initializer=tf.contrib.layers.xavier_initializer())
            b = tf.get_variable('b_disc_out', shape=[1],
                                initializer=tf.constant_initializer())
            y = tf.sigmoid(tf.matmul(current_input, w) + b)
        return y

    def sampler(self):
        z = tf.random_uniform([self.batch_size, self.z_dim], -1, 1, name='sampled_z')
        return z
