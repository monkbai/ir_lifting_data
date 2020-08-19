import task_utils
import rgx_utils as rgx
import pickle
from sklearn.utils import resample
import os
import numpy as np
import math
import struct
from absl import app
from absl import flags
import time
import random
import progressbar

import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.utils.data import Dataset

# Parameters of classifyapp
flags.DEFINE_string('input_data', 'task/classifyapp', 'Path to input data')
flags.DEFINE_string('out', 'task/classifyapp', 'Path to folder in which to write saved Keras models and predictions')
flags.DEFINE_integer('num_epochs', 50, 'number of training epochs')
flags.DEFINE_integer('batch_size', 100, 'training batch size')
flags.DEFINE_integer('num_workers', 8, 'num_workers for data loader')
flags.DEFINE_integer('dense_layer_size', 32, 'dense layer size')
flags.DEFINE_integer('embedding_dim', 200, 'dense layer size')
flags.DEFINE_integer('num_classes', 104, 'dense layer size')
flags.DEFINE_integer('train_samples', 1500, 'Number of training samples per class')
flags.DEFINE_integer('vsamples', 0, 'Sampling on validation set')
flags.DEFINE_integer('save_every', 5, 'Save checkpoint every N batches')
flags.DEFINE_integer('ring_size', 5, 'Checkpoint ring buffer length')
flags.DEFINE_bool('print_summary', False, 'Print summary of Keras model')

FLAGS = flags.FLAGS

#seed = 204
#random.seed(seed)
#torch.manual_seed(seed)
#torch.cuda.manual_seed_all(seed)

########################################################################################################################
# Utils
########################################################################################################################
def get_onehot(y, num_classes):
    """
    y is a vector of numbers (1, number of classes)
    """
    hot = np.zeros((len(y), num_classes), dtype=np.int32)
    for i, c in enumerate(y):
        # i: data sample index
        # c: class number in range [1, 104]
        hot[i][int(c) - 1] = 1

    return hot


def encode_srcs(input_files, dataset_name, unk_index):
    """
    encode and pad source code for learning
    data_folder: folder from which to read input files
    input_files: list of strings of file names
    """

    # Get list of source file names
    num_files = len(input_files)
    num_unks = 0
    seq_lengths = list()

    print('\n--- Preparing to read', num_files, 'input files for', dataset_name, 'data set')
    seqs = list()
    for i, file in enumerate(input_files):
        if i % 10000 == 0:
            print('\tRead', i, 'files')
        file = file.replace('.ll', '_seq.rec')
        assert os.path.exists(file), 'input file not found: ' + file
        with open(file, 'rb') as f:
            full_seq = f.read()
        seq = list()
        for j in range(0, len(full_seq), 4):  # read 4 bytes at a time
            seq.append(struct.unpack('I', full_seq[j:j + 4])[0])
        assert len(seq) > 0, 'Found empty file: ' + file
        num_unks += seq.count(str(unk_index))
        seq_lengths.append(len(seq))
        seqs.append([int(s) for s in seq])

    print('\tShortest sequence    : {:>5}'.format(min(seq_lengths)))
    maxlen = max(seq_lengths)
    print('\tLongest sequence     : {:>5}'.format(maxlen))
    print('\tMean sequence length : {:>5} (rounded down)'.format(math.floor(np.mean(seq_lengths))))
    print('\tNumber of \'UNK\'      : {:>5}'.format(num_unks))
    print('\tPercentage of \'UNK\'  : {:>8.4} (% among all stmts)'.format((num_unks * 100) / sum(seq_lengths)))
    print('\t\'UNK\' index          : {:>5}'.format(unk_index))

    return seqs, maxlen

