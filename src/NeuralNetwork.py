import unittest
from functools import reduce
from typing import List, Callable

import Math
from Perceptron import Perceptron


class Layer:
    def __init__(self, dimension: int, previous_layer_dimension: int,
                 activation: Callable[[float], float],
                 weights: List[List[float]] = None) -> None:
        """
        Initialize a layer in the Neural Network with specified dimension (
        i.e., number of neuron of current layer), previous layer dimension (
        i.e., number of inputs), activation function and optional weights for
        each neuron.
        :param dimension: Number of neuron of current layer.
        :param previous_layer_dimension: Number of inputs of current layer.
        :param activation: Activation function.
        :param weights: Optional weight.
        """
        self.__dimension__ = dimension

        if weights is None:
            weights = [None] * dimension

        assert len(weights) == dimension

        self.__neurons__ = [Perceptron(dimension=previous_layer_dimension,
                                       activation=activation,
                                       weights=weights[i])
                            for i in range(dimension)]
        self.__inputs__ = None

    def backward(self, downstream: List[float]) -> List[float]:
        """
        Based on given downstream (weight * delta) sum, let each neuron compute
        its own delta. And then compute and return all the (weight * delta)
        sum of this layer.
        :param downstream: List of downstream (weight * delta) sum for each
        neurons.
        :return: List of (weight * delta) sum of this layer.
        """

        # The length of downstream input should be the same as neuron number.
        assert len(self.__neurons__) == len(downstream)

        for p, d in zip(self.__neurons__, downstream):
            p.compute_delta(d)
        return reduce(lambda a, b: [x + y for x, y in zip(a, b)],
                      [n.weight_delta for n in self.__neurons__])

    def forward(self, inputs: List[float]) -> List[float]:
        """
        Store the given inputs and let each neuron compute its output. And
        return all the computed output in this layer.
        :param inputs: List of input values to neurons in this layer.
        :return: List of output values of neurons in this layer after feeding
        the inputs.
        """
        self.__inputs__ = inputs
        return [neuron.compute_output(self.__inputs__)
                for neuron in self.__neurons__]

    def update_weights(self) -> None:
        """
        Let each neuron update its weight based on previously computed delta.
        :return: None
        """
        for neuron in self.__neurons__:
            neuron.update_weight(self.__inputs__)


class NeuralNetwork:
    def __init__(self,
                 iteration: int,
                 input_count: int,
                 label_count: int,
                 hidden_layers: int,
                 neurons: List[int],
                 learning_rate: float = 0.1,
                 activation: Callable[[float], float] = Math.sigmoid,
                 weights: List[List[List[float]]] = None) -> None:
        """
        Initialize a Neural Network with specific max-iteration, number of
        inputs and labels, number of hidden layers and number of neuron for
        each hidden layer.
        If specified, learning rate activation function for each neuron and
        initial weights can be specified, but are considered optional.
        :param iteration: maximum number of iterations to perform.
        :param input_count: Number of inputs.
        :param label_count: Number of labels.
        :param hidden_layers: Number of hidden layers.
        :param neurons: List of neuron numbers for each hidden layers.
        :param learning_rate: Learning rate with default value of 0.1.
        :param activation: Activation function with default value of sigmoid
        function.
        :param weights: Initial weights for all neurons. Required format is
        List[List[List[float]]], which each element indicated a list of
        weights list of each neurons in a layers. Default value is None,
        indicating random generated weight is used.
        """
        self.__iteration__ = iteration
        self.__layer_num__ = hidden_layers + 1
        self.__label_count__ = label_count
        neurons.append(label_count)

        assert len(neurons) == self.__layer_num__

        if weights is None:
            weights = [None] * self.__layer_num__
        self.__layers__ = [Layer(c, p, activation, weights[i]) for i, (c, p) in
                           enumerate(zip(neurons, [input_count] + neurons))]
        self.__activation__ = activation
        self.__activation_partial__ = Math.partial(self.__activation__)

    def train_instance(self, instance) -> None:
        """
        Train the neural network with one instance.
        :param instance: Training instance, should be a List of values with
        last value as label.
        :return: None
        """

        # Extract the label from input instance.
        label = int(instance[-1])
        # Create binary representation of extracted label.
        labels = [0 for _ in range(self.__label_count__)]
        labels[label] = 1

        # Extract the inputs values from input instance.
        inputs = instance[:-1]

        # Feed the first layer with extracted inputs. After computing output,
        # iteratively feed each layer's output to its next layer. After
        # iteration finished,  ``inputs`` stores the final output value of the
        # output layer.
        for layer in self.__layers__:
            inputs = layer.forward(inputs)

        # Compute the Backpropagation inputs. Specifically, for output layer,
        #  the input is the different of label and output.
        inputs = [target - output for target, output in zip(labels, inputs)]

        # Feed the input just computed to each layer backward. After
        # computing delta, iteratively feed each layer's delta and weight sum
        # to its previous layer.
        for layer in self.__layers__[::-1]:
            inputs = layer.backward(inputs)

        # Update weights in each layer.
        for layer in self.__layers__:
            layer.update_weights()

    def test_instance(self, instance) -> bool:
        label = int(instance[-1])

        inputs = instance[:-1]

        for layer in self.__layers__:
            inputs = layer.forward(inputs)

        return label == inputs.index(max(inputs))

    def train(self, instances) -> None:
        for _ in range(self.__iteration__):
            for instance in instances:
                self.train_instance(instance)

    def test(self, instances) -> float:
        positive = 0
        for instance in instances:
            if self.test_instance(instance):
                positive += 1
        return positive / len(instances)

    def __str__(self) -> str:
        ret = ''
        for i, layer in enumerate(self.__layers__):
            ret += 'Layer ' + str(i) + '\n'
            for j, n in enumerate(layer.__neurons__):
                ret += '\tNeuron ' + str(j) + ' weight: ' + str(n) + '\n'
        return ret


class TestNeuralNetwork(unittest.TestCase):
    """ This class is for testing the function of NeuralNetwork class. """

    # def test_train_instance(self) -> None:
    #     nn = NeuralNetwork(iteration=200,
    #                        input_count=3,
    #                        label_count=2,
    #                        hidden_layers=1,
    #                        neurons=[2],
    #                        weights=[[[-0.4, 0.2, 0.4, 0.1],
    #                                  [0.2, -0.5, -0.3, -0.2]],
    #                                 [[0.1, -0.3, -0.2], [1., 1., 1.]]])
    #
    #     print(nn)
    #
    #     nn.train_instance([1, 0, 1, 1])
    #
    #     print(nn)

    # def test_test_instance(self) -> None:
    #     pass

    def test_test(self) -> None:
        import pandas as pd
        train_data = pd.read_csv('../adult.csv')

        train_data_m = train_data.as_matrix()

        # print(train_data_m[0])

        nn = NeuralNetwork(iteration=200,
                           input_count=14,
                           label_count=2,
                           hidden_layers=5,
                           neurons=[10, 10, 10, 10, 10])
        print(nn)

        nn.train(train_data_m)

        print(nn)

        print(nn.test(train_data_m))

        # nn = NeuralNetwork(iteration=2000,
        #                    input_count=4,
        #                    label_count=3,
        #                    hidden_layers=5,
        #                    neurons=[4, 4, 4, 4, 4])
        # print(nn)
        # import pandas as pd
        # train_data = pd.read_csv('../iris.csv')
        # nn.train(train_data.as_matrix())
        # print(nn.test(train_data.as_matrix()))
        # print(nn)
        # pass


if __name__ == '__main__':
    unittest.main()
