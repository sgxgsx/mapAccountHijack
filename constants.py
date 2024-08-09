




EXAMPLE_MESSAGE = b"BEGIN:BMSG\r\nVERSION:1.0\r\nSTATUS:READ\r\nTYPE:MMS\r\nFOLDER:null\r\nBEGIN:BENV\r\nBEGIN:VCARD\r\nVERSION:2.1\r\nN:null;;;;\r\nTEL:+1234567890\r\nEND:VCARD\r\nBEGIN:BBODY\r\nCHARSET:UTF-8\r\nENCODING:8bit\r\nLENGTH:40\r\nBEGIN:MSG\r\nThis is a new msg!\r\nEND:MSG\r\nEND:BBODY\r\nEND:BENV\r\nEND:BMSG\r\n"


def get_SMS_MESSAGE_BEGIN():
    return b"BEGIN:BMSG\r\nVERSION:1.0\r\nSTATUS:READ\r\nTYPE:MMS\r\nFOLDER:null\r\nBEGIN:BENV\r\nBEGIN:VCARD\r\nVERSION:2.1\r\nN:null;;;;\r\nTEL:"


def get_SMS_MESSAGE_END():
    return b"\r\nEND:VCARD\r\n"  + b"BEGIN:BBODY\r\nCHARSET:UTF-8\r\nENCODING:8bit\r\nLENGTH:40\r\nBEGIN:MSG\r\nThis is a new msg!\r\nEND:MSG\r\n" + b"END:BBODY\r\nEND:BENV\r\nEND:BMSG\r\n"
    
    