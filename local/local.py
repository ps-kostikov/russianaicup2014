import shortcuts
import environment
import geometry
import measurements
import prediction

import pickle


def make_start_env_im_left():
    with open('local/start_env_im_left.pickle') as inf:
        return pickle.load(inf)


env = make_start_env_im_left()
# print measurements.test(env)
# print measurements.count_chances(env)
import ipdb; ipdb.set_trace()