def pad_sequences(sequences, maxlen=None, dtype='int32',
                  padding='pre', truncating='pre', value=0.):
    if not hasattr(sequences, '__len__'):
        raise ValueError('`sequences` must be iterable.')
    num_samples = len(sequences)

    lengths = []
    sample_shape = ()
    flag = True

    # take the sample shape from the first non empty sequence
    # checking for consistency in the main loop below.

    for x in sequences:
        try:
            lengths.append(len(x))
            if flag and len(x):
                sample_shape = np.asarray(x).shape[1:]
                flag = False
        except TypeError:
            raise ValueError('`sequences` must be a list of iterables. '
                             'Found non-iterable: ' + str(x))

    if maxlen is None:
        maxlen = np.max(lengths)

    import six
    is_dtype_str = np.issubdtype(dtype, np.str_) or np.issubdtype(dtype, np.unicode_)
    if isinstance(value, six.string_types) and dtype != object and not is_dtype_str:
        raise ValueError("`dtype` {} is not compatible with `value`'s type: {}\n"
                         "You should set `dtype=object` for variable length strings."
                         .format(dtype, type(value)))

    x = np.full((num_samples, maxlen) + sample_shape, value, dtype=dtype)
    for idx, s in enumerate(sequences):
        if not len(s):
            continue  # empty list/array was found
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError('Truncating type "%s" '
                             'not understood' % truncating)

        # check `trunc` has expected shape
        trunc = np.asarray(trunc, dtype=dtype)
        if trunc.shape[1:] != sample_shape:
            raise ValueError('Shape of sample %s of sequence at position %s '
                             'is different from expected shape %s' %
                             (trunc.shape[1:], idx, sample_shape))

        if padding == 'post':
            x[idx, :len(trunc)] = trunc
        elif padding == 'pre':
            x[idx, -len(trunc):] = trunc
        else:
            raise ValueError('Padding type "%s" not understood' % padding)
    return x

def pad_src(seqs, maxlen, unk_index):
    encoded = np.array(pad_sequences(seqs, maxlen=maxlen, value=unk_index))
    return np.vstack([np.expand_dims(x, axis=0) for x in encoded])

def clear_progressbar():
    # moves up 3 lines
    print("\033[2A")
    # deletes the whole line, regardless of character position
    print("\033[2K")
    # moves up two lines again
    print("\033[2A")

class Record(object):
    def __init__(self):
        self.loss = 0
        self.count = 0

    def add(self, value):
        self.loss += value
        self.count += 1

    def mean(self):
        return self.loss / self.count

########################################################################################################################
# Data
########################################################################################################################

class DataFolder(Dataset):
    def __init__(self, x_seq, y_label):
        self.x_seq = x_seq
        self.y_label = y_label

    def __len__(self):
        return len(self.x_seq)

    def __getitem__(self, idx):
        X = self.x_seq[idx]
        X = torch.from_numpy(X).type(torch.LongTensor)
        y = self.y_label[idx]
        y = torch.LongTensor([y])
        #y = torch.from_numpy(np.ndarray([y])).type(torch.LongTensor)
        return X, y.squeeze()

########################################################################################################################
# Model
########################################################################################################################
class NCC_classifier(nn.Module):
    def __init__(self, embedding_dim: int, num_classes: int, dense_layer_size: int):
        super(NCC_classifier, self).__init__()
        self.lstm_1 = nn.LSTM(input_size=embedding_dim, hidden_size=embedding_dim, batch_first=True)
        self.lstm_2 = nn.LSTM(input_size=embedding_dim, hidden_size=embedding_dim, batch_first=True)
        self.tanh = nn.Tanh()
        self.bn = nn.BatchNorm1d(embedding_dim)
        self.dense_1 = nn.Sequential(
            nn.Linear(embedding_dim, dense_layer_size),
            nn.ReLU()
            )
        self.dense_2 = nn.Sequential(
            nn.Linear(dense_layer_size, num_classes),
            nn.Sigmoid() 
            )

    def forward(self, x):
        # x: (batch, seq_len, embedding_dim)
        self.lstm_1.flatten_parameters()
        x, (h, c) = self.lstm_1(x)
        x = self.tanh(x)
        #print('x1', x.shape)
        self.lstm_2.flatten_parameters()
        x, (h, c) = self.lstm_2(x)
        x = self.tanh(h.squeeze(0))
        #x = x.permute(0, 2, 1)
        x = self.bn(x)
        #x = x.permute(0, 2, 1)
        #print('x2', x.shape)
        x = self.dense_1(x)
        #print('x3', x.shape)
        x = self.dense_2(x)
        #print('x4', x.shape)
        return x

