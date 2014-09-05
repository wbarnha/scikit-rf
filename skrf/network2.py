
from traits.api import  *

from .frequency import Frequency
from .mathFunctions import *
from .plotting import plot_complex_rectangular,plot_rectangular, smith
from scipy import fft 
import numpy as npy
import pylab as plb

from IPython.display import Image, SVG, Math
from IPython.core.pylabtools import print_figure

from abc import ABCMeta, abstractmethod

      
class Parameter(object):
    '''
    a complex network parameter
    '''
    
    def __init__(self,  network):
        self._network = network
        self.db10 = Db10(self)
        self.db20 = Db20(self)
        self.db = self.db20 # 
        self.deg = Deg(self)
        self.deg = Rad(self)
        
    def __getattr__(self,name):
        return getattr(self.val,name)  
    @property
    def val(self):
        raise NotImplementedError()
    def __getitem__(self,key):
        return self.val[key]
    
    
    def plot(self, m=None, n=None, ax=None, show_legend=True,*args, 
             **kwargs):

        # create index lists, if not provided by user
        if m is None:
            M = range(self._network.nports)
        else:
            M = [m]
        if n is None:
            N = range(self._network.nports)
        else:
            N = [n]

        if 'label'  not in kwargs.keys():
            gen_label = True
        else:
            gen_label = False

        
        #was_interactive = plb.isinteractive
        #if was_interactive:
        #    plb.interactive(False)
        lines = []
        for m in M:
            for n in N:
                # set the legend label for this trace to the networks
                # name if it exists, and they didnt pass a name key in
                # the kwargs
                if gen_label:
                    if self._network.name is None:
                        if plb.rcParams['text.usetex']:
                            label_string = '$%s_{%i%i}$'%\
                            (str(self).upper(),m+1,n+1)
                        else:
                            label_string = '%s%i%i'%\
                            (str(self).upper(),m+1,n+1)
                    else:
                        if plb.rcParams['text.usetex']:
                            label_string = str(self._network)+', $%s_{%i%i}$'%\
                            (str(self).upper(),m+1,n+1)
                        else:
                            label_string = self._network.name+', %s%i%i'%\
                            (str(self).upper(),m+1,n+1)
                    kwargs['label'] = label_string

                # plot the desired attribute vs frequency
                lines.append(plot_complex_rectangular(
                    z = self.val[:,m,n],
                    show_legend = show_legend, ax = ax,
                    *args, **kwargs))#[0]) ## fix 
        #return lines ## fix
    def plot_smith(self, **kwargs):
        self.plot(**kwargs)
        smith()
        
    def _figure_data(self, format):
        fig, ax = plb.subplots()
        self.plot(ax=ax)
        data = print_figure(fig, format)
        plb.close(fig)
        return data
    
    def _repr_png_(self):
        return self._figure_data('png')
    
    @property
    def png(self):
        return Image(self._repr_png_(), embed=True)

class S(Parameter):
    '''
    S parameters 
    
    this Parameter is special, because they are the internal storage format 
    
    '''
    def __init__(self,  network, s):
        Parameter.__init__(self, network)
        s = fix_s_shape(s)
        self._val= npy.array(s,dtype=complex)
    
   
    def __str__(self): return 's'
    
    @property
    def val(self):
        return self._val
    
class Z(Parameter):
    '''
    Impedance parameters
    '''
    def __str__(self): return 'z'
    @property
    def val(self):
        return s2z(self._network.s.val)
        
class Y(Parameter):
    def __str__(self): return 'y'
    @property
    def val(self):
        return s2y(self._network.s.val)

class T(Parameter):
    def __str__(self): return 't'
    @property
    def val(self):
        return s2t(self._network.s.val)
    

