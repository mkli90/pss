# -*- encoding: utf-8 -*-
from logging import getLogger
from math import ceil

from matplotlib.patches import Rectangle
from matplotlib.pyplot import subplots, cm, show
from numpy import min, max, invert, savetxt

gui_logger = getLogger("SymbolGroupDisplay")

SPACE = .05
POSITION = .98
FIG_POS = (5, 5)
ROWS = 1
COLUMNS = 1
FONTSIZE = 20
NODESIZE = 10
SAVE_PATH = "./"


def setup_figure(name, rows=ROWS, cols=COLUMNS):
    """
    This sets up the plot-figures, respectively the window.
    :param name: The name to set the windows title
    :return: The two empty subplots for the original image and the skeletonized one
    """
    fig, ax = subplots(rows, cols, figsize=FIG_POS, sharex=True, sharey=True,
                       subplot_kw={'adjustable': 'box-forced'})
    fig.canvas.set_window_title("name: [{}]".format(name))
    fig.subplots_adjust(wspace=SPACE, hspace=SPACE, top=POSITION,
                        bottom=SPACE, left=SPACE, right=POSITION)
    return fig, ax


def setup_plot(ax, array, title):
    """
    :param ax: Empty subplot for the original image or the skeletonized image
    :param array: The array to fill up the subplot
    :param title: Title of the subplot

    This fills up the subplots
    """
    ax.axis('on')
    ax.set_xlim([0, array.shape[1]])
    ax.set_ylim([array.shape[0], 0])
    ax.set_title(title, fontsize=FONTSIZE)


def draw_array(ax, array):
    """
    Fills the AxisSubplot with the array to draw
    :param ax: AxisSubplot to draw on
    :param array: Array to draw onto AxisSubplot
    """
    ax.imshow(array, cmap=cm.gray)


class GUIHandler(object):
    """
    This class starts up all the gui wanted.
    """
    def __init__(self):
        gui_logger.info("GUIHandler started")

    @staticmethod
    def display_query(query, index):  # pragma: no cover
        """
        Plots the query entered in different forms
        :param query: The query image to plot
        """
        QueryPlot(query, index)

    @staticmethod
    def display_target(target, index):
        TargetPlot(target, index)

    @staticmethod
    def display_distance_transform(dt, index):
        """
        Plots the summed up distance transform for the target image
        :param dt: TargetDistanceTransform-object, which holds summed up distance transform
        """
        DistanceTransformPlot(dt, index)

    @staticmethod
    def display_evaluation(eval, index):
        """
        Plots the target image with embedded bounding boxes and a list of the top n results
        :param eval: Evaluation Object
        :param index: Index of the query
        """
        EvaluationPlot(eval, index)

    @staticmethod
    def show():
        """
        Fires up the matplotlib method show
        """
        show()


