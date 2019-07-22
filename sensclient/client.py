import config

import click
from click_shell import shell

import atexit, os, threading

from sensclient.listener import Listener


# Used to make the event callback function thread-safe
_event_lock = threading.Lock()

# Stores active device listeners
_listeners = dict()

# Stores the configuration
_config = None

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
    
    if br in Listener.RATES:
        return Listener.RATES[br]
    else:
        return int(br)


def load_config(filename=os.path.dirname(os.path.abspath(__file__)) + '/sensclient.conf'):
    '''
    Loads the configuration file.
    '''
    return config.Config(filename)


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
    
    
@run.group()
def devices():
    pass
    
    
@run.group()
def server():
    pass


@devices.command('add')
@click.argument('device')
@click.argument('baudrate')
@click.argument('samplerate')
def devices_add_command(device, baudrate, samplerate):
    '''
    Adds a device and starts listening on it.
    Arguments:
        device: The physical address of the device to start listening
        on.
    '''
    global _listeners
    
    if device not in _listeners:
        try:
            _listeners[device] = Listener(
                process_event, 
                device, 
                get_baudrate(baudrate), 
                int(samplerate)
            )
            _listeners[device].start()
        except RuntimeError as e:
            click.secho(e, fg='red', err=True)
        except ValueError:
            click.secho('Cannot add listener for device {}, invalid baudrate or sample rate entered!'.format(device), fg='red', err=True)
    else:
        click.secho('Cannot start Listener for device {}, there is already an active Listener for the device!'.format(device), fg='red', err=True)


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
        click.echo('{:>15} {:>15} {:>15} {:>10}'.format('DEVICE', 'BAUDRATE', 'SAMPLERATE', 'STATE'))
        click.echo('-'*80)
        # for some reason this is giving an error?
        for _, listener in _listeners.items():
            click.echo('{:>15} {:>15} {:>15} {:>10}'.format(
                listener.device(), 
                listener.baudrate(), 
                listener.samplerate(), 
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


@server.command('set')
@click.argument('num')
def server_set_handler(num):
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


@run.command('cls')
def clear_command():
    '''
    Clears the terminal output.
    '''
    click.clear()


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
    _config = load_config()
    # TODO: This needs refactored so it calls the device add 
    #   command directly
    try:
        for device in _config['devices']:
            _listeners[device] = Listener(
                process_event, 
                device.device, 
                get_baudrate(device.baudrate), 
                int(device.samplerate)
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