class Projection(object):
    '''
    a scalar projection of a parameter
    '''
    def __init__(self, param):
        self._param = param 
        self._network = param._network 
    
    def __getitem__(self,key):
        return self.val[key]
    def __getattr__(self,name):
        return getattr(self.val,name)
    
    @property
    def val(self):
        raise NotImplementedError()
    
    def plot(self,  m=None, n=None, ax=None, show_legend=True,*args, 
             **kwargs):

        # create index lists, if not provided by user
        if m is None:
            M = range(self._network.nports)
        else:
            M = [m]
        if n is None:
            N = range(self._network.nports)
        else:
            N = [n]

        if 'label'  not in kwargs.keys():
            gen_label = True
        else:
            gen_label = False

        lines = [] #list of mpl lines
        for m in M:
            for n in N:
                # set the legend label for this trace to the networks
                # name if it exists, and they didnt pass a name key in
                # the kwargs
                if gen_label:
                    if self._network.name is None:
                        if plb.rcParams['text.usetex']:
                            label_string = '$%s_{%i%i}$'%\
                            (str(self._param).upper(),m+1,n+1)
                        else:
                            label_string = '%s%i%i'%\
                            (str(self._param).upper(),m+1,n+1)
                    else:
                        if plb.rcParams['text.usetex']:
                            label_string = self._network.name+', $%s_{%i%i}$'%\
                            (str(self._param).upper(),m+1,n+1)
                        else:
                            label_string = self._network.name+', %s%i%i'%\
                            (str(self._param).upper(),m+1,n+1)
                    kwargs['label'] = label_string

                # plot the desired attribute vs frequency
                if 'time' in str(self._param): 
                    x_label = 'Time (ns)'
                    x = self._network.frequency.t_ns
                    
                else:
                    x_label = 'Frequency (%s)'%self._network.frequency.unit
                    x = self._network.frequency.f_scaled
                
                
                lines.append(plot_rectangular(
                        x = x,
                        y = self.val[:,m,n],
                        x_label = x_label,
                        y_label = self.y_label,
                        show_legend = show_legend, ax = ax,
                        *args, **kwargs)[0])
        return lines
    
    def _figure_data(self, format):
        fig, ax = plb.subplots()
        self.plot(ax=ax)
        data = print_figure(fig, format)
        plb.close(fig)
        return data
    
    def _repr_png_(self):
        return self._figure_data('png')
    
    @property
    def png(self):
        return Image(self._repr_png_(), embed=True)
  
class Db10(Projection):
    y_label = 'Magnitude (dB)'
    unit='dB'
    def __str__(self):
        return 'dB'
    def __repr__(self):
        return '{self._param}{self}'.format(self=self)
    
    @property
    def val(self):
        return complex_2_db10(self._param.val)

class Db20(Projection):
    y_label = 'Magnitude (dB)'
    unit = 'dB'
    def __str__(self):
        return 'dB'
    def __repr__(self):
        return '{self._param}{self}'.format(self=self)
    @property
    def val(self):
        return complex_2_db(self._param.val)
                
class Deg(Projection):
    y_label = 'Phase (deg)'
    unit = 'deg'
    def __str__(self):
        return 'deg'
    def __repr__(self):
        return '{self._param}{self}'.format(self=self)
    @property
    def val(self):
        return complex_2_degree(self._param.val)

class Rad(Projection):
    y_label = 'Phase (rad)'
    unit = 'rad'
    def __str__(self):
        return 'rad'
    def __repr__(self):
        return '{self._param}{self}'.format(self=self)
    @property
    def val(self):
        return complex_2_radian(self._param.val)

  
class Network(object):
    def __init__(self, frequency=None,s=None,z0=50,name = ''):
            
        self.frequency = frequency
        self.s = s
        self.z0 = z0
        self.name = name
    
    @property
    def s(self):
        '''
        my docstring
        '''
        return self._s
        
    @s.setter
    def s(self,s):
        self._s = S(self, s)
    
    @property
    def z(self):
        return Z(self)
        
    @z.setter
    def z(self,z):
        s = z2s(z,self.z0)
        self._s =  S(self, s)
        
    
    @classmethod
    def from_z(cls, z, z0=50, **kwargs):
        return cls(s = z2s(z,z0), **kwargs)
    
    @classmethod
    def from_y(cls, y, z0=50, **kwargs):
        return cls(s = y2s(y,z0), **kwargs)
            
    @classmethod
    def from_ntwkv1( cls, network):
        return cls(frequency = network.frequency,
                   s = network.s,
                   name = network.name,
                   )
        
        
    @property
    def nports(self):
        '''
        the number of ports the network has.

        Returns
        --------
        nports : number
                the number of ports the network has.

        '''
        try:
            return self.s.val.shape[1]
        except (AttributeError):
            return 0

    @property
    def z0(self):
        return self._z0
    
    @z0.setter
    def z0(self,z0):
        self._z0 = fix_z0_shape(z0, len(self.frequency),nports=self.nports)
        
       
