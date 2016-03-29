from numpy import argsort, nonzero, genfromtxt, array
from scipy.ndimage import minimum_filter
from sklearn.metrics import precision_recall_curve, precision_score
from matplotlib import pyplot as plt
from sklearn.preprocessing import normalize


class Evaluation(object):
    def __init__(self, query, target, dt, limit, scale=1):
        self.query = query
        self.target = target
        self.dt = dt
        self.limit = limit

        self.minimum = self.find_local_minima()
        self.found_symbols = self.extract_found_symbols()

    def find_local_minima(self):
        size = min(self.dt.sum_dt.shape[1], self.dt.sum_dt.shape[0]) // 10

        res = minimum_filter(self.dt.sum_dt, size=size, mode="nearest")
        x, y = nonzero(res == self.dt.sum_dt)
        order = argsort(self.dt.sum_dt[x, y])
        x, y = x[order], y[order]
        return x[0:self.limit], y[0:self.limit]

    def extract_found_symbols(self):
        found_symbols = list()

        height, width = self.query.original_array.shape

        for (y, x) in zip(*self.minimum):
            begin_bbox_y = y - self.query.root_node.position[0]
            begin_bbox_x = x - self.query.root_node.position[1]
            box = self.target.original_array[begin_bbox_y:begin_bbox_y + height, begin_bbox_x:begin_bbox_x + width]
            found_symbols.append((box, self.dt.sum_dt[y, x]))

        return found_symbols


class PR(object):
    def __init__(self, path):
        self.eva_array = array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        self.probs_pred = genfromtxt(path + "/normal_eva_33x30.csv", delimiter=';')

        self.calculate_precision_recall()

    def calculate_precision_recall(self):
        p, r, t = precision_recall_curve(self.eva_array, self.probs_pred[0])

        plt.plot(r, p, label="Precision-Recall curve")
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.show()
