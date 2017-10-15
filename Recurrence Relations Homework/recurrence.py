# recurrence.py
# by James Fulford


from matplotlib import pyplot as plt


class Recurrence:
    def __init__(self, find_next, initial=None):
        self._find_next = find_next

        from inspect import getargspec
        self.count_inputs = len(getargspec(find_next)[0])
        self._recall = {}
        if initial:
            if type(initial) is dict:
                self._recall = initial
            else:
                self._recall[0] = initial

    def __call__(self, value):
        """
        Evaluates function at given value.
        Remembers past calculations.
        """
        assert type(value) is int
        if value in self._recall.keys():
            return self._recall[value]
        else:
            values = []
            for i in range(self.count_inputs):
                values.append(self(value - i - 1))
            nxt = self._find_next(*values)
            self._recall[value] = nxt
            return nxt

class SingleRecurrence(Recurrence):
    def __init__(self, find_next, initial=None):
        Recurrence.__init__(self, find_next, initial=initial)

    def putt(self, initial, epsilon=.0001, max_depth=100):
        """
        Use to detect stable equilibria near provided initial value.
        Starting at initial value, recurses max_depth times
        until changes are within epsilon of difference of each other.
        Returns a list of values to go from.
        """
        data = [initial]
        depth = 0
        x1 = initial

        close_enough = False
        while (not close_enough and dep < max_depth):
            x2 = self._find_next(x1)
            data.append(x2)
            # next value
            close_enough = abs(x2 - x1) < epsilon
            x1 = x2
            depth += 1
        return xdata, ydata

    def plot(self, initial, epsilon=.01, max_depth=100):
        """
        Sets up a cobweb plot
        """

        # Get cobweb points
        xdata = [initial]
        ydata = [0]
        depth = 0
        x1 = initial
        close_enough = False
        while depth < max_depth:
            x2 = self._find_next(x1)
            xdata.append(x1)
            ydata.append(x2)
            xdata.append(x2)
            ydata.append(x2)
            if abs(x2 - x1) < epsilon:
                print "Converging by step", depth, x1, x2
                break
            if abs(x2 - x1) > (.1 / epsilon):
                print "Diverging by step", depth, x1, x2
                break
            x1 = x2
            depth += 1

        # Set up the plot
        import numpy as np
        fix, ax = plt.subplots()
        mini, maxi = min(initial, min(xdata)), max(initial, max(xdata))
        diff = (maxi - mini) * .5
        mini, maxi = mini - diff, maxi + diff  # now lower and higher than before

        rng = np.linspace(mini, maxi, num=100)
        data = map(self._find_next, rng)
        ax.plot(rng, rng, rng, data) # y=x, y=f
        ax.plot(xdata, ydata)  # cobwebs!
        ax.grid(True, which="both")
        ax.axhline(y=0, color='k')
        ax.axvline(x=0, color='k')
        return ax
