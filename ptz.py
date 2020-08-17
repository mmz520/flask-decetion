from onvif import ONVIFCamera
import zeep

def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue

def move(ip,port,account,pwd,pan,pan_speed,tilt,tilt_speed,zoom,zoom_speed):
    mycam=ONVIFCamera(ip,port,account,pwd)
    media = mycam.create_media_service()
    # Create ptz service object
    ptz = mycam.create_ptz_service()

    # Get target profile
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
    media_profile = media.GetProfiles()[0]

    m_request = ptz.create_type('AbsoluteMove')
    m_request.ProfileToken = media_profile.token
    ptz.Stop({'ProfileToken': media_profile.token})

    if m_request.Position is None:
        m_request.Position = ptz.GetStatus({'ProfileToken': media_profile.token}).Position
    if m_request.Speed is None:
        m_request.Speed = ptz.GetStatus({'ProfileToken': media_profile.token}).Position

    m_request.Position.PanTilt.x = pan
    m_request.Speed.PanTilt.x = pan_speed

    m_request.Position.PanTilt.y = tilt
    m_request.Speed.PanTilt.y = tilt_speed

    m_request.Position.Zoom = zoom
    m_request.Speed.Zoom = zoom_speed

    ptz.AbsoluteMove(m_request)