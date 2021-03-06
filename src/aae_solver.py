import tensorflow as tf
from tensorflow.python.ops.nn import sigmoid_cross_entropy_with_logits as ce_loss


class AaeSolver:
    def __init__(self, model):

        # Tensor with images provided by the user
        self.x_image = model.x_image
        self.y_labels = model.y_labels

        # Two sources of latent variables (encoded and sampled from selected distribution)
        self.z_sampled = model.sampler()
        self.z_encoded = model.encoder()

        # Getting images from latent variables provided by the user
        self.z_provided = tf.placeholder(tf.float32, shape=[model.batch_size, model.z_dim])
        self.x_from_z = model.decoder(self.z_provided)

        # Learning rates for different parts of training
        self.rec_lr = tf.placeholder(tf.float32, shape=[])
        self.disc_lr = tf.placeholder(tf.float32, shape=[])
        self.enc_lr = tf.placeholder(tf.float32, shape=[])

        # Reconstruction
        self.x_reconstructed = model.decoder(self.z_encoded, reuse=True)
        self.rec_loss = tf.reduce_mean(tf.square(self.x_reconstructed - self.x_image))

        t_vars = tf.trainable_variables()
        rec_vars = [var for var in t_vars if 'dec' in var.name or 'enc' in var.name]

        self.rec_optimizer = tf.train.RMSPropOptimizer(learning_rate=self.rec_lr).\
            minimize(self.rec_loss, var_list=rec_vars)

        # Discriminator
        self.y_pred_sam = model.discriminator(self.z_sampled)
        self.y_pred_enc = model.discriminator(self.z_encoded, reuse=True)

        disc_loss_sam = ce_loss(self.y_pred_sam, tf.ones_like(self.y_pred_sam))
        disc_loss_enc = ce_loss(self.y_pred_enc, tf.zeros_like(self.y_pred_enc))
        disc_loss = tf.reduce_mean(disc_loss_sam) + tf.reduce_mean(disc_loss_enc)
        self.disc_loss = disc_loss / 2.0

        t_vars = tf.trainable_variables()
        disc_vars = [var for var in t_vars if 'disc' in var.name]
        self.disc_optimizer = tf.train.RMSPropOptimizer(learning_rate=self.disc_lr).\
            minimize(self.disc_loss, var_list=disc_vars)

        # Encoder
        enc_loss = ce_loss(self.y_pred_enc, tf.ones_like(self.y_pred_enc))
        self.enc_loss = tf.reduce_mean(enc_loss)

        t_vars = tf.trainable_variables()
        enc_vars = [var for var in t_vars if 'enc' in var.name]

        self.enc_optimizer = tf.train.RMSPropOptimizer(learning_rate=self.enc_lr).\
            minimize(self.enc_loss, var_list=enc_vars)
