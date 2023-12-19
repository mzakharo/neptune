sudo cp neptune.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable neptune.service
sudo systemctl restart neptune.service
sudo systemctl status neptune.service
