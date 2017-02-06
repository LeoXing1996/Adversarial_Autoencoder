import numpy as np
from src.model_subpix_32 import ModelSubpix32
from src.model_conv_32 import ModelConv32

from src.datasets import CelebA
from src.aae_solver import AaeSolver
from src.aae_gan_solver import AaeGanSolver
from src.aae_wgan_solver import AaeWGanSolver
from tensorflow.python.framework import ops

import tensorflow as tf
from PIL import Image
from apng import APNG
import os

# Dirty script to preview celeb images
# TO DO: Clean it up

frames = 20


def draw_images(model, name, systematic=True, gan=''):
    # Solver
    if gan == 'WGan':
        print("WGan Solver")
        solver = AaeWGanSolver(model=model)
        gan = 'WGan_'
    elif gan == 'Gan':
        print("Gan Solver")
        solver = AaeGanSolver(model=model)
        gan = 'Gan_'
    else:
        solver = AaeSolver(model=model)

    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    saver = tf.train.Saver()

    # To restore previous
    print("Restoring model")
    saver.restore(sess, 'models/model_%s%s.ckpt' % (gan, name))
    print("Model restored")

    z = []

    # If systematic then all animations pass through origin
    # If random then they pass through respective axis
    if systematic:
        name += 'sys'
        a = np.zeros([50, 50])
    else:
        name += 'rand'
        a = np.random.uniform(-1, 1, [50, 50])

    # We use sinus so that we can see edge images for longer
    for v in np.linspace(-np.pi/2, np.pi/2, frames):
        for i in range(model.z_dim):
            b = np.reshape(np.copy(a[i, :]), [1, 50])
            b[0][i] = 2.5 * np.sin(v)
            z.append(b)

    z = np.concatenate(z)
    y = np.zeros([model.z_dim * frames, 1])

    img = sess.run(solver.x_from_z, feed_dict={solver.z_provided: z, solver.y_labels: y})

    files = []
    w = 32 * 10
    h = 32 * 5

    b_i_apng = Image.new('RGB', (w, h), color=1)
    b_i_canv = Image.new('RGB', (w, h*frames), color=1)

    for f in range(frames):
        for x in range(10):
            for y in range(5):
                index = f*50 + x + y*10
                im = CelebA.transform2display(img[index])
                cimg = Image.fromarray(np.uint8(1+im * 254))
                b_i_apng.paste(cimg, (x*32, y*32))
                b_i_canv.paste(cimg, (x*32, y*32 + f*32*5))

        file = "output/celeb/Res_%d.png" % f
        files.append(file)
        # blank_image = blank_image.resize((128*10, 128*5))
        b_i_apng.save(file)
    
    ap = APNG()
    # Create animated png
    for file in files:
        ap.append(file, delay=50)
    for file in files[::-1]:
        ap.append(file, delay=50)

    if not os.path.exists('output/celeb'):
        os.makedirs('output/celeb')

    ap.save("output/celeb/%s.apng" % name)
    b_i_canv.save("output/celeb/%s.png" % name)


def draw_reconstruction(model, name, gan):
    # Solver
    if gan == 'WGan':
        print("WGan Solver")
        solver = AaeWGanSolver(model=model)
        gan = 'WGan_'
    elif gan == 'Gan':
        print("Gan Solver")
        solver = AaeGanSolver(model=model)
        gan = 'Gan_'
    else:
        solver = AaeSolver(model=model)

    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    saver = tf.train.Saver()

    # To restore previous
    print("Restoring model")

    saver.restore(sess, 'models/model_%s%s.ckpt' % (gan, name))
    print("Model restored")

    data = CelebA()
    x = data.train_images[:20, :]
    y = data.train_labels[:20, :]

    x_rec = sess.run(solver.x_reconstructed, feed_dict={solver.x_image: x,
                                                        solver.y_labels: y})

    b_i = Image.new('RGB', (32 * 20, 32 * 2))

    for i in range(20):
        im = x[i]
        im = CelebA.transform2display(im)
        img_o = Image.fromarray(np.uint8(im * 255))
        im = x_rec[i]
        im = CelebA.transform2display(im)
        img_r = Image.fromarray(np.uint8(im * 255))

        b_i.paste(img_o, (i * 32, 0))
        b_i.paste(img_r, (i * 32, 32))

    if not os.path.exists('output/celeb'):
        os.makedirs('output/celeb')

    b_i.save('output/celeb/%s_rec.png' % name)


# Could be improved by using one model with smaller batch size, right now there are many models
# It's bad solution but works for now
# For higher 'samples' and 'frames' value it needs a lot of GPU memory.
if __name__ == '__main__':
    scenario = 3
    celeb_z_dim = 50

    if scenario == 1:
        name = 'Celeb_Subpix_4_noy'
        model = ModelSubpix32(batch_size=frames*celeb_z_dim, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_images(model, name=name, systematic=True, gan='')
        ops.reset_default_graph()
        model = ModelSubpix32(batch_size=frames * celeb_z_dim, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_images(model, name=name, systematic=False, gan='')
        ops.reset_default_graph()
        model = ModelSubpix32(batch_size=frames * celeb_z_dim, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_reconstruction(model, name=name, gan='')

    if scenario == 2:
        name = 'Celeb_Conv_4_noy'
        model = ModelConv32(batch_size=frames * celeb_z_dim, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_images(model, name=name, systematic=True, gan='')
        ops.reset_default_graph()
        model = ModelConv32(batch_size=frames * celeb_z_dim, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_images(model, name=name, systematic=False, gan='')
        ops.reset_default_graph()
        model = ModelConv32(batch_size=20, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_reconstruction(model, name=name, gan='')

    if scenario == 3:
        name = 'Celeb_Conv_4_noy_S1_b'
        name = 'Celeb_Conv_8_noy_S6'
        model = ModelConv32(batch_size=frames * celeb_z_dim, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_images(model, name=name, systematic=True, gan='Gan')
        ops.reset_default_graph()
        model = ModelConv32(batch_size=frames * celeb_z_dim, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_images(model, name=name, systematic=False, gan='Gan')
        ops.reset_default_graph()
        model = ModelConv32(batch_size=20, z_dim=celeb_z_dim, y_dim=None, is_training=False)
        draw_reconstruction(model, name=name, gan='Gan')
