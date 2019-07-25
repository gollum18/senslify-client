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
# DEFINE CLIENT COMMAND GROUPS
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
# DEFINE CONFIGURATION MANAGEMENT COMMANDS
#    


@config.command('add-device')
@click.argument('device')
@click.argument('baudrate')
@click.argument('amrate')
def config_add_server_command(device, baudrate, amrate):
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
# DEFINE DEVICE COMMANDS
#


def add_listener(device, listener):
    '''
    Adds the listener to the active listeners list.
    Argument:
        device: The device corresponding to the listener.
        listener: The listener corresponding to the device.
    '''
    global _listeners
    
    if device not in _listeners:
        _listeners[device] = listener
        click.secho('Successfully added listener for device {}.'.format(device))
    else:
        click.secho('Unable to add listener for device {}, listener already exists for device!'.format(device), fg='red', err=True)

    
# TODO: Implement the add device commands for the various device types


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
        if _listeners[device] == Listener.RUNNING:
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
        if _listeners[device].state() == Listener.PAUSED:
            click.echo('Resuming Listener for device {}...'.format(device))
            _listeners[device].resume()
        else:
            click.secho('Cannot resume Listener for device {}, Listener already running!'.format(device), fg='red', err=True)
    else:
        click.secho('Cannot resume Listener for device {}, no Listener registered for device!'.format(device), fg='red', err=True)
        
        
@devices.command('show')
def devices_show_command():
    global _listeners
    
    if len(_listeners) > 0:
        click.echo('-'*80)
        click.echo('{:>15} {:>15} {:>15} {:>10}'.format('DEVICE', 'BAUDRATE', 'AMRATE', 'STATE'))
        click.echo('-'*80)
        # for some reason this is giving an error?
        for _, listener in _listeners.items():
            click.echo('{:>15} {:>15} {:>15} {:>10}'.format(
                listener.device(), 
                listener.baudrate(), 
                listener.amrate(), 
                listener.state_as_str()
                )
            )
    else:
        click.secho('Cannot show Listener status for connected devices, no devices registered!', fg='red', err=True)


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


@run.command('cls')
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
    # TODO: This needs refactored so it calls the device add 
    #   command directly
    try:
        for device in _config['devices']:
            _listeners[device] = Listener(
                process_event, 
                device.device, 
                get_baudrate(device.baudrate), 
                int(device.amrate)
            )
            _listeners[device].start()
    except RuntimeError as e:
        click.secho(e, fg='red', err=True)
    except ValueError:
        click.secho('Cannot add listener for device {}, invalid baudrate or sample rate entered!'.format(device), fg='red', err=True)
    # register the cleanup function
    atexit.register(cleanup)
    
    # start the shell
    run()
    

# explicitly declare the entry point in case anyone runs the client
#   directly.
if __name__ == '__main__':
    init()
