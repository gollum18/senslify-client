import click
from click_shell import shell

import atexit, os, threading

from sensclient.configuration import read_config, write_config
import sensclient.listener as listener


# Used to make the event callback function thread-safe
_event_lock = threading.Lock()

# Stores active device listeners
_listeners = dict()

# Stores the configuration
_config = None
_config_file = None

# Constant for the primary server
PRIMARY = -1

# The currently selected server
_server = PRIMARY


def get_baudrate(baudrate):
    '''
    Attempts to mask the baudrate to a known value.
    
    If masking fails, the method will simply return the passed in
    baudrate as an int.
    Arguments:
        baudrate: A baudrate provided by the user.
    '''
    br = baudrate.upper()
    
    if br in listener.TinyOSListener.RATES:
        return listener.TinyOSListener.RATES[br]
    else:
        return int(br)


def process_event(event):
    '''
    Defines a thread-safe method for handling events from 
    Listeners.
    Arguments:
        event: The event to handle.
    '''
    global _event_lock
    
    _event_lock.acquire()
    click.echo(event)
    _event_lock.release()


@shell(prompt='\nSDCP: ')
def run():
    pass
    
    
#
# DEFINES THE TOP LEVEL COMMAND GROUPS
#
    
    
@run.group()
def config():
    '''
    Defines commands for managing the servers configuration file.
    '''
    pass
    
    
@run.group()
def devices():
    '''
    Defines commands for managing the clients connected devices.
    '''
    pass
    
    
@run.group()
def server():
    '''
    Defines commands for managing the servers in use by the client.
    '''
    pass
    

#
# DEFINES THE CONFIGURATION MANAGEMENT GROUP
#    

@config.command('add-device')
def config_add_device_command():
    pass


@config.command('remove-device')
@click.argument('device')
def config_remove_device(device):
    pass

    
@config.command('add-server')
@click.argument('server')
def config_add_server_command(server):
    pass


@config.command('remove-server')  
@click.argument('server')  
def config_remove_server_command(server):
    pass


@config.command('set-primary-server')
@click.argument('server')
def config_set_primary_server_command(server):
    pass
    
    
@config.command('create')
@click.argument('filename')
def config_create_command(filename):
    pass


@config.command('load')
@click.argument('filename')
def config_load_command(filename):
    pass


#
# DEFINES THE ADD DEVICE GROUP
#

def add_listener(ltype, **kwargs):
    '''
    Adds the listener to the active listeners list.
    Argument:
        ltype: The type of listener to add.
        kwargs: A dictionary containing keyword args passed to the function.
    '''
    global _listeners
    
    if 'device' not in kwargs.keys() or not kwargs['device']:
        click.secho('Unable to create Listener, no device specified!', fg='red', err=True)
        pass
    device = kwargs['device']
    if device not in _listeners:
        cl = None
        # Try to create the listener, fail soft if theres an error
        try:
            cl = listener.create_listener(ltype=ltype, **kwargs)
        except KeyError as e:
            click.secho('Unable to add listener for device {}, invalid argument supplied!'.format(device), fg='red', err=True)
        except ValueError as e:
            click.secho('Unable to add listener for device {}, invalid argument supplied!'.format(device), fg='red', err=True)
        # Make sure the listener was created, fail soft otherwise
        if cl is None:
            click.secho('Unable to add listener for device {}, there was an error creating the listener.'.format(device), fg='red', err=True)
        else:
            _listeners[device] = cl
            click.secho('Successfully added listener for device {}.'.format(device), fg='green')
    else:
        click.secho('Unable to add listener for device {}, listener already exists for device!'.format(device), fg='red', err=True)
    
    
@devices.group('add')
def devices_add():
    '''
    Adds a device for event listening.
    '''
    pass
    

@devices_add.command('dummy')
@click.argument('device')
def devices_add_dummy_command(device):
    '''
    [DEVICE] Adds a dummy device.
    Arguments:
        device: The device mount/end point.
    '''
    add_listener(listener.T_DUMMY, callback=process_event, device=device)


@devices_add.command('serial')
@click.argument('device')
@click.argument('baudrate')
def devices_add_serial_command(device, baudrate):
    '''
    [DEVICE BAUDRATE] Adds a serial device.
    Arguments:
        device: The device mount/end point.
        baudrate: The baudrate of the serial device.
    '''
    add_listener(listener.T_SERIAL, callback=process_event, device=device, baudrate=baudrate)


