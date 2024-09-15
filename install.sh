python3 -m pip install aiohttp
git clone https://github.com/nccgroup/nOBEX.git
cd nOBEX
#sudo python3 setup.py build
#sudo python3 setup.py install
#sudo -E env PATH=$PATH python3 setup.py build
sudo -E env PATH=$PATH pip install --break-system-packages .
cd ..
git clone https://github.com/thxomas/bdaddr 
cd bdaddr
make
cd ..
