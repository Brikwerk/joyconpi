#Stop the background process
sudo /etc/init.d/bluetooth stop
# Turn on Bluetooth
sudo hciconfig hcio up

#Get current Path
export C_PATH=$(pwd)
#Create Tmux session
tmux has-session -t  joyconpi
if [ $? != 0 ]; then
    tmux new-session -s joyconpi -n os -d
    tmux split-window -h -t joyconpi
    tmux split-window -v -t joyconpi:os.0
    tmux split-window -v -t joyconpi:os.1
    tmux send-keys -t joyconpi:os.0 'cd $C_PATH && sudo /usr/sbin/bluetoothd --nodetach --debug -p time ' C-m
    tmux send-keys -t joyconpi:os.1 'sudo ./venv/bin/python testserver.py' C-m
    tmux send-keys -t joyconpi:os.2 'cd $C_PATH && sudo /usr/bin/bluetoothctl' C-m
fi