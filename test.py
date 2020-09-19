from time import sleep
import zeep
from onvif import ONVIFCamera

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1
def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue
def perform_move(ptz, request, timeout):
    # Start continuous move
    ptz.ContinuousMove(request)
    # Wait a certain time
    sleep(timeout)
    # Stop continuous move
    ptz.Stop({'ProfileToken': request.ProfileToken})

def move_up(ptz, request, timeout=1):
    #print 'move up...'
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)

def move_down(ptz, request, timeout=1):
    #print 'move down...'
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)

def move_right(ptz, request, timeout=1):
    #print 'move right...'
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def move_left(ptz, request, timeout=1):
    #print 'move left...'
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def continuous_move(direction,ip,port,account,password):
    mycam = ONVIFCamera(ip, port, account, password)
    # Create media service object
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    # Get target profile
    media_profile = media.GetProfiles()[0]

    # Get PTZ configuration options for getting continuous move range
    request = ptz.create_type('GetConfigurationOptions')
    request.ConfigurationToken = media_profile.PTZConfiguration.token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = media_profile.token
    if(request.Velocity is None):
        request.Velocity=ptz.GetConfigurations()[0].DefaultPTZSpeed
    #request.Velocity.PanTilt.space=None
    #request.Velocity.Zoom.space=None
    ptz.Stop({'ProfileToken': media_profile.token})

    if(direction=='right'):
        request.Velocity.PanTilt.x = 1
        request.Velocity.PanTilt.y = 0
        request.Velocity.Zoom.x=0
        request.Timeout=1
        ptz.ContinuousMove(request)
        sleep(0.1)
        ptz.Stop({'ProfileToken': request.ProfileToken})
    if(direction=='left'):
        request.Velocity.PanTilt.x = -1
        request.Velocity.PanTilt.y = 0
        request.Velocity.Zoom.x=0
        request.Timeout=1
        ptz.ContinuousMove(request)
        sleep(0.1)
        ptz.Stop({'ProfileToken': request.ProfileToken})
    if(direction=='up'):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = -1
        request.Velocity.Zoom.x=0
        request.Timeout=1
        ptz.ContinuousMove(request)
        sleep(0.1)
        ptz.Stop({'ProfileToken': request.ProfileToken})
    if(direction=='down'):
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = 1
        request.Velocity.Zoom.x=0
        request.Timeout=1
        ptz.ContinuousMove(request)
        sleep(0.1)
        ptz.Stop({'ProfileToken': request.ProfileToken})

if __name__ == '__main__':
    continuous_move()
