# carry out the rebuttal experiments
# differentiate function words and content words
# and compute the corresponding sentence entropy respectively
# Yang Xu
# 5/1/2016

from pynlpl.lm.lm import ARPALanguageModel

# main
if __name__ == '__main__':
    models_path = '/Users/yangxu/Documents/workspace/swbdShuffleLM/models'

    for fold_id in range(0, 10):
        for sent_id in range(1, 101):
            model_file = models_path + '/testFold{}_sentId{}.arpa'.format(fold_id, sent_id)
            model = ARPALanguageModel(model_file)
