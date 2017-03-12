#!/usr/bin/env python3
"""This shows how to run the new dynamic models (work in progress)."""
import time
import tensorflow as tf
from chatbot import DynamicBot
from data import Cornell, Ubuntu, WMT
from utils import io_utils

# ==================================================================================================
# Parser for command-line arguments.
# - Each flag below is formatted in three columns: [name] [default value] [description]
# - Each flag's value can later be accessed via: FLAGS.name
# - The flags are shown in alphabetical order (by name).
# - Example usage:
#       python3 main.py --ckpt_dir [path_to_dir] --reset_model=False --state_size=128
# ==================================================================================================

flags = tf.app.flags
# String flags -- directories and dataset name(s).
flags.DEFINE_string("ckpt_dir", "out", "Directory in which checkpoint files will be saved.")
flags.DEFINE_string("dataset", "cornell", "Dataset to use. 'ubuntu', 'cornell', or 'wmt'.")
# Boolean flags.
#flags.DEFINE_boolean("load_flags", False, "If true, use the same FLAGS as previous run.")
flags.DEFINE_boolean("reset_model", False, "wipe output directory; new params")
flags.DEFINE_boolean("decode", False, "If true, initiates chat session.")
# Integer flags.
flags.DEFINE_integer("steps_per_ckpt", 200, "How many training steps to do per checkpoint.")
flags.DEFINE_integer("batch_size", 32, "Batch size to use during training.")
flags.DEFINE_integer("vocab_size", 40000, "Number of unique words/tokens to use.")
flags.DEFINE_integer("state_size", 256, "Number of units in the RNN cell.")
flags.DEFINE_integer("embed_size", 64, "Size of word embedding dimension.")
flags.DEFINE_integer("nb_epoch", 10, "Number of epochs over full train set to run.")
# Float flags -- hyperparameters.
flags.DEFINE_float("learning_rate", 0.6, "Learning rate.")
flags.DEFINE_float("lr_decay", 0.95, "Decay factor applied to learning rate.")
flags.DEFINE_float("max_gradient", 5.0, "Clip gradients to this value.")
flags.DEFINE_float("temperature", 0.01, "Sampling temperature.")
FLAGS = flags.FLAGS

DATASET = {'ubuntu': Ubuntu,
           'cornell': Cornell,
           'wmt': WMT}

if __name__ == "__main__":

    if FLAGS.decode:
        if FLAGS.reset_model:
            print("WARNING: To chat, should pass --reset_model=False, but found True."
                  "Resetting to False.")
            FLAGS.reset_model = False

    # All datasets follow the same API, found in data/_dataset.py
    print("Setting up dataset.")
    dataset = DATASET[FLAGS.dataset](FLAGS.vocab_size)

    # Create chat model of choice. Pass in FLAGS values in case you want to change from defaults.
    print("Creating DynamicBot.")
    bot = DynamicBot(dataset,
                     ckpt_dir=FLAGS.ckpt_dir,
                     batch_size=FLAGS.batch_size,
                     state_size=FLAGS.state_size,
                     embed_size=FLAGS.embed_size,
                     learning_rate=FLAGS.learning_rate,
                     lr_decay=FLAGS.lr_decay,
                     steps_per_ckpt=FLAGS.steps_per_ckpt,
                     temperature=FLAGS.temperature,
                     is_chatting=FLAGS.decode)


    # Don't forget to compile!
    print("Compiling DynamicBot.")
    bot.compile(max_gradient=FLAGS.max_gradient, reset=FLAGS.reset_model)

    # Train an epoch on the data. CTRL-C at any time to safely stop training.
    # Model saved in FLAGS.ckpt_dir if specified, else "./out"
    if not FLAGS.decode:
        print("Training bot. CTRL-C to stop training.")
        bot.train(dataset, nb_epoch=FLAGS.nb_epoch)

    else:
        print("Initiating chat session.")
        print("Your bot has a temperature of %.2f." % FLAGS.temperature, end=" ")
        if FLAGS.temperature < 0.1:
            print("Not very adventurous, are we?")
        elif FLAGS.temperature < 0.7:
            print("This should be interesting . . . ")
        else:
            print("Enjoy your gibberish!")
        bot.decode()