def fix_z0_shape( z0, nfreqs, nports):
    '''
    Make a port impedance of correct shape for a given network's matrix 
    
    This attempts to broadcast z0 to satisy
        npy.shape(z0) == (nfreqs,nports)
    
    Parameters 
    --------------
    z0 : number, array-like
        z0 can be: 
        * a number (same at all ports and frequencies)
        * an array-like of length == number ports.
        * an array-like of length == number frequency points.
        * the correct shape ==(nfreqs,nports)
    
    nfreqs : int
        number of frequency points
    nportrs : int
        number of ports
        
    Returns
    ----------
    z0 : array of shape ==(nfreqs,nports)
        z0  with the right shape for a nport Network

    Examples
    ----------
    For a two-port network with 201 frequency points, possible uses may
    be
    
    >>> z0 = rf.fix_z0_shape(50 , 201,2)
    >>> z0 = rf.fix_z0_shape([50,25] , 201,2)
    >>> z0 = rf.fix_z0_shape(range(201) , 201,2)

        
    '''
    
    
    
    if npy.shape(z0) == (nfreqs, nports):
        # z0 is of correct shape. super duper.return it quick.
        return z0.copy() 
    
    elif npy.isscalar(z0):
        # z0 is a single number
        return npy.array(nfreqs*[nports * [z0]])
    
    elif len(z0)  == nports:
        # assume z0 is a list of impedances for each port, 
        # but constant with frequency 
        return npy.array(nfreqs*[z0])
        
    elif len(z0) == nfreqs:
        # assume z0 is a list of impedances for each frequency,
        # but constant with respect to ports
        return npy.array(nports * [z0]).T
        
    else: 
        raise IndexError('z0 is not acceptable shape')

def fix_s_shape(s):
    s_shape= npy.shape(s)
    if len(s_shape) <3:
        if len(s_shape) == 2:
            # reshape to kx1x1, this simplifies indexing in function
            s = npy.reshape(s,(-1,s_shape[0],s_shape[0]))
        else:
            s = npy.reshape(s,(-1,1,1))
    return s
  
## network parameter conversion       
  
def s2z(s,z0=50):
    '''
    Convert scattering parameters [1]_ to impedance parameters [2]_


    .. math::
        z = \\sqrt {z_0} \\cdot (I + s) (I - s)^{-1} \\cdot \\sqrt{z_0}

    Parameters
    ------------
    s : complex array-like
        scattering parameters
    z0 : complex array-like or number 
        port impedances.                                         

    Returns
    ---------
    z : complex array-like
        impedance parameters

    
        
    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/S-parameters
    .. [2] http://en.wikipedia.org/wiki/impedance_parameters
    
    '''
    nfreqs, nports, nports = s.shape
    z0 = fix_z0_shape(z0, nfreqs, nports)
    
    z = npy.zeros(s.shape, dtype='complex')
    I = npy.mat(npy.identity(s.shape[1]))
    s = s.copy() # to prevent the original array from being altered
    s[s==1.] = 1. + 1e-12 # solve numerical singularity
    s[s==-1.] = -1. + 1e-12 # solve numerical singularity
    for fidx in xrange(s.shape[0]):
        sqrtz0 = npy.mat(npy.sqrt(npy.diagflat(z0[fidx])))
        z[fidx] = sqrtz0 * (I-s[fidx])**-1 * (I+s[fidx]) * sqrtz0
    return z

def s2y(s,z0=50):
    '''
    convert scattering parameters [#]_ to admittance parameters [#]_


    .. math::
        y = \\sqrt {y_0} \\cdot (I - s)(I + s)^{-1} \\cdot \\sqrt{y_0}
    
    Parameters
    ------------
    s : complex array-like
        scattering parameters
    z0 : complex array-like or number
        port impedances                                                                                             

    Returns
    ---------
    y : complex array-like 
        admittance parameters

    See Also
    ----------
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    References
    ----------
    .. [#] http://en.wikipedia.org/wiki/S-parameters
    .. [#] http://en.wikipedia.org/wiki/Admittance_parameters
    '''

    nfreqs, nports, nports = s.shape
    z0 = fix_z0_shape(z0, nfreqs, nports)
    y = npy.zeros(s.shape, dtype='complex')
    I = npy.mat(npy.identity(s.shape[1]))
    s = s.copy() # to prevent the original array from being altered
    s[s==-1.] = -1. + 1e-12 # solve numerical singularity
    s[s==1.] = 1. + 1e-12 # solve numerical singularity
    for fidx in xrange(s.shape[0]):
        sqrty0 = npy.mat(npy.sqrt(npy.diagflat(1.0/z0[fidx])))
        y[fidx] = sqrty0*(I-s[fidx])*(I+s[fidx])**-1*sqrty0
    return y

