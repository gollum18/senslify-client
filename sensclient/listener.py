import threading, time, sys
import tinyos


# This code comes from the TinyOS oscilloscope application
class OscilloscopeMsg (tinyos.tos.Packet):
    '''
    Defines a message that is read from the official TinyOS oscilloscope
    application.
    '''
    def __init__(self, packet=None):
        tinyos.tos.Packet.__init__(self,
            [('version',  'int', 2),
             ('interval', 'int', 2),
             ('id',       'int', 2),
             ('count',    'int', 2),
             ('readings', 'blob', None)],
            packet)


class Listener(threading.Thread):
    '''
    Defines a class for listening for events on connected serial 
    devices compatible with TinyOS. A single Listener is always 
    bound to a single physical device.
    
    This class functions as state machine that runs as a daemon 
    (background) thread.
    
    The state machine defines the following three states:
        PAUSED: Daemon alive, not reporting data.
        RUNNING: Daemon alive, reporting data.
        STOPPED: Daemon soon to be officially dead.
    In PAUSED mode, the state machine functions effectively as a 
    spin lock. It will not collect data from the connected serial 
    port and will not relay said data through the Listeners callback
    function.
    
    When created, a Listener will always intialize to the PAUSED 
    state. Once stopped, the daemon thread backing the Listener 
    cannot be restarted.
    '''
    
    # Define the states for the state machine
    PAUSED = 0
    RUNNING = 1
    STOPPED = 2
    
    
    # The rate at which the AM module is configured to send 
    #   messages. This is application specific so only
    #   the rate for the Oscilloscope application is defined
    AM_RATES = {
        'OSCIILLOSCOPE': 0x93
    }
    
    
    # Define baudrates for official TinyOS devices
    RATES = {
        'TELOS':        115200,
        'TELOSB':       115200,
        'TMOTE':        115200,
        'MICAZ':        57600,
        'MICA2':        57600,
        'IRIS':         57600,
        'MICA2DOT':     19200,
        'EYES':         115200,
        'INTELMOTE2':   115200
    }
    

    def __init__(self, callback, device, baudrate, amrate='OSCILLOSCOPE'):
        '''
        Returns a new instance of a Listener.
        Arguments:
            callback: The callback to execute when an event is 
            received. The callback function should be thread-safe.
            device: The physical address of the device.
            baudrate: The sampling rate of the physical device.
            amrate: The rate of transfer for the Active Messaging
            module on the connected device.
        '''
        threading.Thread.__init__(self, daemon=True)
        self._callback = threading.local()
        self._callback = callback
        
        self._device = threading.local()
        self._device = device
        
        self._baudrate = threading.local()
        self._baudrate = baudrate
        
        self._amrate = threading.local()
        self._amrate = amrate
        
        self._state = threading.local()
        self._state = Listener.PAUSED
        
        
    #
    # ACCESSOR METHODS
    #
        
    def baudrate(self):
        '''
        Gets the physical sampling rate of the device.
        '''
        return self._baudrate
        
        
    def device(self):
        '''
        Gets the physical address of the device being listened to.
        '''
        return self._device
        
        
    def samplerate(self):
        '''
        Gets the software sampling rate of the device in ms.
        '''
        return self._samplerate
    
    
    def state(self):
        '''
        Gets the state that the Listener is in.
        '''
        return self._state
        
        
    def state_as_str(self):
        if self._state == Listener.RUNNING:
            return 'RUNNING'
        elif self._state == Listener.PAUSED:
            return 'PAUSED'
        elif self._state == Listener.STOPPED:
            return 'STOPPED'
        else:
            return 'NULL'
     
     
    #
    # CONTROL METHODS
    #    
        
    def run(self):
        '''
        Overridden from the Thread superclass. This function defines
        the logic of the Listeners state machine.
        '''
        # Note that the tinyos specific code comes from the 
        #   oscilloscope python application that ships with tos
        am = tinyos.tos.AM()
        
        while self._state != Listener.STOPPED:
            if self._state == Listener.RUNNING:
                # read in the packet
                p = am.read()
                # check if there was a packet and we have an AM rate for it
                if p and p.type == LISTENER.AM_RATES[self._amrate]:
                    msg = OscilloscodeMsg(p.data)
                    callback(msg)
            elif self._state == Listener.PAUSED:
                time.sleep(0)
        
        
    def resume(self):
        '''
        Provides a method for resuming the listener, thereby 
        continuing data collection.
        '''
        if self.is_alive() and self._state != Listener.RUNNING:
            self._state = Listener.RUNNING
     
     
    def pause(self):
        '''
        Provides a method for pausing the Listener, thereby halting
        data collection.
        '''
        if self.is_alive() and self._state == Listener.RUNNING:
            self._state = Listener.PAUSED
     
     
    def stop(self):
        '''
        Provides a method for stopping the Listener, thereby ending 
        the backing daemon thread.
        '''
        if self.is_alive() and self._state != Listener.STOPPED:
            self._state = Listener.STOPPED