class Engine(object):
    def __init__(self, args):
        self.args = args
        self.gpus = torch.cuda.device_count()
        self.epoch = 0
        self.nll = nn.NLLLoss()
        self.ce = nn.CrossEntropyLoss()

        self.init_model_optimizer()
        self.load_embed()

    def weights_init(self, m):
        classname = m.__class__.__name__
        if classname.find('Conv') != -1:
            m.weight.data.normal_(0.0, 0.02)
        elif classname.find('BatchNorm') != -1:
            m.weight.data.normal_(1.0, 0.02)
            m.bias.data.fill_(0)

    def weights_init_rnn(self, model):
        if type(model) in [nn.Linear]:
            nn.init.xavier_uniform_(model.weight)
            nn.init.zeros_(model.bias)
        elif type(model) in [nn.LSTM, nn.RNN, nn.GRU]:
            nn.init.orthogonal_(model.weight_hh_l0)
            nn.init.xavier_uniform_(model.weight_ih_l0)
            nn.init.zeros_(model.bias_hh_l0)
            nn.init.zeros_(model.bias_ih_l0)

    def init_dataloader(self, train_folder, valid_folder, test_folder):
        print('Initializing Data Loader.')
        self.train_loader = torch.utils.data.DataLoader(train_folder,
                                                        batch_size=self.args.batch_size * self.gpus,
                                                        num_workers=self.args.num_workers * self.gpus,
                                                        shuffle=True,
                                                        drop_last=False)
        self.valid_loader = torch.utils.data.DataLoader(valid_folder,
                                                        batch_size=self.args.batch_size * self.gpus,
                                                        num_workers=self.args.num_workers * self.gpus,
                                                        shuffle=True,
                                                        drop_last=False)
        self.test_loader = torch.utils.data.DataLoader(test_folder,
                                                        batch_size=self.args.batch_size * self.gpus,
                                                        num_workers=self.args.num_workers * self.gpus,
                                                        shuffle=True,
                                                        drop_last=False)

    def init_model_optimizer(self):
        print('Initializing Model and Optimizer.')
        self.model = NCC_classifier(self.args.embedding_dim, self.args.num_classes, self.args.dense_layer_size)
        self.model = torch.nn.DataParallel(self.model).cuda()
        self.model.apply(self.weights_init)
        self.model.apply(self.weights_init_rnn)

        self.optim = torch.optim.Adam(self.model.module.parameters(), lr=1e-4)

    def load_embed(self):
        print('Loading Embedding.')
        embeddings = task_utils.get_embeddings()
        vocab_size = embeddings.shape[0]
        weights = torch.from_numpy(embeddings).type(torch.FloatTensor)
        weights = F.normalize(weights, p=2, dim=1)

        self.embed = nn.Embedding(vocab_size, self.args.embedding_dim)
        self.embed.weight = torch.nn.Parameter(weights)
        self.embed = torch.nn.DataParallel(self.embed).cuda()
        self.embed.eval()
        # !!!
    
    def save_model(self, path):
        state = {
            'model': self.model.module.state_dict()
        }
        torch.save(state, path)
        print('Model Saved.')

    def load_model(self, path):
        checkpoint = torch.load(path)
        self.model.module.load_state_dict(checkpoint['model'])
        print('Module Loaded.')

    def accuracy(self, preds, y):
        preds = torch.argmax(preds, dim=1)
        correct = (preds == y).float()
        #print(correct)
        #print(correct.shape)
        acc = correct.sum() / len(correct)
        return acc

    def train(self):
        with torch.autograd.set_detect_anomaly(True):
            self.model.train()
            self.epoch += 1
            record = Record()
            acc = Record()
            current_time = time.time()
            progress = progressbar.ProgressBar(maxval=len(self.train_loader)).start()
            for i, (x_seq, y_label) in enumerate(self.train_loader):
                progress.update(i + 1)
                x_seq = x_seq.cuda()
                #print('x_seq', x_seq.shape)
                y_label = y_label.cuda()
                x_embed = self.embed(x_seq)
                #print('x_embed', x_embed.shape)
                y_pred = self.model(x_embed)#.permute(1, 0, 2))
                #print('y_pred', y_pred.shape)
                #print('y_label', y_label.shape)
                #print(y_pred[0])
                #print(y_label[0])
                acc.add(self.accuracy(y_pred, y_label))
                loss = self.ce(y_pred, y_label)

                self.optim.zero_grad()
                record.add(loss.item())
                loss.backward()
                self.optim.step()
            progress.finish()
            clear_progressbar()
            print('--------------------')
            print('Epoch :', self.epoch)
            print('Time: %.2f' % (time.time() - current_time), 's')
            print('Loss: %f' % (record.mean()))
            print('Acc: %f' % (acc.mean()))
    
    def predict(self, is_test=False):
        if is_test:
            data_loader = self.test_loader
        else:
            data_loader = self.valid_loader
        with torch.no_grad():
            self.model.eval()
            record = Record()
            acc = Record()
            current_time = time.time()
            progress = progressbar.ProgressBar(maxval=len(data_loader)).start()
            for i, (x_seq, y_label) in enumerate(data_loader):
                progress.update(i + 1)
                x_seq = x_seq.cuda()
                y_label = y_label.cuda()

                y_pred = self.model(self.embed(x_seq))
                acc.add(self.accuracy(y_pred, y_label))
                loss = self.ce(y_pred, y_label)
                record.add(loss.item())
            progress.finish()
            clear_progressbar()
            print('--------------------')
            print('Predict')
            print('Time: %.2f' % (time.time() - current_time), 's')
            print('Loss: %f' % (record.mean()))
            print('Acc: %f' % (acc.mean()))

