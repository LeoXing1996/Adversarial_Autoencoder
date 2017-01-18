import numpy as np
import os
import sys
celeb_path = 'CELEB'
celeb_big_path = 'CELEB_BIG'
mnist_path = 'MNIST'


class CelebBig:
    def __init__(self, small=False):
        x = []
        # Read train data
        if small:
            r = 1
        else:
            r = 9
        for i in range(r):
            print("Reading CelebBig %d/9" % (i+1))
            xs = np.float32(np.load(os.path.join(celeb_big_path, 'celeb_%d.npy' % i)))/127.5 - 1.
            x.append(xs)

        print("Concatenate")
        self.train_images = np.concatenate(x)
        self.name = 'CelebBig'
        print("Reading done")

        # Those are just for compatibility, labels are messed up for this dataset (TODO: fix it)
        self.train_labels = np.concatenate([np.uint8(np.load(os.path.join(celeb_big_path, 'train_labels_32.npy'))),
                                            np.uint8(np.load(os.path.join(celeb_big_path, 'val_labels_32.npy'))),
                                            np.uint8(np.load(os.path.join(celeb_big_path, 'test_labels_32.npy')))])

        self.train_labels = self.train_labels[:self.train_images.shape[0]]

    def sample_image(self):
        i = np.random.randint(0, self.train_images.shape[0])
        img = np.reshape(self.train_images[i], [1, 128, 128, 3])

        y = np.reshape(self.train_labels[i], [1, 40])
        return img, y

    def sample_y(self):
        return np.array([0 for i in range(40)]).reshape([1, 40])

    def transform2display(self, image):
        image = (np.reshape(image, [128, 128, 3]) + 1) / 2.0
        image.clip(0, 1.0)
        return image

    def transform2data(self, image, alpha=False):
        if alpha:
            image = image[:, :, :3]
        return np.reshape(image, [1, 128, 128, 3])

    def iterate_minibatches(self, batchsize, shuffle=False, test=False):
        if test:
            inputs = self.test_images
            targets = self.test_labels
        else:
            inputs = self.train_images
            targets = self.train_labels
        assert len(inputs) == len(targets)
        if shuffle:
            indices = np.arange(len(inputs))
            np.random.shuffle(indices)
        for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
            if shuffle:
                excerpt = indices[start_idx:start_idx + batchsize]
            else:
                excerpt = slice(start_idx, start_idx + batchsize)
            yield (
                inputs[excerpt], targets[excerpt])


class CelebA:
    def __init__(self):
        self.train_images = np.concatenate(
            [np.float32(np.load(os.path.join(celeb_path, 'train_images_32.npy')))/127.5 - 1.,
             np.float32(np.load(os.path.join(celeb_path, 'val_images_32.npy')))/127.5 - 1.,
             np.float32(np.load(os.path.join(celeb_path, 'test_images_32.npy')))/127.5 - 1.])
        self.train_labels = np.concatenate(
            [np.uint8(np.load(os.path.join(celeb_path, 'train_labels_32.npy'))),
             np.uint8(np.load(os.path.join(celeb_path, 'val_labels_32.npy'))),
             np.uint8(np.load(os.path.join(celeb_path, 'test_labels_32.npy')))]
        )
        self.train_images = np.rollaxis(self.train_images, 1, 4)
        self.test_images = np.rollaxis(self.train_images, 1, 4)

        self.name = 'Celeb'

        with open(os.path.join(celeb_path, 'attr_names.txt')) as f:
            self.attr_names = f.readlines()[0].split()

    def sample_image(self):
        i = np.random.randint(0, self.train_images.shape[0])
        img = np.reshape(self.train_images[i], [1, 32, 32, 3])

        y = np.reshape(self.train_labels[i], [1, 40])
        return img, y

    def sample_y(self):
        return np.array([0 for i in range(40)]).reshape([1, 40])

    def transform2display(self, image):
        print(image.shape)
        image = (np.reshape(image, [32, 32, 3]) + 1) / 2.0
        image.clip(0, 1.0)
        return image

    def transform2data(self, image, alpha=False):
        if alpha:
            image = image[:, :, :3]
        return np.reshape(image, [1, 32, 32, 3])


    def iterate_minibatches(self, batchsize, shuffle=False, test=False):
        if test:
            inputs = self.test_images
            targets = self.test_labels
        else:
            inputs = self.train_images
            targets = self.train_labels
        assert len(inputs) == len(targets)
        if shuffle:
            indices = np.arange(len(inputs))
            np.random.shuffle(indices)
        for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
            if shuffle:
                excerpt = indices[start_idx:start_idx + batchsize]
            else:
                excerpt = slice(start_idx, start_idx + batchsize)
            yield (
             inputs[excerpt], targets[excerpt])


