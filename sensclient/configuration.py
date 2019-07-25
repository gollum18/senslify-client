# Package: senslify-client
# Name: configuration.py
# Since: July 24th, 2019
# Author: Christen Ford <c.t.ford@vikes.csuohio.edu>
# Description: Defines methods for managing the Senslify client's configuration 
#   file.


import os
import click
import simplejson


# The default path and name for the configration file
DEFAULT_CONFIG_PATH = os.path.dirname(os.path.abspath(__file__)) + '/sensclient.json'


def _prompt_servers():
    '''
    Configuration generation step that setups up the primary server and any
    additional servers.
    '''
    click.echo('\nWe are now going to ask you for a primary Senslify server as well as any additional secondary servers.')
    click.echo('You may select from these servers at any time from with the client using the \'servers\' command.')
    servers = dict()
    servers['primary'] = click.prompt('Enter the primary senslify server', type=str)
    secondary = []
    if click.confirm('\nDo you want to enter any additional servers?'):
        while True:
            server = click.prompt('Enter the server')
            secondary.append(server)
            if click.confirm('Do you want to enter any additional servers?'):
                break
    servers['secondary'] = secondary
    # return the servers
    return servers
        
        
def _prompt_devices():
    '''
    Configuration generation step that setsup any default devices.
    '''
    click.echo('\nWe are now going to ask if you want to add any default devices.')
    click.echo('A Listener will automatically be created for these devices when you start the client.')
    devices = []
    if click.confirm('Do you want to add any default devices?'):
        while True:
            device_raw = click.prompt('Enter input in the form \'DEVICE BAUDRATE AMRATE\':')
            parts = device_raw.split(' ')
            devices.add({'device': parts[0], 'baudrate': parts[1], 'amrate': parts[2]})
            if not click.confirm('\nDo you want to add any additional devices?'):
                break
    return devices
    

def _prompt_config():
    '''
    Manages configration creation.
    '''
    # stores the configuration for the next step
    config = dict()
    # print the header
    click.echo('-'*80)
    click.echo('No configuration file found...')
    click.echo('You will be asked a few questions to generate an initial configration file.')
    click.echo('-'*80)
    # Setup servers
    config['servers'] = _prompt_servers()
    # Ask whether the user wants to add any default devices
    config['devices'] = _prompt_devices()
    # return the raw configuration
    return config


def read_config(filename=DEFAULT_CONFIG_PATH):
    '''
    Reads the configuration file.
    Arguments:
        filename: The path and filename of the configuration file.
    '''
    config = None
    if not os.path.isfile(filename):
        config = _prompt_config()
        write_config(config, filename)
    else:
        try:
            with open(filename, 'r') as fp:
                config = simplejson.load(fp)
        except OSError:
            pass
    if not config:
        return prompt_config()
    return config


def write_config(config, filename=DEFAULT_CONFIG_PATH):
    '''
    Writes the configuration to file.
    Arguments:
        config: The raw configuration, usually a Python dict.
        filename: The path + filename to write the configuration to.
    '''
    if os.path.isfile(filename):
        if not click.prompt('Are you sure you want to overwrite the configuration file?'):
            return
    try:
        with open(filename, 'w') as fp:
            fp.write(simplejson.dumps(config, fp))
    except OSError:
        click.secho('There was an error writing the configuration file.\nConfiguration file not written.', fg='red')