def evaluate(engine, folder_data, samples_per_class, folder_results, print_summary, num_epochs):
    # Set seed for reproducibility
    seed = 204

    ####################################################################################################################
    # Get data
    vsamples_per_class = FLAGS.vsamples

    # Data acquisition
    num_classes = FLAGS.num_classes
    y_train = np.empty(0)  # training
    X_train = list()
    folder_data_train = os.path.join(folder_data, 'seq_train')
    y_val = np.empty(0)  # validation
    X_val = list()
    folder_data_val = os.path.join(folder_data, 'seq_val')
    y_test = np.empty(0)  # testing
    X_test = list()
    folder_data_test = os.path.join(folder_data, 'seq_test')
    print('Getting file names for', num_classes, 'classes from folders:')
    #print(folder_data_train)
    #print(folder_data_val)
    #print(folder_data_test)
    for i in range(1, num_classes + 1):  # loop over classes

        # training: Read data file names
        folder = os.path.join(folder_data_train, str(i))  # index i marks the target class
        assert os.path.exists(folder), "Folder: " + folder + ' does not exist'
        #print('\ttraining  : Read file names from folder ', folder)
        listing = os.listdir(folder + '/')
        seq_files = [os.path.join(folder, f) for f in listing if f[-4:] == '.rec']

        # training: Randomly pick programs
        assert len(seq_files) >= samples_per_class, "Cannot sample " + str(samples_per_class) + " from " + str(
            len(seq_files)) + " files found in " + folder
        X_train += resample(seq_files, replace=False, n_samples=samples_per_class, random_state=seed)
        y_train = np.concatenate([y_train, np.array([int(i)] * samples_per_class, dtype=np.int32)])  # i becomes target

        # validation: Read data file names
        folder = os.path.join(folder_data_val, str(i))
        assert os.path.exists(folder), "Folder: " + folder + ' does not exist'
        #print('\tvalidation: Read file names from folder ', folder)
        listing = os.listdir(folder + '/')
        seq_files = [os.path.join(folder, f) for f in listing if f[-4:] == '.rec']

        # validation: Randomly pick programs
        if vsamples_per_class > 0:
            assert len(seq_files) >= vsamples_per_class, "Cannot sample " + str(vsamples_per_class) + " from " + str(
                len(seq_files)) + " files found in " + folder
            X_val += resample(seq_files, replace=False, n_samples=vsamples_per_class, random_state=seed)
            y_val = np.concatenate([y_val, np.array([int(i)] * vsamples_per_class, dtype=np.int32)])
        else:
            assert len(seq_files) > 0, "No .rec files found in" + folder
            X_val += seq_files
            y_val = np.concatenate([y_val, np.array([int(i)] * len(seq_files), dtype=np.int32)])

        # test: Read data file names
        folder = os.path.join(folder_data_test, str(i))
        assert os.path.exists(folder), "Folder: " + folder + ' does not exist'
        #print('\ttest      : Read file names from folder ', folder)
        listing = os.listdir(folder + '/')
        seq_files = [os.path.join(folder, f) for f in listing if f[-4:] == '.rec']
        assert len(seq_files) > 0, "No .rec files found in" + folder
        X_test += seq_files
        y_test = np.concatenate([y_test, np.array([int(i)] * len(seq_files), dtype=np.int32)])

    # Load dictionary and cutoff statements
    folder_vocabulary = FLAGS.vocabulary_dir
    dictionary_pickle = os.path.join(folder_vocabulary, 'dic_pickle')
    print('\tLoading dictionary from file', dictionary_pickle)
    with open(dictionary_pickle, 'rb') as f:
        dictionary = pickle.load(f)
    unk_index = dictionary[rgx.unknown_token]
    del dictionary

    # Encode source codes and get max. sequence length
    X_seq_train, maxlen_train = encode_srcs(X_train, 'training', unk_index)
    X_seq_val, maxlen_val = encode_srcs(X_val, 'validation', unk_index)
    X_seq_test, maxlen_test = encode_srcs(X_test, 'testing', unk_index)
    maxlen = max(maxlen_train, maxlen_val)
    print('Max. sequence length overall:', maxlen)
    print('Padding sequences')
    X_seq_train = pad_src(X_seq_train, maxlen, unk_index)
    X_seq_val = pad_src(X_seq_val, maxlen, unk_index)
    X_seq_test = pad_src(X_seq_test, maxlen, unk_index)
    print(X_seq_train.shape)
    print(X_seq_val.shape)
    print(X_seq_test.shape)

    # Get one-hot vectors for classification
    print('YTRAIN\n', y_train)
    print(y_train.shape)
    #y_1hot_train = get_onehot(y_train, num_classes)
    #y_1hot_val = get_onehot(y_val, num_classes)
    #y_1hot_test = get_onehot(y_test, num_classes)

    ####################################################################################################################
    # Setup paths

    # Set up names paths
    model_name = 'NCC_classifyapp_norm'
    model_path = os.path.join(folder_results,
                              "models/{}.model".format(model_name))
    predictions_path = os.path.join(folder_results,
                                    "predictions/{}.result".format(model_name))
    
    train_folder = DataFolder(X_seq_train, y_train)
    valid_folder = DataFolder(X_seq_val, y_val)
    test_folder = DataFolder(X_seq_test, y_test)
    engine.init_dataloader(train_folder, valid_folder, test_folder)
    print('Trainging.')
    engine.load_model(model_path)
    for i in range(FLAGS.num_epochs):
        engine.train()
        if i % FLAGS.save_every == 0:
            engine.predict()
            engine.save_model(model_path)

    print('Save Model.')
    engine.save_model(model_path)
    print('Testing.')
    engine.predict(is_test=True)

