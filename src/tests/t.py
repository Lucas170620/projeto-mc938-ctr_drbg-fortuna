import math

import numpy
from scipy.special import gammainc


def approximate_entropy(sequence: str, m=10):
    """
    Note that this description is taken from the NIST documentation [1]
    [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
    As with the Serial test of Section 2.11, the focus of this test is the frequency of all possible overlapping
    m-bit patterns across the entire sequence. The purpose of the test is to compare the frequency of overlapping
    blocks of two consecutive/adjacent lengths (m and m+1) against the expected result for a random sequence.
    :param sequence: a binary string
    :param m: the length of the pattern (m)
    :return: the P value
    """
    n = len(sequence)
    # Add first m+1 bits to the end
    # NOTE: documentation says m-1 bits but that doesnt make sense, or work.
    sequence += sequence[:m + 1:]

    # Get max length one patterns for m, m-1, m-2
    max_pattern = ''
    for i in range(m + 2):
        max_pattern += '1'

    # Keep track of each pattern's frequency (how often it appears)
    vobs_one = numpy.zeros(int(max_pattern[0:m:], 2) + 1)
    vobs_two = numpy.zeros(int(max_pattern[0:m + 1:], 2) + 1)

    for i in range(n):
        # Work out what pattern is observed
        vobs_one[int(sequence[i:i + m:], 2)] += 1
        vobs_two[int(sequence[i:i + m + 1:], 2)] += 1

    # Calculate the test statistics and p values
    vobs = [vobs_one, vobs_two]
    sums = numpy.zeros(2)
    for i in range(2):
        for j in range(len(vobs[i])):
            if vobs[i][j] > 0:
                sums[i] += vobs[i][j] * math.log(vobs[i][j] / n)
    sums /= n
    ape = sums[0] - sums[1]
    chi_squared = 2.0 * n * (math.log(2) - ape)
    p_val = gammaincc(pow(2, m-1), chi_squared/2.0)
    return p_val