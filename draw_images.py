import numpy as np
from itertools import combinations

from src.datasets import MNIST, CelebA
from src.model_dense_mnist import ModelDenseMnist
from src.model_conv_mnist import ModelConvMnist
from src.model_mnist_hq import ModelHqMnist
from src.model_conv_32 import ModelConv32
from src.aae_solver import AaeSolver
import tensorflow as tf
from PIL import Image

samples = 5


# Script to generate series of images that can later be converted to a gif
def draw_images(model, name):
    # Solver
    solver = AaeSolver(model=model)
    # Session
    config = tf.ConfigProto(
        device_count={'GPU': 0}
    )
    sess = tf.Session(config=config)
    sess.run(tf.global_variables_initializer())
    # Saver

    saver = tf.train.Saver()

    # To restore previous
    print("Restoring model")
    saver.restore(sess, 'models/model_%s.ckpt' % name)
    print("Model restored")

    z = []

    # Generate grid of z
    r = 1.8
    for z_4 in np.linspace(-r, r, 20):
        for z_3 in np.linspace(-r, r, samples):
            for z_2 in np.linspace(-r, r, samples):
                for z_1 in np.linspace(-r, r, samples):
                    for z_0 in np.linspace(-r, r, samples):
                        z.append([z_4, z_1, z_2, z_3, z_0])

    z = np.array(z)
    z.reshape([-1, model.z_dim])
    code_4 = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0]]
    #code_8 = [[0, 0, 0, 0, 0, 0, 0, 0, 1, 0]]

    y_lab = np.reshape(code_4 * (samples**4*20), [(samples**4*20), 10])
    img = sess.run(solver.x_from_z, feed_dict={solver.z_provided: z, solver.y_labels: y_lab})

    for z4 in range(20):
        blank_image = Image.new('L', (28 * samples**2 + (samples-1)*10, 28 * samples**2 + (samples-1)*10))
        for z3 in range(samples):
            for z2 in range(samples):
                for z1 in range(samples):
                    for z0 in range(samples):
                        index = samples**4 * z4 + samples**3 * z3 + samples**2 * z2 + samples * z1 + z0
                        im = img[index].reshape([28, 28])
                        cimg = Image.fromarray(np.uint8(im*255))

                        x = z0 * 28 + z2*(10+28*samples)
                        y = z1 * 28 + z3*(10+28*samples)
                        blank_image.paste(cimg, (x, y))

        blank_image.save("output/z0/Res_%d.png" % z4)
        blank_image.save("output/z0/Res_%d.png" % (39-z4))


def compare_style(model, name):
    # Solver
    solver = AaeSolver(model=model)
    # Session
    config = tf.ConfigProto(
        device_count={'GPU': 0}
    )
    sess = tf.Session(config=config)
    sess.run(tf.global_variables_initializer())
    # Saver

    saver = tf.train.Saver()

    # To restore previous
    print("Restoring model")
    saver.restore(sess, 'models/model_%s.ckpt' % name)
    print("Model restored")

    b_i = []
    for i in range(91):
        b_i.append(Image.new('L', (28 * 5, 28 *5)))

    ys = []

    for i in range(9):
        y = [0] * 10
        y[i] = 1.0
        ys.append(np.array(y).reshape([1, 10]))
        for j in range(1, 10):
            y = [0] * 10
            y[i] = 1 - np.sin(np.pi/20*j)
            y[i+1] = np.sin(np.pi/20*j)
            ys.append(np.array(y).reshape([1, 10]))

    y = [0] * 10
    y[9] = 1.0
    ys.append(np.array(y).reshape([1, 10]))
    y = np.concatenate(ys, axis=0)

    print(y.shape)
    for i in range(25):
        z = np.random.uniform(-1.5, 1.5, size=[1, 5])
        z = np.tile(z, [91, 1])
        print(z.shape)
        img = sess.run(solver.x_from_z, feed_dict={solver.z_provided: z, solver.y_labels: y})

        for j in range(91):
            im = img[j].reshape([28, 28])
            cimg = Image.fromarray(np.uint8(im * 255))
            x = 28 * (i%5)
            x2 = 28 * (i//5)
            b_i[j].paste(cimg, (x, x2))

    for i in range(91):
        b_i[i].save("output/style/Res_%d.png" % i)

if __name__ == '__main__':
    scenario = -1

    if scenario == 1:
        y_dim = 10
        model = ModelDenseMnist(batch_size=samples**4*20, z_dim=5, y_dim=y_dim, is_training=False)
        draw_images(model, name='Mnist_Dense_y')
    if scenario == -1:
        y_dim = 10
        model = ModelDenseMnist(batch_size=91, z_dim=5, y_dim=y_dim, is_training=False)
        compare_style(model, name='Mnist_Dense_y')

    if scenario == 2:
        y_dim = None
        model = ModelDenseMnist(batch_size=samples**4*20, z_dim=5, y_dim=y_dim, is_training=False)
        draw_images(model, name='Mnist_Dense_noy')
    if scenario == 3:
        model = ModelHqMnist(batch_size=100, z_dim=5, y_dim=y_dim, is_training=False)
        draw_images(model, name='Mnist_Hq')
    if scenario == 4:
        model = ModelConv32(batch_size=128, z_dim=25, y_dim=None, is_training=False)
        data = CelebA()
        draw_images(model, name='Celeb_Conv_Momentum_noy')