########################################################################################################################
# Main
########################################################################################################################
def main(argv):
    del argv    # unused

    ####################################################################################################################
    # Setup
    # Get flag values
    folder_results = FLAGS.out
    assert len(folder_results) > 0, "Please specify a path to the results folder using --folder_results"
    folder_data = FLAGS.input_data
    print_summary = FLAGS.print_summary
    num_epochs = FLAGS.num_epochs
    train_samples = FLAGS.train_samples

    # Acquire data
    if not os.path.exists(os.path.join(folder_data, 'ir_train')):
        # Download data
        task_utils.download_and_unzip('https://polybox.ethz.ch/index.php/s/JOBjrfmAjOeWCyl/download',
                                      'classifyapp_training_data', folder_data)

    task_utils.llvm_ir_to_trainable(os.path.join(folder_data, 'ir_train'))
    assert os.path.exists(os.path.join(folder_data, 'ir_val')), "Folder not found: " + folder_data + '/ir_val'
    task_utils.llvm_ir_to_trainable(os.path.join(folder_data, 'ir_val'))
    assert os.path.exists(os.path.join(folder_data, 'ir_test')), "Folder not found: " + folder_data + '/ir_test'
    task_utils.llvm_ir_to_trainable(os.path.join(folder_data, 'ir_test'))


    # Create directories if they do not exist
    if not os.path.exists(folder_results):
        os.makedirs(folder_results)
    if not os.path.exists(os.path.join(folder_results, "models")):
        os.makedirs(os.path.join(folder_results, "models"))
    if not os.path.exists(os.path.join(folder_results, "predictions")):
        os.makedirs(os.path.join(folder_results, "predictions"))

    ####################################################################################################################
    # Train model
    # Evaluate Classifyapp
    print("\nEvaluating ClassifyappInst2Vec ...")
    evaluate(Engine(FLAGS), folder_data, train_samples, folder_results, print_summary, num_epochs)


if __name__ == '__main__':
    app.run(main)