def s2t(s):
    '''
    Converts scattering parameters [#]_ to scattering transfer parameters [#]_ .

    transfer parameters are also refered to as
    'wave cascading matrix', this function only operates on 2-port
    networks.

    Parameters
    -----------
    s : :class:`numpy.ndarray` (shape fx2x2)
        scattering parameter matrix

    Returns
    -------
    t : numpy.ndarray
        scattering transfer parameters (aka wave cascading matrix)

    See Also
    ---------
    inv : calculates inverse s-parameters
    
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    References
    -----------
    .. [#] http://en.wikipedia.org/wiki/S-parameters
    .. [#] http://en.wikipedia.org/wiki/Scattering_transfer_parameters#Scattering_transfer_parameters
    '''
    #TODO: check rank(s) ==2
    
    t = npy.array([
        [-1*(s[:,0,0]*s[:,1,1]- s[:,1,0]*s[:,0,1])/s[:,1,0],
            -s[:,1,1]/s[:,1,0]],
        [s[:,0,0]/s[:,1,0],
            1/s[:,1,0] ]
        ]).transpose()
    return t   

def z2s(z, z0=50):
    '''
    convert impedance parameters [1]_ to scattering parameters [2]_

    .. math::
        s = (\\sqrt{y_0} \\cdot z \\cdot \\sqrt{y_0} - I)(\\sqrt{y_0} \\cdot z \\cdot\\sqrt{y_0} + I)^{-1}

    Parameters
    ------------
    z : complex array-like
        impedance parameters
    z0 : complex array-like or number
        port impedances                                                                                             

    Returns
    ---------
    s : complex array-like
        scattering parameters

    
    
    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/impedance_parameters
    .. [2] http://en.wikipedia.org/wiki/S-parameters
    '''
    nfreqs, nports, nports = z.shape
    z0 = fix_z0_shape(z0, nfreqs, nports)
    s = npy.zeros(z.shape, dtype='complex')
    I = npy.mat(npy.identity(z.shape[1]))
    for fidx in xrange(z.shape[0]):
        sqrty0 = npy.mat(npy.sqrt(npy.diagflat(1.0/z0[fidx])))
        s[fidx] = (sqrty0*z[fidx]*sqrty0 - I) * (sqrty0*z[fidx]*sqrty0 + I)**-1
    return s

def z2y(z):
    '''
    convert impedance parameters [#]_ to admittance parameters [#]_


    .. math::
        y = z^{-1}

    Parameters
    ------------
    z : complex array-like
        impedance parameters

    Returns
    ---------
    y : complex array-like 
        admittance parameters

    See Also
    ----------
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    References
    ----------
    .. [#] http://en.wikipedia.org/wiki/impedance_parameters
    .. [#] http://en.wikipedia.org/wiki/Admittance_parameters
    '''
    return npy.array([npy.mat(z[f,:,:])**-1 for f in xrange(z.shape[0])])
    
def z2t(z):
    '''
    Not Implemented yet
    
    convert impedance parameters [#]_ to scattering transfer parameters [#]_
    

    Parameters
    ------------
    z : complex array-like or number
        impedance parameters

    Returns
    ---------
    s : complex array-like or number
        scattering parameters

    See Also
    ----------
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    
    References
    ----------
    .. [#] http://en.wikipedia.org/wiki/impedance_parameters
    .. [#] http://en.wikipedia.org/wiki/Scattering_transfer_parameters#Scattering_transfer_parameters
    '''
    raise (NotImplementedError)

