import click
from click_shell import shell

import atexit, threading

from sensclient.listener import Listener


_event_lock = threading.Lock()


def get_baudrate(baudrate):
    br = baudrate.upper()
    
    if br in Listener.RATES:
        return Listener.RATES[br]
    else:
        return eval(br)


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


@shell(prompt='Command: ')
def run():
    pass
    
    
@run.group()
def devices():
    pass


# Stores active device listeners
_listeners = dict()
    

@devices.command('add')
@click.argument('device')
@click.argument('baudrate')
@click.argument('samplerate')
def add_command(device, baudrate, samplerate):
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
                eval(samplerate)
            )
            _listeners[device].start()
        except RuntimeError as e:
            click.echo(e)
    else:
        click.echo('Cannot start Listener for device {}, there is already an active Listener for the device!'.format(device))


@devices.command('pause')
@click.argument('device')
def pause_command(device):
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
        click.echo('Cannot pause Listener for device {}, no Listener registered for device!'.format(device))


@devices.command('resume')
@click.argument('device')
def resume_command(device):
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
            click.echo('Cannot resume Listener for device {}, Listener already running!'.format(device))
    else:
        click.echo('Cannot resume Listener for device {}, no Listener registered for device!'.format(device))
        
        
@devices.command('show')
def show_command():
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
        click.echo('Cannot show Listener status for connected devices, no devices registered!')


@devices.command('stop')
@click.argument('device')
def stop_command(device):
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
        click.echo('Cannot stop Listener for device {}, no Listener registered!'.format(device))
        

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
    atexit.register(cleanup)
    run()
    

# explicitly declare the entry point in case anyone runs the client
#   directly.
if __name__ == '__main__':
    init()
