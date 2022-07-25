from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.colors import BoundaryNorm, ListedColormap
import seaborn as sns


class FieldDisplay:

    def __init__(self, field_data) -> None:
        '''The display of a data field'''

        cell_colors = ['orange', 'green', 'red', 'blue', 'gray', 'white', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'yellow']
        self.__field_cmap = ListedColormap(cell_colors)
        self.__field_bounds = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
        self.__field_norm = BoundaryNorm(self.__field_bounds, ncolors=len(cell_colors))

        grid_kws = {"height_ratios": (.9, .025), "hspace": .1}
        self.__fig, (self.__ax, self.__cbar_ax) = plt.subplots(nrows=2, figsize=(8,18), gridspec_kw=grid_kws)
        self.update_screen(field_data)

    def update_screen(self,field_data) -> None:
        '''Update the display with new data'''

        if (self.check_screen_active() == False):
            return

        sns.heatmap(field_data,
            yticklabels=2, 
            ax=self.__ax,
            cmap=self.__field_cmap,
            norm=self.__field_norm,
            cbar_ax=self.__cbar_ax,
            annot=True,     # Show value in cell
            square=True,    # Force square cells
            vmax=8,         # Ensure same color scale
            vmin=-5,        # Ensure same color scale
            cbar_kws={"orientation": "horizontal"})

        #Filter out the numbers below 1 so only the adjecent mines number is shown
        for t in self.__ax.texts:
            try:
                if (float(t.get_text()) > 0.0):
                    t.set_text(t.get_text())
                else:
                    t.set_text("")
            except:
                t.set_text("")

        colorbar = self.__ax.collections[0].colorbar
        colorbar.set_ticks([(b0+b1)/2 for b0, b1 in zip(self.__field_bounds[:-1], self.__field_bounds[1:])])
        colorbar.set_ticklabels(['Trap', 'Found', 'Bomb', 'Flag', 'Unclear', 'Clear', '                                                     Number of adjacent mines','','','','','',''])

        plt.draw()
        plt.pause(0.1)

    def check_screen_active(self) -> bool:
        '''Check if the display is still open'''

        if (plt.fignum_exists(1)):
            return True
        else:
            return False