class EvaluationPlot(object):
    """
    This plots the Evaluation object
    """
    def __init__(self, eval, index):
        self.index = index
        self.create_eval_figure("evaluation", eval)
        self.shape = eval.dt.sum_dt.shape
        self.sum_dt = eval.dt.sum_dt

    def create_eval_figure(self, name, eval):
        name = name.replace("/", "_")
        fig, ax = setup_figure(name)
        setup_plot(ax, eval.dt.sum_dt, name)
        # self.draw_distance_transform(ax, eval)
        self.draw_target_image(ax, eval.target.original_array)
        self.draw_minima(ax, eval)
        self.draw_found_symbols(eval, name)
        ax.format_coord = self.format_coord
        fig.savefig(SAVE_PATH + str(self.index) + "/" + name, dpi=300)

    def format_coord(self, x, y):
        """
        For the distance transforms the displayed info is altered to also show the value of the DT
        :param x: x of the cell which the mouse points to
        :param y: y of the cell which the mouse points to
        """
        col = int(x+0.5)
        row = int(y+0.5)
        if 0 <= col < self.shape[1] and 0 <= row < self.shape[0]:
            value = self.sum_dt[row,col]
            return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, value)
        else:
            return 'x=%1.4f, y=%1.4f'%(x, y)

    def draw_minima(self, ax, eval):
        shape = eval.found_symbols[0][0].shape

        ax.plot(eval.minimum[1], eval.minimum[0], 'r.')

        for (i, j) in zip(*eval.minimum):
            x = j - eval.query.root_node.position.item(1)
            y = i - eval.query.root_node.position.item(0)
            ax.add_patch(Rectangle((x, y), shape[1], shape[0], fill=None, ec="red"))

    @staticmethod
    def draw_distance_transform(ax, eval):
        ax.imshow(eval.dt.sum_dt, cmap=cm.jet, vmin=min(eval.dt.sum_dt), vmax=max(eval.dt.sum_dt))

    def draw_found_symbols(self, eval, name):
        results_number = len(eval.found_symbols)
        max_rows = ceil(results_number / 5)

        fig, axes = subplots(1, results_number, sharex=False, sharey=False)
        fig.canvas.set_window_title("name: [{}]".format("Found"))

        i = 0
        j = 0
        for found_symbol in eval.found_symbols:
            col = i
            if len(eval.found_symbols) > 1:
                axes[col].set_xlabel("{0:.2f}".format(found_symbol[1]))
                axes[col].get_xaxis().set_ticks([])
                axes[col].get_xaxis().set_visible(True)
                axes[col].get_yaxis().set_visible(False)
                axes[col].imshow(found_symbol[0], cmap=cm.gray)
            else:
                axes.set_xlabel("{0:.2f}".format(found_symbol[1]))
                axes.get_xaxis().set_ticks([])
                axes.get_xaxis().set_visible(True)
                axes.get_yaxis().set_visible(False)
                axes.imshow(found_symbol[0], cmap=cm.gray)
            if col == 4:
                j += 1
            i += 1
        values = [x[1] for x in eval.found_symbols]
        fig.set_size_inches(15, 5)
        fig.savefig(SAVE_PATH + str(self.index) + "/found", dpi=300)
        savetxt(SAVE_PATH + "values/found_value_" + str(self.index) + ".csv", values, newline=";")

    def draw_target_image(self, ax, target):
        draw_array(ax, target)


class TargetPlot(object):
    def __init__(self, target, index):
        self.index = index
        self.create_target_figure("target", target.original_array, "Target")

    def create_target_figure(self, name, original_array, title):
        fig, ax = setup_figure(name, 1, 1)
        setup_plot(ax, original_array, title)
        self.draw_target_image(ax, original_array)
        fig.savefig(SAVE_PATH + str(self.index) + "/" + name, dpi=300)

    @staticmethod
    def draw_target_image(ax, target):
        draw_array(ax, target)


class DistanceTransformPlot(object):
    def __init__(self, dt, index):
        self.index = index
        self.create_distance_transform_figure("dt_single_node", dt, "Distance Transform (Single Node)")

    def create_distance_transform_figure(self, name, dt, title):
        fig, ax = setup_figure(name)
        setup_plot(ax, dt.root_dt_normalized, title)
        self.draw_distance_transform(ax, dt.root_dt_normalized, min(dt.root_dt_normalized), max(dt.root_dt_normalized))
        fig.savefig(SAVE_PATH + str(self.index) + "/" + name, dpi=300)

    @staticmethod
    def draw_distance_transform(ax, dt, vmin, vmax):
        ax.imshow(dt, cmap=cm.jet, vmin=vmin, vmax=vmax)


