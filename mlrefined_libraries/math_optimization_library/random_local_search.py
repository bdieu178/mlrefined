# import custom JS animator
from mlrefined_libraries.JSAnimation_slider_only import IPython_display_slider_only

# import standard plotting and animation
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from IPython.display import clear_output
import time
from matplotlib import gridspec
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch
from matplotlib.text import Annotation
from mpl_toolkits.mplot3d.proj3d import proj_transform

# import autograd functionality
from autograd import grad as compute_grad   # The only autograd function you may ever need
import autograd.numpy as np
import math
import copy

# random local search function
def random_local_search(func,pt,max_its,num_samples,steplength):
    
    # starting point evaluation
    current_eval = func(pt)
    current_pt = pt
    
    # loop over max_its descend until no improvement or max_its reached
    pt_history = [current_pt]
    eval_history = [current_eval]
    for i in range(max_its):
        # loop over num_samples, randomly sample direction and evaluate, move to best evaluation
        swap = 0
        keeper_pt = current_pt
        for j in range(num_samples):
            # produce direction
            theta = np.random.rand(1)
            x = steplength*np.cos(2*np.pi*theta)
            y = steplength*np.sin(2*np.pi*theta)
            new_pt = np.asarray([x,y])
            temp_pt = copy.deepcopy(keeper_pt) 
            new_pt += temp_pt
            
            # evaluate new point
            new_eval = func(new_pt)
            if new_eval < current_eval:
                current_pt = new_pt
                current_eval = new_eval
                swap = 1
        
        # if nothing has changed
        if swap == 1:
            pt_history.append(current_pt)
            eval_history.append(current_eval)
    
    # translate to array, reshape appropriately
    pt_history = np.asarray(pt_history)
    pt_history.shape = (np.shape(pt_history)[0],np.shape(pt_history)[1])

    eval_history = np.asarray(eval_history)
    eval_history.shape = (np.shape(eval_history)[0],np.shape(eval_history)[1])

    return pt_history,eval_history
    
