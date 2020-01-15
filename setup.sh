# Constants
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

printf "\n${RED}Installing System Requirements and Bluetooth Requirements...${NC}\n\n"
# Bluetooth + Sys Reqs
sudo apt install libbluetooth-dev bluez bluez-tools bluez-firmware libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0 -y

printf "\n${RED}Changing Bluetooth Address...${NC}\n\n"
# Bluetooth Mac Address change software
# Saving old bluetooth address
hciconfig hcio | awk '/BD Address: /{print $3}' > original_bt_mac.txt
# Installing and using bt address changer
# cd tools
# tar xf bdaddrtar
# cd bdaddr && make
# # Changing address
# sudo ./bdaddr -i hci0 -r 98:B6:E9:35:D7:37
# sudo hciconfig hci0 reset
# sudo systemctl restart bluetooth.service
# cd ../../

printf "\n${RED}Installing Python Requirements...${NC}\n\n"
# Python Reqs
# In case of bdist_wheel failure
pip install wheel
pip install -r requirements.txt