@devices_add.command('tos')
@click.argument('device')
@click.argument('baudrate')
@click.argument('amrate')
def devices_add_tos_command(device, baudrate, amrate):
    '''
    [DEVICE BAUDRATE AMRATE] Adds a TinyOS device.
    Arguments:
        device: The device mount/end point.
        baudrate: The baudrate of the serial device.
        amrate: The Active Messaging rate of the TinyOS application installed
        on the device.
    '''
    add_listener(listener.T_TINYOS, callback=process_event, device=device, baudrate=baudrate, amrate=amrate)


@devices_add.command('btooth')
@click.argument('device')
def devices_add_btooth_command(device):
    '''
    [DEVICE] Adds a bluetooth device.
    Arguments:
        device: The device mount/end point.
    '''
    add_listener(listener.T_BLUETOOTH, callback=process_event, device=device)


#
# DEFINES THE LISTENER CONTROL GROUP
#

@devices.command('pause')
@click.argument('device')
def devices_pause_command(device):
    '''
    Pauses listening to a device.
    Arguments:
        device: The physical address of the device to pause listening
        on.
    '''
    global _listeners
    
    if device in _listeners:
        if _listeners[device] == listener._Listener.RUNNING:
            click.echo('Pausing Listener for device {}...'.format(device))
            _listeners[device].pause()
    else:
        click.secho('Cannot pause Listener for device {}, no Listener registered for device!'.format(device), fg='red', err=True)


@devices.command('resume')
@click.argument('device')
def devices_resume_command(device):
    '''
    Resumes listening on a device.
    Arguments:
        device: The physical address of the device to resume
        listening on.
    '''
    global _listeners
    
    if device in _listeners:
        if _listeners[device].state() == listener._Listener.PAUSED:
            click.echo('Resuming Listener for device {}...'.format(device))
            _listeners[device].resume()
        else:
            click.secho('Cannot resume Listener for device {}, Listener already running!'.format(device), fg='red', err=True)
    else:
        click.secho('Cannot resume Listener for device {}, no Listener registered for device!'.format(device), fg='red', err=True)
        

#
# DEFINES THE SHOW DEVICE GROUP
#

@devices.group('show')
def show_devices():
    '''
    Shows devices that with connected listeners.
    '''
    pass
    
    
@show_devices.command('dummy')
def show_devices_dummy_command():
    '''
    Shows connected dummy devices.
    '''
    pass


@show_devices.command('serial')
def show_devices_serial_command():
    '''
    Shows connected serial devices.
    '''
    pass


@show_devices.command('tos')
def show_devices_tos_command():
    '''
    Shows connected TinyOS devices.
    '''
    pass


@show_devices.command('btooth')
def show_devices_btooth_command():
    '''
    Shows connected bluetooth devices.
    '''
    pass


@devices.command('stop')
@click.argument('device')
def devices_stop_command(device):
    '''
    Stops listening on a device.
    Arguments:
        device: The physical address of the device to stop listening
        on.
    '''
    global _listeners
    
    if device in _listeners:
        click.echo('Stopping listener for device {}...'.format(device))
        _listeners[device].stop()
        del _listeners[device]
    else:
        click.secho('Cannot stop Listener for device {}, no Listener registered!'.format(device), fg='red', err=True)


#
# DEFINE SET COMMANDS
#


@server.command('set')
@click.argument('num')
def server_set_command(num):
    global _config

    if (num == -1 or 
            (0 <= num < len(_config['servers']['secondary']))):
        click.echo('Setting server to server number: {}...'.format(num))
    else:
        click.echo('Cannot set server, {} is not a valid server number!'.format(num))


@server.command('show')
def server_show_handler():
    global _config
    
    click.echo('Displaying all configured servers...')
    if _server == PRIMARY:
        click.echo('* (-1) {}'.format(_config['servers']['primary']))
    else:
        click.echo('(-1) {}'.format(_config['servers']['primary']))
        
    for i in range(len(_config['servers']['secondary'])):
        if i != _server:
            click.echo('({}) {}'.format(i, _config['servers']['secondary'][i]))
        else:
            click.echo('* ({}) {}'.format(i, _config['servers']['secondary'][i]))


#
# DEFINE MISC COMMANDS
#


@run.command('clear')
def clear_command():
    '''
    Clears the terminal output.
    '''
    click.clear()


#
# CLIENT FUNCTIONS
#


def cleanup():
    '''
    Defines a function for cleaning up the clients environment prior 
    to shutdown.
    '''
    global _listeners
    
    for _, listener in _listeners.items():
        listener.stop()


def init():
    '''
    Defines the entry point of the client.
    '''
    global _config
    global _listeners
    
    # load in the configuration file
    _config = read_config()
    # TODO: Add in default devices
    # register the cleanup function
    atexit.register(cleanup)
    
    # start the shell
    run()
    

# explicitly declare the entry point in case anyone runs the client
#   directly.
if __name__ == '__main__':
    init()
