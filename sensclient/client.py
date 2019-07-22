'''
Defines a client for the Senslify web application.
'''
import aiohttp
import click, click_shell as shell

from listener import Listener


# The server client - An aiohttp.ClientSession
_session = aiohttp.ClientSession()
# Maps devices to listeners
_devices = dict()


async def process_event(event, host):
    '''
    Defines a callback for processing events received from a listener.
    Arguments:
        event: The event to process.
        host: The hostname of the Senslify server to send proccessed event data to.
    '''
    global _session

    # upload the received data to the specified host
    # url = host + 'sensors/upload'

    # DEBUG
    click.echo(event)


@shell.command('pause')
@click.command('device')
def pause_command(device):
    '''
    Pauses listening on a device.
    Arguments:
        device: The device to pause listening on.
    '''
    global _devices

    if device in _devices:
        if _devices[device].state() == Listener.ACTIVE:
            _devices[device].pause()
        else:
            click.echo('Unable to pause Listener on device {}, Listener already paused or stopped!'.format(device))
    else:
        click.echo('Unable to pause listening on device {}, no Listener registered for device!')


@shell.command('resume')
@click.command('device')
def resume_command(device):
    '''
    Resumes listening on a device.
    Arguments:
        device: The device to resume listening on.
    '''
    global _devices

    if device in _devices:
        if _device[device].state() == Listener.PAUSED:
            _device[device].resume()
        else:
            click.echo('Unable to resume listening on device {}, Listener is already running or stopped!'.format(device))
    else:
        click.echo('Unable to resume listening on device {}, no Listener registered for device!'.format(device))


@shell.command('remove')
@click.argument('device')
def remove_command(device):
    '''
    Removes the listener for a connected device.
    Arguments:
        device: The device to remove the listener from.
    '''
    global _devices

    if device in _devices:
        if _devices[device].state != Listener.STOPPED:
            _devices[device].stop()
        del _devices[device]
    else:
        click.echo('Unable to remove device {}, no Listener registered for device!'.format(device))


@shell.command('add')
@click.argument('device')
@click.argument('baudrate')
@click.argument('samplerate')
def add_command(device, baudrate, samplerate):
    '''
    Adds an event listener on the indicated device.
    Arguments:
        device: The device to listen on.
        baudrate: The baudrate of the target device.
        samplerate: The rate to sample the device at.
    '''
    global _devices

    if device not in _devices:
        devices[device] = listener.Listener(
            process_event,  # The callback to run when an event is generated
            device,         # The endpoint for the device
            baudrate,       # The actual sampling rate of the device
            samplerate      # The rate at whcih samples are drawn (ms)
        )
    else:
        click.echo('Unable to start Listener for {}, Listener already active!'.format(device))


@shell.command('show')
def show_command():
    '''
    Shows devices being listened to.
    '''
    global _devices

    for device, _ in _devices.items():
        click.echo(device)


@shell(prompt('SDCP> '))
def run():
    '''
    Starts the interactive shell for the Senslify Data Control Protocol.

    Do not modify this function.
    '''
    pass


