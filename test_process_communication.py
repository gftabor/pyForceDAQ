import random
from time import sleep
from multiprocessing import Queue, Process, Event, sharedctypes, Pipe
import pickle
import timeit
import ctypes as ct
import numpy as np
from sys import getsizeof

CTYPE_FORCES = ct.c_float * 600
CTYPE_TRIGGER = ct.c_float * 2

class CTypesForceData(ct.Structure):
    _fields_ = [("device_id", ct.c_int),
            ("time", ct.c_int),
            ("counter", ct.c_uint64),
            ("forces", CTYPE_FORCES),
            ("trigger", CTYPE_TRIGGER)]


class ForceData(object):
    """The Force data structure with the following properties
        * device_id
        * Fx,  Fy, & Fz
        * Tx, Ty, & Tz
        * trigger1 & trigger2
        * time
        * counter

    """

    variable_names = "device_id, time, counter, Fx, Fy, Fz, Tx, Ty, Tz, " + \
                     "trigger1, trigger2"

    def __init__(self, time=None, counter=0, forces=[0] * 6, trigger=(0, 0),
                 device_id=0):
        """Create a ForceData object
        Parameters
        ----------
        device_id: int, optional
            the id of the sensor device
        time: int, optional
            the timestamp
        counter: int
            sample counter; useful, for instance, if multiple samples are
            received within one millisecond
        forces: array of six floats
            array of the force data defined as [Fx, Fy, Fz, Tx, Ty, Tz]
        trigger: array of two floats
            two trigger values: [trigger1, trigger2]

        """

        self.time = time
        self.device_id = device_id
        self.counter = counter
        self.forces = forces
        self.trigger = trigger

    def __str__(self):
        """converts data to string. """
        txt = "%d,%d,%d, %.8f,%.8f,%.8f,%.8f,%.8f,%.8f" % (self.device_id,
                                                           self.time,
                                                           self.counter,
                                                           self.forces[0],
                                                           self.forces[1],
                                                           self.forces[2],
                                                           self.forces[3],
                                                           self.forces[4],
                                                           self.forces[5])
        txt += ",%.4f,%.4f" % (self.trigger[0], self.trigger[1])
        return txt

    @property
    def Fx(self):
        return self.forces[0]

    @Fx.setter
    def Fx(self, value):
        self.forces[0] = value

    @property
    def Fy(self):
        return self.forces[1]

    @Fy.setter
    def Fy(self, value):
        self.forces[1] = value

    @property
    def Fz(self):
        return self.forces[2]

    @Fz.setter
    def Fz(self, value):
        self.forces[2] = value

    @property
    def Tx(self):
        return self.forces[3]

    @Tx.setter
    def Tx(self, value):
        self.forces[3] = value

    @property
    def Ty(self):
        return self.forces[4]

    @Ty.setter
    def Ty(self, value):
        self.forces[4] = value

    @property
    def Tz(self):
        return self.forces[3]

    @Tz.setter
    def Tz(self, value):
        self.forces[3] = value

    @property
    def ctypes_struct(self):
        return CTypesForceData(self.device_id, self.time, self.counter,
              CTYPE_FORCES(*self.forces), CTYPE_TRIGGER(*self.trigger))

    @ctypes_struct.setter
    def ctypes_struct(self, struct):
        self.device_id = struct.device_id
        self.time = struct.time
        self.counter = struct.counter
        self.force = struct.forces
        self.trigger = struct.triger

    @property
    def array(self):
        rtn = [self.device_id, self.time ,
        self.counter, self.forces, self.trigger]
        return rtn


class SensorTest(Process):

    def __init__(self, chunk_size=10000):
        super(SensorTest, self).__init__()
        self._pipe_i, self._pipe_o = Pipe()
        self._buffer_size = sharedctypes.RawValue(ct.c_uint64)
        self.event_sending_data = Event()
        self.event_reading_data = Event()
        self.chunk_size = chunk_size


    def read_buffer(self):
        data = []
        if self._buffer_size.value > 0:
            self.event_sending_data.wait()
            while self._buffer_size.value > 0:
                data.extend(self._pipe_i.recv())
            self.event_sending_data.clear()
        return data

    def stop(self):
        rtn = self.read_buffer()
        self.join()
        return rtn


    def run(self):

        self.event_sending_data.clear()
        data = []
        self._buffer_size.value = 0
        for cnt in xrange(1000*60*1):
            d = ForceData(time=8, counter=cnt,
                  forces=np.random.random(6),
                  trigger=(99,cnt+100))
            data.append(d)
            self._buffer_size.value = len(data)

        print data[2345].forces
        # sending data
        self.event_sending_data.set()
        chks = self.chunk_size
        while len(data)>0:
            if chks > len(data):
                chks = len(data)
            self._pipe_o.send(data[0:chks])
            data[0:chks] = []
            self._buffer_size.value = len(data)
        # wait that data read
        if self.event_sending_data.is_set():
            sleep(0.01)


def MB(x):
    return getsizeof(x)/(1024.0*2)

if __name__=="__main__":
    sensor = SensorTest()

    sensor.start()

    print "reading"
    tic = timeit.default_timer()
    b = []
    while len(b)==0:
        b = sensor.read_buffer()

    sensor.stop()
    bb = []
    for x in b:
        bb.append(x.ctypes_struct)
    import pickle
    import cPickle
    print MB(b)

    tic = timeit.default_timer()
    print MB(cPickle.dumps(b))
    print timeit.default_timer() -tic

    tic = timeit.default_timer()
    print MB(pickle.dumps(b))
    print timeit.default_timer() -tic