# animator for recursive function
def visualize3d(func,**kwargs):
    ### input arguments ###        
    wmax = 1
    if 'wmax' in kwargs:
        wmax = kwargs['wmax'] + 0.5
        
    view = [20,-50]
    if 'view' in kwargs:
        view = kwargs['view']
        
    num_contours = 10
    if 'num_contours' in kwargs:
        num_contours = kwargs['num_contours']
        
    pt = [0,0]
    if 'pt' in kwargs:
        pt = kwargs['pt']
    pt = np.asarray(pt)
    pt.shape = (2,1)
     
    max_its = 10
    if 'max_its' in kwargs:
        max_its = kwargs['max_its']
    num_samples = 10
    if 'num_samples' in kwargs:
        num_samples = kwargs['num_samples'] 
    steplength = 1
    if 'steplength' in kwargs:
        steplength = kwargs['steplength']     
        
    ##### construct figure with panels #####
    # construct figure
    fig = plt.figure(figsize = (7,3))
          
    # remove whitespace from figure
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1) # remove whitespace
    fig.subplots_adjust(wspace=0.01,hspace=0.01)
        
    # create subplot with 3 panels, plot input function in center plot
    gs = gridspec.GridSpec(1, 2, width_ratios=[1,1]) 
    ax = plt.subplot(gs[0],projection='3d'); 
    ax2 = plt.subplot(gs[1]); 
    
    #### define input space for function and evaluate ####
    w = np.linspace(-wmax,wmax,200)
    w1_vals, w2_vals = np.meshgrid(w,w)
    w1_vals.shape = (len(w)**2,1)
    w2_vals.shape = (len(w)**2,1)
    h = np.concatenate((w1_vals,w2_vals),axis=1)
    func_vals = np.asarray([func(s) for s in h])
    w1_vals.shape = (len(w),len(w))
    w2_vals.shape = (len(w),len(w))
    func_vals.shape = (len(w),len(w))
    
    # plot function 
    ax.plot_surface(w1_vals, w2_vals, func_vals, alpha = 0.1,color = 'w',rstride=25, cstride=25,linewidth=1,edgecolor = 'k',zorder = 2)

    # plot z=0 plane 
    ax.plot_surface(w1_vals, w2_vals, func_vals*0, alpha = 0.1,color = 'w',zorder = 1,rstride=25, cstride=25,linewidth=0.3,edgecolor = 'k') 
    
    ### make contour right plot 
    ax2.contour(w1_vals, w2_vals, func_vals,num_contours,colors = 'k')
    
    #### run local random search algorithm ####
    pt_history,eval_history = random_local_search(func,pt,max_its,num_samples,steplength)

    # colors for points
    s = np.linspace(0,1,len(eval_history[:round(len(eval_history)/2)]))
    s.shape = (len(s),1)
    t = np.ones(len(eval_history[round(len(eval_history)/2):]))
    t.shape = (len(t),1)
    s = np.vstack((s,t))
    colorspec = []
    colorspec = np.concatenate((s,np.flipud(s)),1)
    colorspec = np.concatenate((colorspec,np.zeros((len(s),1))),1)
    
    #### scatter path points ####
    for k in range(len(eval_history)):
        ax.scatter(pt_history[k,0],pt_history[k,1],0,s = 60,c = colorspec[k],edgecolor = 'k',linewidth = 2,zorder = 3)
        
        ax2.scatter(pt_history[k,0],pt_history[k,1],s = 60,c = colorspec[k],edgecolor = 'k',linewidth = 2,zorder = 3)

    #### connect points with arrows ####
    for i in range(len(eval_history)-1):
        pt1 = pt_history[i]
        pt2 = pt_history[i+1]
        
        # draw arrow in left plot
        a = Arrow3D([pt1[0],pt2[0]], [pt1[1],pt2[1]], [0, 0], mutation_scale=10, lw=2, arrowstyle="-|>", color="k")
        ax.add_artist(a)
                
        # draw 2d arrow in right plot
        ax2.arrow(pt1[0],pt1[1],(pt2[0] - pt1[0])*0.85,(pt2[1] - pt1[1])*0.85, head_width=0.1, head_length=0.1, fc='k', ec='k',linewidth=3,zorder = 2,length_includes_head=True)

    ### cleanup panels ###
    ax.set_xlabel('$w_1$',fontsize = 12)
    ax.set_ylabel('$w_2$',fontsize = 12,rotation = 0)
    ax.set_title('$g(w_1,w_2)$',fontsize = 12)
    ax.view_init(view[0],view[1])
    
    # clean up axis
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    ax.xaxis.pane.set_edgecolor('white')
    ax.yaxis.pane.set_edgecolor('white')
    ax.zaxis.pane.set_edgecolor('white')
    
    ax.xaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.yaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.zaxis._axinfo["grid"]['color'] =  (1,1,1,0)

    '''
    ax.set_xticks([-1,0,1])
    ax.set_xticklabels([-1,0,1])
    
    ax.set_yticks([-1,0,1])
    ax.set_yticklabels([-1,0,1])
    
    ax.set_zticks([0,1,2])
    ax.set_zticklabels([0,1,2])
    '''
    
    # plot
    plt.show()

#### custom 3d arrow and annotator functions ###    
# nice arrow maker from https://stackoverflow.com/questions/11140163/python-matplotlib-plotting-a-3d-cube-a-sphere-and-a-vector
class Arrow3D(FancyArrowPatch):

    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)

# great solution for annotating 3d objects - from https://datascience.stackexchange.com/questions/11430/how-to-annotate-labels-in-a-3d-matplotlib-scatter-plot
class Annotation3D(Annotation):
    '''Annotate the point xyz with text s'''

    def __init__(self, s, xyz, *args, **kwargs):
        Annotation.__init__(self,s, xy=(0,0), *args, **kwargs)
        self._verts3d = xyz        

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.xy=(xs,ys)
        Annotation.draw(self, renderer)        

def annotate3D(ax, s, *args, **kwargs):
    '''add anotation text s to to Axes3d ax'''

    tag = Annotation3D(s, *args, **kwargs)
    ax.add_artist(tag)