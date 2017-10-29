import numpy as np
import pykov
import csv

def dumb_poisson_plot(array):
    """Plot a naively created Poisson model of a volleyball dataset.

    :array: Numpy array of some volleyball data.
    :returns: Nothing.

    """
    dumb_mu = array.mean()
    samples = np.random.poisson(dumb_mu, size=array.size)

    print("Data dispersion:", array.std()**2 / array.mean())
    plt.style.use("ggplot")
    plt.hist(samples, normed=True, alpha=.8, label="Poisson samples")
    plt.hist(array, normed=True, alpha=.8, label="Volleyball data")
    plt.legend()
    plt.show()

def estimate_transition_probs(set_scores):
    """Estimate the transition probabilities for our Markov chain model.

    Our model consists of two states: "OU scores" and "Opponent scores." We
    estimate our transition probabilities with the MLE for transition
    probabilities, using every score after the first in every recorded game.
    (We consider the first score, i.e., the intial state, to be arbitrary. It
    is determined by some initial distribution.)

    :set_scores: List of lists, where each inner list is a sequence of
                 Oglethorpe scores in a set.
    :returns: 2x2 numpy matrix, approximating the transition probabilities.

    """
    # Our states are "OU scores" (1) and "OPP scores" (0).
    transition_counts = np.zeros((2, 2))

    # transition_counts[i, j] is the number of times j transitions to i. (This
    # is backwards with respect to many texts, but it's how I learned it.)

    for set_score in set_scores:
        # We can find the "OU scores" and "OPP scores" moments by taking the
        # difference of OU's score at each step. If the difference is 0, OPP
        # scored. If it is 1, OU scored.
        states = np.diff(set_score)

        for k in range(len(states) - 1):
            to_state = states[k + 1]
            from_state = states[k]
            transition_counts[to_state, from_state] += 1

    # The MLE estimator is p_{ij} = T[i, j] / Σ_k T[k, j], where T is the
    # transition count matrix.
    mle = np.zeros((2, 2))
    mle[:, 0] = transition_counts[:, 0] / sum(transition_counts[:, 0])
    mle[:, 1] = transition_counts[:, 1] / sum(transition_counts[:, 1])

    return mle

total_kills = np.array([
       11, 14, 12, 10,  9, 12, 14,  9,  9,  8,  6, 13,  5,  8,  8, 13, 15,
       10,  7,  4,  5, 12,  9, 11, 11,  4, 14,  5, 11, 12, 12, 12, 16, 12,
       17, 13, 13,  1,  7,  5, 15,  9, 13, 15,  3,  6, 12, 13, 10,  8,  5,
        5,  4,  6,  8,  8,  8,  4,  7, 10, 12, 13, 13,  6,  7,  4,  9,  7,
        5,  6, 11,  3, 12, 10,  4, 10, 10,  7, 10,  8, 13, 13, 12,  9, 14,
       12,  6,  9, 10,  6,  8,  8, 13, 11, 12,  7, 10, 12,  8,  7, 16, 15,
       11, 12,  8, 13])

total_errors = np.array([
        10,  6,  7,  5,  0,  4,  6,  7,  5, 10,  6,  4,  6,  6,  7,  4,  7,
        3,  5,  2,  4,  9,  4,  6,  7,  5,  4,  9,  7,  5,  4,  5,  3,  6,
        4,  7,  5,  9,  7,  4,  9, 12,  3,  7,  6,  6,  3,  6,  2,  5, 10,
        7,  7,  6,  3,  7,  5,  3,  5,  4, 10,  3,  5,  2,  7, 11,  2,  4,
        7, 12,  6, 11,  5, 10,  6,  4,  4,  7,  2,  1,  5,  4,  5,  5,  5,
        4,  7, 12,  5,  8,  8,  8,  5,  3,  5,  6,  5,  5,  6,  3,  2,  3,
        2,  2,  7,  3])

total_attempts = np.array([
       39, 37, 34, 45, 21, 29, 38, 28, 28, 40, 28, 41, 35, 35, 31, 37, 59,
       32, 27, 23, 25, 47, 32, 44, 48, 35, 47, 31, 45, 41, 33, 40, 34, 31,
       35, 39, 44, 19, 26, 24, 43, 45, 35, 48, 22, 41, 47, 60, 47, 33, 32,
       31, 39, 23, 20, 38, 33, 24, 37, 29, 58, 31, 42, 30, 39, 28, 41, 29,
       38, 35, 42, 35, 32, 49, 23, 39, 37, 31, 42, 29, 34, 37, 46, 31, 35,
       31, 32, 52, 53, 41, 34, 34, 46, 29, 35, 33, 35, 40, 39, 34, 19, 28,
       16, 30, 41, 32])

total_pcts = (total_kills - total_errors) / total_attempts

# Load set scores.

with open("./set_scores.csv") as f:
    reader = csv.reader(f)
    set_scores = list(reader)

# The csv module doesn't do any conversion for us, so convert the set scores
# from strings to integers.

# 2017-09-03: I note that at least one set has less than 25 plays recorded.
# This is impossible for a 25-point set, but it looks like it's only one set,
# so I don't really care right now.
set_scores = [[int(s) for s in score] for score in set_scores]

transition_matrix = estimate_transition_probs(set_scores)
P = transition_matrix
chain = pykov.Chain({
            ("OU", "OPP"): P[0, 1],
            ("OU", "OU"): P[1, 1],
            ("OPP", "OU"): P[1, 0],
            ("OPP", "OPP"): P[0, 0]})
