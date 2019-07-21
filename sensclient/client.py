'''
Defines a client for the Senslify web application.
'''
import aiohttp
import click, click_shell as shell

from listener import listen


# The server client - An aiohttp.ClientSession
_session = aiohttp.ClientSession()
# Maps devices to listeners
_devices = dict()


def process_event(event, host):
    '''
    Defines a callback for processing events received from a listener.
    Arguments:
        event: The event to process.
        host: The hostname of the Senslify server to send proccessed event data to.
    '''
    global _session

    # upload the received data to the specified host
    url = host + 'sensors/upload'


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

    else:
        click.echo('')


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

    else:
        click.echo('')


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

    else:
        click.echo('')


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

    else:
        click.echo('Unable to start listener for {}, listener already active!'.format(device))


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