class MNIST:
    # By default do not compute mean (Output layer from the network uses sigmoid activation)
    def __init__(self):
        data = self.load_dataset()
        self.train_images = data['x_train']
        self.test_images = data['x_test']
        self.name = 'Mnist'

        y_tr = data['y_train']
        y_te = data['y_test']
        # One hot encoding
        y = np.zeros((y_tr.size, 10))
        y[np.arange(y_tr.size), y_tr] = 1
        self.train_labels = y
        y = np.zeros((y_te.size, 10))
        y[np.arange(y_te.size), y_te] = 1
        self.test_labels = y

    def sample_image(self):
        i = np.random.randint(0, self.test_images.shape[0])
        img = np.reshape(self.test_images[i], [1, 784])

        y = np.reshape(self.test_labels[i], [1, 10])
        return img, y

    def sample_y(self):
        y = np.random.randint(0, 10)
        return np.array([0 if i != y else 1 for i in range(10)]).reshape([1, 10])

    def transform2display(self, image):
        image = np.resize(image, [28, 28])
        return image

    def transform2data(self, image):
        return np.resize(image, [1, 784])

    def iterate_minibatches(self, batchsize, shuffle=False, test=False):
        if test:
            inputs = self.test_images
            targets = self.test_labels
        else:
            inputs = self.train_images
            targets = self.train_labels
        assert len(inputs) == len(targets)
        if shuffle:
            indices = np.arange(len(inputs))
            np.random.shuffle(indices)
        for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
            if shuffle:
                excerpt = indices[start_idx:start_idx + batchsize]
            else:
                excerpt = slice(start_idx, start_idx + batchsize)
            yield (inputs[excerpt], targets[excerpt])

    @staticmethod
    def load_dataset():
        if sys.version_info[0] == 2:
            from urllib import urlretrieve
        else:
            from urllib.request import urlretrieve

        def download(filename, source='http://yann.lecun.com/exdb/mnist/'):
            print('Downloading %s' % filename)
            urlretrieve(source + filename, os.path.join(mnist_path, filename))

        import gzip

        def load_mnist_images(filename):
            if not os.path.exists(os.path.join(mnist_path, filename)):
                download(filename)
            with gzip.open(os.path.join(mnist_path, filename), 'rb') as f:
                data = np.frombuffer(f.read(), np.uint8, offset=16)
            data = data.reshape(-1, 1, 28, 28)
            return data / np.float32(256)

        def load_mnist_labels(filename):
            if not os.path.exists(os.path.join(mnist_path, filename)):
                download(filename)
            with gzip.open(os.path.join(mnist_path, filename), 'rb') as f:
                data = np.frombuffer(f.read(), np.uint8, offset=8)
            return data

        x_train = load_mnist_images('train-images-idx3-ubyte.gz')
        y_train = load_mnist_labels('train-labels-idx1-ubyte.gz')
        x_test = load_mnist_images('t10k-images-idx3-ubyte.gz')
        y_test = load_mnist_labels('t10k-labels-idx1-ubyte.gz')
        x_train = np.reshape(x_train, [-1, 784])
        x_test = np.reshape(x_test, [-1, 784])
        return {'x_train': x_train, 'y_train': y_train, 'x_test': x_test, 'y_test': y_test}