def y2s(y, z0=50):
    '''
    convert admittance parameters [#]_ to scattering parameters [#]_


    .. math::
        s = (I - \\sqrt{z_0} \\cdot y \\cdot \\sqrt{z_0})(I + \\sqrt{z_0} \\cdot y \\cdot \\sqrt{z_0})^{-1}

    Parameters
    ------------
    y : complex array-like
        admittance parameters

    z0 : complex array-like or number
        port impedances                                                                                             

    Returns
    ---------
    s : complex array-like or number
        scattering parameters

    See Also
    ----------
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    
    References
    ----------
    .. [#] http://en.wikipedia.org/wiki/Admittance_parameters
    .. [#] http://en.wikipedia.org/wiki/S-parameters
    '''
    nfreqs, nports, nports = y.shape
    z0 = fix_z0_shape(z0, nfreqs, nports)
    s = npy.zeros(y.shape, dtype='complex')
    I = npy.mat(npy.identity(s.shape[1]))
    for fidx in xrange(s.shape[0]):
        sqrtz0 = npy.mat(npy.sqrt(npy.diagflat(z0[fidx])))
        s[fidx] = (I - sqrtz0*y[fidx]*sqrtz0) * (I + sqrtz0*y[fidx]*sqrtz0)**-1
    return s

def y2z(y):
    '''
    convert admittance parameters [#]_ to impedance parameters [#]_


    .. math::
        z = y^{-1}

    Parameters
    ------------
    y : complex array-like 
        admittance parameters

    Returns
    ---------
    z : complex array-like
        impedance parameters

    See Also
    ----------
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    References
    ----------
    .. [#] http://en.wikipedia.org/wiki/Admittance_parameters
    .. [#] http://en.wikipedia.org/wiki/impedance_parameters
    '''
    return npy.array([npy.mat(y[f,:,:])**-1 for f in xrange(y.shape[0])])

def y2t(y):
    '''
    Not Implemented Yet 
    
    convert admittance parameters [#]_ to scattering-transfer parameters [#]_


    Parameters
    ------------
    y : complex array-like or number
        impedance parameters

    Returns
    ---------
    t : complex array-like or number
        scattering parameters

    See Also
    ----------
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    References
    ----------
    .. [#] http://en.wikipedia.org/wiki/Admittance_parameters
    .. [#] http://en.wikipedia.org/wiki/Scattering_transfer_parameters#Scattering_transfer_parameters
    '''
    raise (NotImplementedError)

def t2s(t):
    '''
    converts scattering transfer parameters [#]_ to scattering parameters [#]_

    transfer parameters are also refered to as
    'wave cascading matrix', this function only operates on 2-port
    networks. this function only operates on 2-port scattering
    parameters.

    Parameters
    -----------
    t : :class:`numpy.ndarray` (shape fx2x2)
            scattering transfer parameters

    Returns
    -------
    s : :class:`numpy.ndarray`
            scattering parameter matrix.

    See Also
    ---------
    inv : calculates inverse s-parameters
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y    
    Network.s
    Network.y
    Network.z
    Network.t
    
    References
    -----------
    .. [#] http://en.wikipedia.org/wiki/Scattering_transfer_parameters#Scattering_transfer_parameters
    .. [#] http://en.wikipedia.org/wiki/S-parameters
    '''
    #TODO: check rank(s) ==2
    s = npy.array([
        [t[:,0,1]/t[:,1,1],
             1/t[:,1,1]],
        [(t[:,0,0]*t[:,1,1]- t[:,1,0]*t[:,0,1])/t[:,1,1],
            -1*t[:,1,0]/t[:,1,1] ]
        ]).transpose()
    return s

def t2z(t):
    '''
    Not Implemented  Yet 
    
    Convert scattering transfer parameters [#]_ to impedance parameters [#]_



    Parameters
    ------------
    t : complex array-like or number
        impedance parameters

    Returns
    ---------
    z : complex array-like or number
        scattering parameters

    See Also
    ----------
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    References
    ----------
    .. [#] http://en.wikipedia.org/wiki/Scattering_transfer_parameters#Scattering_transfer_parameters
    .. [#] http://en.wikipedia.org/wiki/impedance_parameters
    '''
    raise (NotImplementedError)

def t2y(t):
    '''
    Not Implemented Yet
    
    Convert scattering transfer parameters to admittance parameters [#]_




    Parameters
    ------------
    t : complex array-like or number
        t-parameters

    Returns
    ---------
    y : complex array-like or number
        admittance parameters

    See Also
    ----------
    s2z 
    s2y 
    s2t 
    z2s 
    z2y 
    z2t 
    y2s 
    y2z 
    y2z
    t2s 
    t2z
    t2y
    Network.s
    Network.y
    Network.z
    Network.t
    
    References
    ----------
    .. [#] http://en.wikipedia.org/wiki/Scattering_transfer_parameters#Scattering_transfer_parameters
    
    '''
    raise (NotImplementedError)