class QueryPlot(object):  # pragma: no cover
    """
    This class is responsible for plotting the Query.
    """

    def __init__(self, query, index):
        self.index = index
        self.create_original_image_figure(query)
        self.create_skeleton_figure(query)
        self.create_tree_figure(query)

    def create_skeleton_figure(self, query):
        name = query.name + "_skeleton"
        name = name.replace("/", "_")
        fig, ax = setup_figure(name)
        setup_plot(ax, query.original_array, "skeleton")
        self.draw_skeleton_image(ax, invert(query.skeleton))
        fig.savefig(SAVE_PATH + str(self.index) + "/" + name, dpi=300)

    def create_original_image_figure(self, query):
        name = query.name + "_original"
        name = name.replace("/", "_")
        fig, ax = setup_figure(name)
        setup_plot(ax, query.original_array, "original")
        draw_array(ax, invert(query.original_array))
        fig.savefig(SAVE_PATH + str(self.index) + "/" + name, dpi=300)

    def create_tree_figure(self, query):
        name = query.name + "_tree"
        name = name.replace("/", "_")
        fig, ax = setup_figure(name)
        setup_plot(ax, query.original_array, "tree")
        root_node = query.root_node
        center_of_mass = query.center_of_mass
        self.draw_tree_image(ax, root_node, center_of_mass)
        fig.savefig(SAVE_PATH + str(self.index) + "/" + name, dpi=300)

    def draw_skeleton_image(self, ax, array):
        """
        Draws skeletonized version of the original array
        :param ax: AxisSubplot to draw on
        :param array: Skeletonized-Array to draw onto AxisSubplot
        """
        draw_array(ax, array)

    def draw_tree_image(self, ax, root_node, center_of_mass):
        """
        Draws tree
        :param ax: AxisSubplot to draw on
        :param root_node: Root-Node (is drawn green)
        :param center_of_mass: Center-Of-Mass Node (is drawn red)
        """
        self.plot_center_of_mass(ax, center_of_mass)

        open_list = list()
        open_list.append(root_node)

        while len(open_list) > 0:
            current_node = open_list.pop()
            for child in current_node.children:
                open_list.append(child)
                self.plot_edge(ax, current_node, child)

        self.plot_root_node(ax, root_node)

    @staticmethod
    def plot_nodes(ax, nodes):
        """
        Plots the Nodes onto a subplot
        :param ax: Subplot to plot onto
        :param nodes: Nodes-Array to draw the nodes for
        """
        if nodes is not None and len(nodes) > 0:
            for node in nodes:
                ax.plot(node.position.item(1), node.position.item(0), "yo", markersize=NODESIZE)

    @staticmethod
    def plot_center_of_mass(ax, center_of_mass):
        """
        Plots the center of mass into a given subplot
        :param ax: Subplot to draw the center of mass into
        :param center_of_mass: Center of mass to draw to the subplot
        """
        if center_of_mass is not None:
            ax.plot(center_of_mass.position.item(1), center_of_mass.position.item(0), "go", markersize=NODESIZE)

    @staticmethod
    def plot_root_node(ax, root_node):
        """
        Highlights the root node, which is the node closest to the center of mass
        :param ax: Subplot to draw the root node into
        :param root_node: Root-Node to highlight
        """
        if root_node is not None:
            ax.plot(root_node.position.item(1), root_node.position.item(0), "go", markersize=NODESIZE)

    @staticmethod
    def plot_edge(ax, parent, child):
        """
        This plots edge between parent-child relation
        :param ax: Subplot to draw the edge into
        :param parent: Parent of the relation
        :param child: Child of the Relation
        """
        ax.plot([parent.position[1], child.position[1]], [parent.position[0], child.position[0]], "b-")
        ax.plot(child.position.item(1), child.position.item(0), "y.", markersize=NODESIZE)


pn_logger = getLogger("PrintNodes")


class PrintNodes(object):  # pragma: no cover
    """
    Prints the Nodes locations to the log
    """

    def __init__(self, symbol_group):
        """
        Initialized the PrintNodes-object for a given SymbolGroup
        :param symbol_group: SymbolGroup, which contains the Nodes to print into the log
        """
        self.symbol_group = symbol_group
        self.print_positions()

    def print_positions(self):
        """
        Prints the Nodes
        """
        for node in self.symbol_group.nodes:
            pn_logger.info(node)
